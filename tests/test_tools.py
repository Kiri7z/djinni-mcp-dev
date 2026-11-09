"""Behavior checks using synthetic data; default tests make no network requests."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from xml.sax.saxutils import escape

import httpx
from mcp import Client, StdioServerParameters

from djinni_mcp.server import create_server
from djinni_mcp.source import MAX_BYTES, DjinniSource, SourceError
from djinni_mcp.state import LocalStore

TOOLS = {'search_jobs', 'get_job', 'get_workflow', 'get_profile', 'update_profile',
         'get_history', 'set_job_excluded', 'save_search'}


def feed(entries):
    return '<rss><channel>' + ''.join(
        f'<item><title>{escape(title)}</title><link>{escape(url)}</link>'
        '<category>Sysadmin</category><pubDate>raw source date</pubDate></item>'
        for title, url in entries
    ) + '</channel></rss>'


def job_page(*, activity="open", metadata=True, description="Example description", extra=None):
    data = {"@type": "JobPosting", "url": "https://djinni.co/jobs/123-example/",
            "title": "Example role", "hiringOrganization": {"name": "Example Company"},
            "datePosted": "2026-11-03T10:00:00", "validThrough": "2026-12-03T10:00:00"}
    data.update(extra or {})
    marker = '<button>Apply for the job</button>' if activity == "open" else (
        '<div>The job ad is no longer active</div>' if activity == "closed" else '')
    script = f'<script type="application/ld+json">{json.dumps(data)}</script>' if metadata else ''
    return (f'<html><h1>Example role</h1>{script}'
            f'<div class="job-post__description">{description}</div>{marker}'
            '<span>Published 16 July</span><div>Updated 3 November</div></html>')


class SourceTests(unittest.IsolatedAsyncioTestCase):
    def source(self, handler):
        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        self.addAsyncCleanup(client.aclose)
        return DjinniSource(client)

    async def test_search_native_filters_literal_filter_and_stable_identity(self):
        calls = []
        def handler(request):
            calls.append(request)
            return httpx.Response(200, headers={"content-type": "application/rss+xml"}, text=feed([
                ('[Ops] Linux', 'https://djinni.co/jobs/123-old-slug/?tracking=example'),
                ('[Ops] renamed', 'https://djinni.co/jobs/123-new-slug/'),
                ('Other role', 'https://djinni.co/jobs/456-other/'),
                ('[Ops] Windows', 'https://djinni.co/jobs/789-windows/'),
            ]))
        result = await self.source(handler).search_jobs(
            category="Sysadmin", title_contains="[OPS]", remote_only=True,
            company_type="product", limit=1,
        )
        self.assertEqual(dict(calls[0].url.params), {
            "primary_keyword": "Sysadmin", "employment": "remote", "company_type": "product"})
        self.assertEqual((result.fetched_count, result.matched_count, result.next_offset), (4, 2, 1))
        self.assertEqual(result.jobs[0].id, "123")
        self.assertNotIn('?', result.jobs[0].url)
        self.assertEqual(result.jobs[0].activity, "unknown")
        self.assertIsNone(result.jobs[0].activity_checked_at)
        self.assertEqual(result.jobs[0].source_pub_date, "raw source date")
        self.assertEqual(result.coverage, "unknown")
        page = await self.source(handler).search_jobs(title_contains="[OPS]", offset=1, limit=1)
        self.assertEqual(page.jobs[0].id, "789")
        self.assertIsNone(page.next_offset)

    async def test_valid_empty_is_distinct_from_invalid_feed(self):
        empty = self.source(lambda r: httpx.Response(200, headers={"content-type":"text/xml"}, text=feed([])))
        self.assertEqual((await empty.search_jobs()).returned_count, 0)
        for body in ['<html>Blocked</html>', '<rss>broken', '<notrss><channel/></notrss>']:
            source = self.source(lambda r, b=body: httpx.Response(200, headers={"content-type":"text/xml"}, text=b))
            with self.assertRaisesRegex(SourceError, 'invalid_response'):
                await source.search_jobs()

    async def test_partial_invalid_items_are_explicit(self):
        source = self.source(lambda r: httpx.Response(200, headers={"content-type":"text/xml"}, text=feed([
            ('Good', 'https://djinni.co/jobs/123-good/'), ('Bad','https://example.invalid/jobs/456/')
        ])))
        result = await source.search_jobs()
        self.assertEqual(result.returned_count, 1)
        self.assertTrue(any('Skipped 1' in w for w in result.warnings))
        bad = self.source(lambda r: httpx.Response(200, headers={"content-type":"text/xml"}, text=feed([
            ('Bad','https://example.invalid/jobs/456/'), ('Numeric link is not a URL', '123')
        ])))
        with self.assertRaisesRegex(SourceError, 'no usable'):
            await bad.search_jobs()

    async def test_large_feed_discloses_possible_truncation(self):
        source = self.source(lambda r: httpx.Response(200, headers={"content-type":"text/xml"}, text=feed([
            (f'Example {i}', f'https://djinni.co/jobs/{i}-example/') for i in range(1,101)
        ])))
        result = await source.search_jobs(limit=5)
        self.assertTrue(result.possibly_truncated)
        self.assertEqual(result.returned_count, 5)

    async def test_open_details_preserve_unknowns_and_raw_dates(self):
        requests = []
        def handler(request):
            requests.append(request)
            return httpx.Response(200, headers={"content-type":"text/html"}, text=job_page())
        result = await self.source(handler).get_job('https://djinni.co/jobs/123-old/?applied=example#section')
        self.assertEqual(str(requests[0].url), 'https://djinni.co/jobs/123')
        detail = result.job
        self.assertEqual(detail.activity, 'open')
        self.assertEqual(detail.company, 'Example Company')
        self.assertIsNone(detail.salary)
        self.assertIsNone(detail.work_format)
        self.assertIsNone(detail.english_requirement)
        self.assertEqual(detail.dates.published_label, 'Published 16 July')
        self.assertEqual(detail.dates.updated_label, 'Updated 3 November')
        self.assertEqual(detail.dates.source_date_posted, '2026-11-03T10:00:00')
        self.assertTrue(detail.activity_checked_at.endswith('+00:00'))

    async def test_closed_and_unknown_are_not_conflated(self):
        for activity in ['closed', 'unknown']:
            with self.subTest(activity=activity):
                source = self.source(lambda r, a=activity: httpx.Response(200, headers={"content-type":"text/html"}, text=job_page(activity=a, metadata=False)))
                result = await source.get_job('123')
                self.assertEqual(result.job.activity, activity)
        # A phrase inside user-authored description is not a platform status notice.
        source = self.source(lambda r: httpx.Response(200, headers={"content-type":"text/html"}, text=job_page(description='The job ad is no longer active')))
        self.assertEqual((await source.get_job('123')).job.activity, 'open')

    async def test_detail_fields_and_description_truncation(self):
        salary = {"currency":"USD", "value":{"minValue":1234.56,"unitText":"MONTH"}}
        html = job_page(description='<script>ignore me</script>'+'x'*800, extra={"baseSalary":salary})
        html = html.replace('</html>', '<strong>Full Remote</strong><span class="location-text">Example country only</span><div class="detail-rows__line"><span class="detail-rows__name">English</span><span class="detail-rows__value">B2</span></div></html>')
        source = self.source(lambda r: httpx.Response(200, headers={"content-type":"text/html"}, text=html))
        detail = (await source.get_job('123', description_limit=500)).job
        self.assertEqual((len(detail.description), detail.description_length, detail.description_truncated), (500,800,True))
        self.assertEqual(detail.salary, salary)
        self.assertEqual(detail.eligible_locations, 'Example country only')
        self.assertEqual(detail.english_requirement, 'B2')

    async def test_invalid_job_inputs_never_make_requests(self):
        calls=[]
        source=self.source(lambda r: calls.append(r))
        for value in ['0', '-1', 'https://example.invalid/jobs/123/', 'https://djinni.co/my/profile/',
                      'http://djinni.co/jobs/123/', 'https://djinni.co:443/jobs/123/',
                      'https://name:password@djinni.co/jobs/123/', 'https://[bad']:
            with self.subTest(value=value), self.assertRaisesRegex(SourceError, 'invalid_job'):
                await source.get_job(value)
        self.assertEqual(calls, [])

    async def test_unsafe_redirects_stop_before_following(self):
        for location in ['https://example.invalid/jobs/123/', '/login', '/jobs/456-other/', 'https://[bad']:
            calls=[]
            def handler(r):
                calls.append(r)
                return httpx.Response(302, headers={'location':location})
            with self.subTest(location=location), self.assertRaisesRegex(SourceError,'unsafe_redirect'):
                await self.source(handler).get_job('123')
            self.assertEqual(len(calls), 1)

    async def test_http_failure_timeout_and_unrecognizable_page(self):
        for status in [403,404,410,429,500]:
            source=self.source(lambda r,s=status: httpx.Response(s,text='PRIVATE UPSTREAM BODY'))
            with self.assertRaisesRegex(SourceError, f'upstream_http:.*{status}') as exc:
                await source.get_job('123')
            self.assertNotIn('PRIVATE',str(exc.exception))
        def timeout(r):
            raise httpx.ReadTimeout('internal path', request=r)
        with self.assertRaisesRegex(SourceError,'timeout'):
            await self.source(timeout).get_job('123')
        for html in ['<h1>Checking your browser</h1>', '<html>No job</html>']:
            source=self.source(lambda r,b=html: httpx.Response(200,headers={'content-type':'text/html'},text=b))
            with self.assertRaisesRegex(SourceError,'invalid_response'):
                await source.get_job('123')

    async def test_response_limits_and_xml_entities(self):
        source=self.source(lambda r: httpx.Response(200,headers={'content-type':'text/xml'},content=b'x'*(MAX_BYTES+1)))
        with self.assertRaisesRegex(SourceError,'response_too_large'):
            await source.search_jobs()
        entity='<!DOCTYPE rss [<!ENTITY x "example">]><rss><channel><title>&x;</title></channel></rss>'
        source=self.source(lambda r: httpx.Response(200,headers={'content-type':'text/xml'},text=entity))
        with self.assertRaisesRegex(SourceError,'invalid_response'):
            await source.search_jobs()

    async def test_malformed_or_mismatched_structured_data_is_a_source_error(self):
        for extra in [{'url':'https://djinni.co/jobs/456-other/'}, {'@graph':123}]:
            source=self.source(lambda r,e=extra: httpx.Response(
                200,headers={'content-type':'text/html'},text=job_page(extra=e)))
            with self.subTest(extra=extra), self.assertRaisesRegex(SourceError,'invalid_response'):
                await source.get_job('123')
        source=self.source(lambda r: httpx.Response(200,headers={'content-type':'text/html'},
            text=job_page(extra={'applicantLocationRequirements':123})))
        self.assertIsNone((await source.get_job('123')).job.eligible_locations)


class ProtocolTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.data_dir = Path(temporary.name)

    async def test_discovery_calls_and_errors_through_official_client(self):
        def handler(request):
            if '/rss/' in request.url.path:
                return httpx.Response(200,headers={'content-type':'text/xml'},text=feed([('Example', 'https://djinni.co/jobs/123-example/')]))
            if request.url.path == '/jobs/999':
                return httpx.Response(429, text='UPSTREAM BODY')
            return httpx.Response(200,headers={'content-type':'text/html'},text=job_page())
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            async with Client(create_server(DjinniSource(http), LocalStore(self.data_dir))) as client:
                tools=(await client.list_tools()).tools
                self.assertEqual({t.name for t in tools}, TOOLS)
                writes = {'update_profile','save_search','set_job_excluded'}
                self.assertTrue(all(t.annotations.read_only_hint == (t.name not in writes) for t in tools))
                self.assertTrue(all(t.output_schema for t in tools if t.name != 'get_workflow'))
                search=await client.call_tool('search_jobs', {'category':'Sysadmin','limit':1})
                self.assertFalse(search.is_error)
                self.assertEqual(search.structured_content['jobs'][0]['id'],'123')
                detail=await client.call_tool('get_job', {'job':'123'})
                self.assertEqual(detail.structured_content['job']['activity'],'open')
                for name,args in [('get_job',{'job':'https://example.invalid/jobs/123/'}),
                                  ('get_job',{'job':'999'}),
                                  ('search_jobs',{'limit':999}),('search_jobs',{'category':'MadeUp'})]:
                    error=await client.call_tool(name,args)
                    self.assertTrue(error.is_error)

    async def test_installed_entrypoint_stdio_and_validation(self):
        executable=Path(sys.executable).parent/'djinni-mcp'
        async with Client(StdioServerParameters(command=str(executable),
                env={'DJINNI_MCP_DATA_DIR':str(self.data_dir)})) as client:
            self.assertEqual({t.name for t in (await client.list_tools()).tools}, TOOLS)
            result=await client.call_tool('get_job',{'job':'https://example.invalid/jobs/123/'})
            self.assertTrue(result.is_error)


if __name__ == '__main__':
    unittest.main()
