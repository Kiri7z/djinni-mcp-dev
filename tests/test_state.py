"""Synthetic private-state and workflow tests; no external network or actual CV."""

import sys
import sysconfig
import os
from contextlib import chdir
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
from mcp import Client, StdioServerParameters
from pydantic import ValidationError

from djinni_mcp.server import create_server
from djinni_mcp.source import DjinniSource
from djinni_mcp.state import LocalStore, SearchSave, StateError
from test_tools import feed, job_page


def batch(request_id='example_batch', version=0, ids=('123',)):
    return SearchSave(request_id=request_id, profile_version=version,
        recommendations=[{'job_id':i,'title':'Example role','summary':'Example fit. Example gap.',
            'draft':'Example draft.','source_updated_label':'Updated 3 November'} for i in ids],
        report_markdown='# Example report\n\nPrepared synthetic recommendations.\n')


class StoreTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / 'private'
        self.store = LocalStore(self.root)

    def test_empty_reads_do_not_create_state(self):
        self.assertEqual(self.store.get_profile().fields, {})
        self.assertEqual(self.store.get_history(['123']).items[0].excluded, False)
        self.assertFalse(self.root.exists())

    def test_default_state_survives_working_directory_changes_without_migration(self):
        first = self.root.parent / 'first-launch'
        second = self.root.parent / 'second-launch'
        first.mkdir()
        second.mkdir()
        # An old cwd/local profile must not be scanned or imported implicitly.
        LocalStore(first / 'local').update_profile(questionnaire={'target_roles': 'Old example'})
        with patch.dict(os.environ, {'DJINNI_MCP_DATA_DIR': ''}), \
                patch('djinni_mcp.state.user_data_path', return_value=self.root):
            with chdir(first):
                store = LocalStore()
                self.assertEqual(store.get_profile().fields, {})
                self.assertFalse(self.root.exists())
                store.update_profile(questionnaire={'target_roles': 'New example'})
            with chdir(second):
                self.assertEqual(LocalStore().get_profile().fields['target_roles'], 'New example')
            self.assertFalse((second / 'local').exists())

    def test_explicit_path_and_environment_keep_existing_profiles(self):
        old = self.root.parent / 'old-data'
        LocalStore(old).update_profile(questionnaire={'target_roles': 'Existing example'})
        with patch.dict(os.environ, {'DJINNI_MCP_DATA_DIR': str(old)}):
            self.assertEqual(LocalStore().get_profile().fields['target_roles'], 'Existing example')
            self.assertEqual(LocalStore(self.root).get_profile().fields, {})

    def test_questionnaire_precedence_patches_and_explicit_cv_refresh(self):
        first = self.store.update_profile(questionnaire={'salary':'USD 3000/month','current_location':'Example A'},
            resume_facts={'current_location':'Example B','candidate_summary':'Old example','languages':'B1'})
        self.assertEqual(first.fields['current_location'], 'Example A')
        changed = self.store.update_profile(questionnaire={'salary':'USD 2500/month'})
        self.assertEqual(changed.fields['candidate_summary'], 'Old example')
        refreshed = self.store.update_profile(resume_facts={'current_location':'Example C','candidate_summary':'New example'})
        self.assertEqual(refreshed.fields['current_location'], 'Example A')
        self.assertEqual(refreshed.fields['salary'], 'USD 2500/month')
        self.assertNotIn('languages', refreshed.fields)
        fallback = self.store.update_profile(questionnaire={'current_location':None})
        self.assertEqual(fallback.fields['current_location'], 'Example C')
        self.assertEqual(LocalStore(self.root).get_profile(), fallback)

    def test_saved_profile_is_reused_without_document_reads_or_noop_updates(self):
        profile = self.store.update_profile(resume_facts={'candidate_summary':'Imported example'})
        document = self.root/'example-resume.pdf'
        document.write_bytes(b'Changed file, deliberately not imported')
        for _ in range(3):
            self.assertEqual(self.store.get_profile(), profile)
        self.assertEqual(self.store.update_profile(resume_facts={'candidate_summary':'Imported example'}), profile)
        with self.assertRaisesRegex(StateError,'invalid_update'):
            self.store.update_profile()

    def test_repeats_preserve_first_date_and_update_last_assessment(self):
        with patch('djinni_mcp.state.now',return_value='2026-11-09T10:00:00+00:00'):
            first = self.store.save_search(batch())
        with patch('djinni_mcp.state.now',return_value='2026-11-16T10:00:00+00:00'):
            request = batch('second_batch')
            request.recommendations[0].summary='New example assessment.'
            second = self.store.save_search(request)
        history = self.store.get_history(['123']).items[0]
        self.assertEqual(history.first_recommended_at, first.saved_at)
        self.assertEqual(history.last_recommended_at, second.saved_at)
        self.assertEqual(history.summary, 'New example assessment.')
        self.assertEqual(Path(second.report_path).read_text(), request.report_markdown)

    def test_idempotent_retry_conflict_and_stale_profile(self):
        request = batch()
        first = self.store.save_search(request)
        retry = self.store.save_search(request)
        self.assertTrue(retry.replayed)
        self.assertEqual(retry.saved_at, first.saved_at)
        self.assertEqual(self.store.get_history(['123']).items[0].last_recommended_at, first.saved_at)
        changed = batch()
        changed.report_markdown='Different output'
        with self.assertRaisesRegex(StateError,'request_conflict'):
            self.store.save_search(changed)
        self.store.update_profile(questionnaire={'salary':'Example new salary'})
        with self.assertRaisesRegex(StateError,'profile_changed'):
            self.store.save_search(batch('stale_batch'))
        self.assertTrue(self.store.save_search(request).replayed)

    def test_exclusion_and_restore_preserve_history_and_save_is_atomic(self):
        self.store.set_job_excluded('https://djinni.co/jobs/456-example/', reason='User said no')
        with self.assertRaisesRegex(StateError,'excluded_job'):
            self.store.save_search(batch(ids=('123','456')))
        self.assertIsNone(self.store.get_history(['123']).items[0].last_recommended_at)
        self.assertFalse((self.root/'reports').exists())
        self.store.set_job_excluded('456',excluded=False)
        self.store.save_search(batch(ids=('123','456')))
        original = self.store.get_history(['456']).items[0]
        self.store.set_job_excluded('456')
        restored = self.store.set_job_excluded('456', excluded=False)
        self.assertEqual(restored.summary, original.summary)
        self.assertEqual(restored.first_recommended_at, original.first_recommended_at)

    def test_failed_markdown_write_preserves_database_and_retry_restores_view(self):
        request = batch()
        with patch.object(self.store,'_write_report',side_effect=OSError('private internal path')):
            with self.assertRaisesRegex(StateError,'report_write_failed: database saved') as exc:
                self.store.save_search(request)
        self.assertNotIn('private internal path',str(exc.exception))
        self.assertEqual(self.store.get_history(['123']).items[0].summary, request.recommendations[0].summary)
        retry = self.store.save_search(request)
        self.assertTrue(retry.replayed)
        self.assertEqual(Path(retry.report_path).read_text(), request.report_markdown)

    def test_invalid_paths_duplicates_and_corrupt_database_fail_explicitly(self):
        for request in [dict(batch().model_dump(),request_id='../outside'),
                        dict(batch().model_dump(),recommendations=[r.model_dump() for r in batch().recommendations]*2)]:
            with self.assertRaises(ValidationError):
                SearchSave(**request)
        self.root.mkdir()
        self.store.path.write_text('Not a database: PRIVATE CONTENT')
        with self.assertRaisesRegex(StateError,'storage_error') as exc:
            self.store.get_profile()
        self.assertNotIn('PRIVATE CONTENT', str(exc.exception))

    def test_incremental_profile_growth_is_bounded_without_losing_saved_fields(self):
        initial = self.store.update_profile(questionnaire={f'field_{i}':'Example' for i in range(30)})
        with self.assertRaisesRegex(StateError,'profile_too_large'):
            self.store.update_profile(questionnaire={'another_field':'Extra'})
        self.assertEqual(self.store.get_profile(),initial)


class StateProtocolTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    async def test_full_mocked_search_workflow_repeat_and_exclusion(self):
        def handler(request):
            if '/rss/' in request.url.path:
                return httpx.Response(200,headers={'content-type':'text/xml'},text=feed([
                    ('Example role','https://djinni.co/jobs/123-example/'),
                    ('Another example','https://djinni.co/jobs/456-example/')]))
            return httpx.Response(200,headers={'content-type':'text/html'},text=job_page())
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            async with Client(create_server(DjinniSource(http), LocalStore(self.root))) as client:
                async def call(name, arguments={}):
                    result = await client.call_tool(name,arguments)
                    self.assertFalse(result.is_error, result.content)
                    return result.structured_content
                guidance=await client.call_tool('get_workflow',{})
                self.assertFalse(guidance.is_error)
                self.assertEqual((await call('get_profile'))['version'],0)
                profile=await call('update_profile',{'questionnaire':{'target_roles':'Example operations'},
                    'resume_facts':{'candidate_summary':'Example experience'}})
                self.assertEqual((await call('search_jobs',{'limit':2}))['returned_count'],2)
                self.assertEqual((await call('get_job',{'job':'123'}))['job']['activity'],'open')
                saved=await call('save_search',{'request':batch(version=profile['version']).model_dump()})
                repeated=await call('search_jobs',{'limit':2})
                self.assertEqual(repeated['jobs'][0]['previously_recommended_at'],saved['saved_at'])
                await call('set_job_excluded',{'job':'123','reason':'Explicit synthetic exclusion'})
                filtered=await call('search_jobs',{'limit':2})
                self.assertEqual([j['id'] for j in filtered['jobs']],['456'])
                self.assertEqual((filtered['matched_count'],filtered['returned_count']),(2,1))
                self.assertTrue(any('locally excluded' in w for w in filtered['warnings']))
                for name,args in [('update_profile',{'questionnaire':{'bad/key':'invalid'}}),
                                  ('get_history',{'job_ids':['../bad']}),
                                  ('update_profile',{})]:
                    self.assertTrue((await client.call_tool(name,args)).is_error)
        self.assertEqual(LocalStore(self.root).get_profile().fields['target_roles'],'Example operations')

    async def test_installed_stdio_state_survives_a_fresh_process(self):
        parameters=StdioServerParameters(command=str(Path(sysconfig.get_path('scripts')) / ('djinni-mcp.exe' if os.name == 'nt' else 'djinni-mcp')),
            env={'DJINNI_MCP_DATA_DIR':str(self.root)})
        async with Client(parameters) as client:
            profile=await client.call_tool('update_profile',{'questionnaire':{'salary':'Example salary'}})
            self.assertFalse(profile.is_error)
            saved=await client.call_tool('save_search',{'request':batch(version=profile.structured_content['version']).model_dump()})
            self.assertFalse(saved.is_error)
        async with Client(parameters) as client:
            profile=await client.call_tool('get_profile',{})
            self.assertEqual(profile.structured_content['fields']['salary'],'Example salary')
            history=await client.call_tool('get_history',{'job_ids':['123']})
            self.assertEqual(history.structured_content['items'][0]['last_recommended_at'], saved.structured_content['saved_at'])


if __name__ == '__main__':
    unittest.main()
