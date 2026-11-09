# Research reproduction

Reference run: 2026-11-09, Python 3.14.7. Run from the repository root. These are disposable public-data research steps, not an application or MCP server. Live results can change.

## Environment

The tested adapter requires Python >=3.11. No candidate identity, cookies, browser session or API token is needed.

```sh
python3 -m venv local/research-venv
local/research-venv/bin/python -m pip install --only-binary=:all: beautifulsoup4==4.15.0 httpx==0.28.1 pydantic==2.14.3
```

PyPI metadata was checked before installation: Beautiful Soup MIT, HTTPX BSD-3-Clause, Pydantic MIT. This was not a production dependency/security audit. Reference transitive versions:

```text
annotated-types==0.8.0
anyio==4.16.0
certifi==2026.10.23
h11==0.16.0
httpcore==1.0.9
idna==3.20
pydantic_core==2.50.4
soupsieve==4.0.1
typing-inspection==0.4.5
typing_extensions==4.16.0
```

## RSS smoke check

```sh
local/research-venv/bin/python - <<'PY'
import urllib.request
import xml.etree.ElementTree as ET

url = 'https://djinni.co/jobs/rss/?primary_keyword=Sysadmin&employment=remote'
request = urllib.request.Request(url, headers={
    'User-Agent': 'Djinni-MCP-Research/0.1 (public read-only evaluation)'
})
with urllib.request.urlopen(request, timeout=25) as response:
    body = response.read()
    print(response.status, response.headers.get('Content-Type'), len(body))
items = ET.fromstring(body).findall('./channel/item')
print('items:', len(items))
print('unique links:', len({item.findtext('link') for item in items}))
PY
```

Reference count: 42. Repeat once to compare identity/order. Adding `page=2` gave identical bytes. A conditional request using observed Last-Modified returned 200/full body, not 304. Other checked filters: DevOps remote (84), Lead remote product (9). These are observations, not permanent counts or completeness guarantees.

## HTML/JSON-LD smoke check

```sh
local/research-venv/bin/python - <<'PY'
import json
import urllib.request
from bs4 import BeautifulSoup

url = 'https://djinni.co/jobs/?primary_keyword=Sysadmin&employment=remote'
request = urllib.request.Request(url, headers={
    'User-Agent': 'Djinni-MCP-Research/0.1 (public read-only evaluation)'
})
with urllib.request.urlopen(request, timeout=25) as response:
    soup = BeautifulSoup(response.read(), 'html.parser')
for block in soup.select('script[type="application/ld+json"]'):
    data = json.loads(block.string or block.get_text())
    records = data if isinstance(data, list) else [data]
    for job in records:
        print(job.get('identifier'), job.get('title'), job.get('jobLocationType'))
print('RSS:', [a['href'] for a in soup.select('a[href]') if '/rss/' in a['href']])
PY
```

Follow actual pagination links. Reference pages 1–3 contained 15/15/12 records; all 42 numeric IDs matched RSS. Compare numeric IDs, not changeable title slugs. Preserve missing salary/location fields. Inspect one open and one explicitly closed card; both may return HTTP 200. Missing JSON-LD alone must not mean closed.

## Existing adapter probe

Download [the exact inspected GitHub revision](https://github.com/kaidashova/job-assistant-mcp/tree/0e49431c85a9f1aaff9f52ce745d4fdebe5035ae) and extract under ignored `local/research/vendor/`. Retain LICENSE. Review import effects before using a different revision.

Inspected import closure: `app/__init__.py`, `app/constants/{__init__,sources}.py`, `app/schemas/{__init__,application,job,matching,profile,search,source}.py`, `app/sources/{__init__,base,djinni,rss,dou}.py`, `app/utils/{__init__,dates,text}.py`. No import-time network, candidate-data reads, subprocesses or writes were found. The sources package only instantiates stateless source objects.

Adjust only the relative extraction path if the archive name differs:

```sh
local/research-venv/bin/python - <<'PY'
import asyncio
import sys
from pathlib import Path
import httpx

repo = Path('local/research/vendor/job-assistant-mcp-0e49431c85a9f1aaff9f52ce745d4fdebe5035ae')
sys.path.insert(0, str(repo.resolve()))
from app.schemas import SourceQuery
from app.sources.djinni import DjinniSource

async def main():
    async with httpx.AsyncClient(timeout=25, follow_redirects=True, headers={
        'User-Agent': 'Djinni-MCP-Research/0.1 (public read-only evaluation)'
    }) as client:
        for keyword in ['DevOps', 'Sysadmin']:
            jobs = await DjinniSource().fetch(client, SourceQuery(keywords=[keyword], remote_only=True))
            print(keyword, len(jobs), sorted({tag for job in jobs for tag in job.tags}))
            print('populated companies:', sum(bool(job.company) for job in jobs))

asyncio.run(main())
PY
```

Reference adapter returned 84 DevOps jobs and 100 cross-category jobs for Sysadmin, with empty company/location/salary and remote=True. This does not test the higher-level search service or start the MCP server/profile/tracker.

Failure checks used existing `httpx.MockTransport`: valid empty XML -> empty list; malformed HTML with HTTP 200 -> ParseError; HTTP 403 -> HTTPStatusError. No live blocking was induced.

## Evidence and measurement

- New raw captures belong under ignored `local/`; do not commit descriptions or contacts.
- Record URL, status, Content-Type, bytes, elapsed time, relevant cache headers and actual retrieval timestamp.
- Initial probe metadata recorded observation date and elapsed time, not per-request UTC capture timestamps. Do not infer exact historical check time from pubDate/Last-Modified.
- Compare the same ID cohort and distinguish raw source bytes, extracted text, compact fields and full descriptions.
- Compact output discards descriptions. Bytes/characters are not measured model tokens.
- The existing web-reading baseline was a separate tool invocation on the same three listing URLs; HTTP commands do not reproduce its extraction/truncation. See research.md for limitations.
- Recheck terms/versions before broader deployment; use synthetic public fixtures.
