# v0.1 verification

Reference run: 2026-11-09, Python 3.14.7 on macOS. Contract: [tool-contract.md](tool-contract.md).

## Results

| Contract acceptance check | Evidence | Result |
| --- | --- | --- |
| Deterministic source behavior and failures | Synthetic HTTPX fixtures: native filters, literal substring, feed-window offset, numeric deduplication, unknowns/dates, description bounds, open/closed/unknown, HTTP/timeout, malformed/oversized input, URL/redirect boundaries | Passed |
| Official MCP protocol and schemas | SDK in-memory client discovers exactly two typed read-only tools, calls both, observes tool errors and rejects invalid argument constraints | Passed |
| Installed stdio process | SDK client launches installed `djinni-mcp`, lists tools and gets a structured tool error without external network access | Passed |
| Live anonymous source through installed stdio | One Sysadmin remote RSS search and three public detail calls | Passed |
| Reproducible local usage | README setup/test commands, dependency snapshot, placeholder client configuration | Included |

Default command: `.venv/bin/python -m unittest discover -s tests -v` — **14 tests passed**. Test cases group related failures with subtests; this count is not a count of individual assertions. Dependency consistency was checked with `pip check`.

Live run at 09:14 UTC:

- RSS returned 42 items; the tool returned two summaries with unknown activity and unknown whole-site coverage.
- The first result's detail was recognized as open; a remote format and a country restriction were extracted.
- Public research example `837568` was recognized as open. Work format, location and English requirement were extracted. Source datePosted differed from the visible publication label; both were preserved without inventing a year.
- Public research example `845892` was recognized as closed from its explicit notice, despite HTTP 200. Missing company and structured dates remained null.
- Descriptions were limited to 500 characters with truncation and original length reported.

The raw observation summary remains in ignored `local/implementation/live-smoke.json`. No real description bodies or candidate information are tracked. Rerun with `.venv/bin/python tests/live_smoke.py`; current source state can differ.

## Desktop client acceptance — phase 1 complete

On 2026-11-09 the owner connected the local stdio server in the desktop application and reported a successful manual search/detail test. At 09:37 UTC both tools were independently invoked from the active chat through that connection:

- `search_jobs(category="Sysadmin", remote_only=true, limit=3)` succeeded, with 41 fetched items and three returned summaries. Search activity and whole-site coverage remained unknown.
- `get_job(job="857167", description_limit=1000)` succeeded, reported open activity and country restrictions, returned null for an unavailable English requirement, and marked description truncation (1000 of 2156 characters).
- Both MCP responses had `isError=false`. No credentials or private candidate data were needed.

Phase 1 is accepted as a working public-discovery baseline. This does not establish exhaustive coverage or personalized matching quality. The source count changing from 42 to 41 between checks is recorded as a changed feed window, not evidence of a closure.

## Limits

- This is not exhaustive job coverage, a correctness proof for every Djinni layout, or a durability/performance/token-savings benchmark.
- Only five verified category values are exposed. No persistent history, cross-source aggregation, account integration or recurring scheduling is implemented.
- The parsers depend on observed public markup and English platform labels. A blocked, changed or mismatched document should raise an acquisition error rather than silently become an empty/closed result; other unexpected layouts may require adapter updates.
- `possibly_truncated=false` does not prove completeness. Native remote/company filters remain source behavior; they do not certify per-job eligibility or employer type.
- A desktop-client connection was verified in addition to the official SDK client and an actual child process. Other client applications and operating systems were not tested; the actual private host configuration is not tracked.
- No GitHub/MCP Market publication, project license selection, or re-publication of job content occurred.
