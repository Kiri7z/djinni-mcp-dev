# Implementation dependencies

Verified from installed distribution metadata on 2026-11-09. These existing components supply general functionality; project code only maps Djinni's observed fields and coordinates two tools.

| Component | Tested version | Declared license | Purpose / primary source |
| --- | --- | --- | --- |
| mcp | 2.3.0 | MIT | Official server, client, stdio transport, schemas and tool errors; [SDK docs](https://py.sdk.modelcontextprotocol.io/), [source](https://github.com/modelcontextprotocol/python-sdk) |
| httpx | 0.28.1 | BSD-3-Clause | Bounded asynchronous public HTTP requests; [documentation](https://www.python-httpx.org/) |
| beautifulsoup4 | 4.15.0 | MIT | HTML parsing and text extraction; [upstream](https://www.crummy.com/software/BeautifulSoup/bs4/) |
| defusedxml | 0.7.1 | PSF license | Existing XML parser wrapper that rejects unsafe entities; [upstream](https://github.com/tiran/defusedxml) |
| pydantic | 2.14.3 | MIT | Tool input/output validation and schema generation; [upstream](https://github.com/pydantic/pydantic) |
| setuptools | 84.2.1 | MIT | Tested packaging backend; [upstream](https://github.com/pypa/setuptools) |
| Python standard library | Python 3.14.7 | PSF license | JSON, URL handling, UTC timestamps, unittest |

The official SDK's [installation](https://py.sdk.modelcontextprotocol.io/get-started/installation/), [tools](https://py.sdk.modelcontextprotocol.io/servers/tools/), [stdio client](https://py.sdk.modelcontextprotocol.io/client/transports/) and [error handling](https://py.sdk.modelcontextprotocol.io/servers/handling-errors/) documentation were consulted before integration. SDK 2.x APIs are used; v1 FastMCP examples are not interchangeable with this pinned version.

`pyproject.toml` declares direct dependencies; `requirements.lock.txt` records the tested resolved runtime environment, including transitive dependencies. Install it as constraints as shown in README. It is a pip freeze snapshot, not a hash-verified multi-platform lock. Build isolation may install a newer setuptools backend. Python versions other than 3.14.7 and other operating systems were not exercised.

The SDK also depends on a newer HTTP stack (`httpx2`); the Djinni source adapter uses the separately pinned HTTPX API above. Both are present in the tested environment. Do not remove or substitute SDK dependencies manually.

v0.2 adds no runtime dependency: local persistence uses the existing Python `sqlite3` module, JSON handling and standard file operations. SQLite availability was verified in the development interpreter. No ORM, document parser, model client or Markdown exporter was introduced. The AI client prepares the saved Markdown and optionally reads CV attachments.

No code from the researched job-collector repositories was copied or vendored. Libraries are installed as dependencies, with their own license metadata and notices. This table covers the selected direct components, not a complete redistribution audit of every transitive dependency. Retain applicable dependency notices if distributing a packaged environment. Project license selection and any publication review remain separate work; library licenses do not grant rights to Djinni job content.
