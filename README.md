# Djinni MCP — development repository

Source code for Djinni MCP, distributed as a ready-to-run PyPI package. Version 0.3.0 is the first stable release following independent Fedora acceptance. Ready Ukrainian application drafts are included by default; explicit opt-outs and language choices take priority. The source remains available for inspection, development and testing.

A small local MCP server for public Djinni job discovery, a saved candidate profile and repeat-aware recommendations.

Stable package: v0.3.0. Previous implementation and release checks are recorded in the verification documents. The default suite checks source behavior, saved profiles/history and actual stdio process exchanges. Research and implementation baselines are recorded separately.

**Start here:** [installation, MCP connection and troubleshooting](docs/setup.md). Requires a locally running MCP client with stdio support. No Djinni login or API key is required by this server; your AI client has its own access and pricing.

Phase 1 is an accepted development baseline. Phase 2 follows the [simplified plan](docs/phase-2-plan.md) and [v0.2 contract](docs/tool-contract-v0.2.md). The public repository starts from a reviewed source snapshot; private development history is not included.

## Tools

- `search_jobs`: native RSS filters, compact summaries, stable numeric IDs, local literal title filtering and a bounded result window.
- `get_job`: current public vacancy details, explicit missing values, source date labels, bounded plain-text descriptions and open/closed/unknown activity evidence.
- `get_workflow`: bundled instructions for the AI client, with no mandatory skill installation.
- `get_profile` / `update_profile`: a compact saved profile; questionnaire answers override CV facts.
- `get_history`: previous recommendation dates, summaries and drafts for selected IDs.
- `save_search`: save selected recommendations and the client's ready Markdown report.
- `set_job_excluded`: explicitly exclude or restore a job at the user's request.

Public discovery is anonymous/read-only; profile, report and exclusion changes are explicit local writes. The connected AI client handles the interview, optional document reading, matching and short drafts. There is no Djinni login, automatic application sending, document watcher, scheduler, CV parser, own LLM API or numeric scoring framework. The package uses platformdirs for a persistent data location across launch directories.

The [v0.1 acquisition contract](docs/tool-contract.md) and [v0.2 local workflow contract](docs/tool-contract-v0.2.md) define inputs, outputs and limits. [v0.2 workflow verification](docs/verification-v0.2.md) and [v0.3 package/publication verification](docs/verification-v0.3.md) describe completed checks and limits.

## Install and run

End-user setup is in [the connection guide](docs/setup.md). The PyPI connection for a stdio MCP client uses command `uvx` with args `["djinni-mcp@0.3.0"]`. No source checkout or development package is required.

For source inspection, local changes and tests, see [developer setup](docs/development.md). The PyPI package readme is [docs/package-readme.md](docs/package-readme.md); developer instructions and tests are excluded from the installable archives.

Example tool arguments:

```json
{"category":"Sysadmin","remote_only":true,"company_type":"product","limit":10}
```

Pass those arguments to `search_jobs`, then use a returned numeric ID with `get_job`:

```json
{"job":"123456","description_limit":4000}
```

`123456` is a synthetic example, not a verified vacancy. Available categories in v0.1: Sysadmin, DevOps, Lead, Head Chief, Support. Remote filtering does not imply worldwide eligibility; inspect details. Feed completeness is unknown, and offset only moves inside the currently fetched feed. Never interpret a missing result as a closed vacancy.

## Personal search workflow

After updating the configured package version or a source installation, restart the MCP server in the client and refresh its tools. The v0.2 catalog contains eight tools. The same launch command and working directory remain valid.

Start with a request such as:

> Use Djinni MCP. Read get_workflow and my saved profile. If essential criteria are missing, ask me once and save my answers. Then find five suitable jobs, show a short assessment and ready Ukrainian application draft unless I decline, label previous recommendations with their date, and save the report.

For a new profile the initial interview explicitly has four items: roles/experience/languages; work conditions/geography/salary; an optional CV invitation; optional significant projects/achievements. It states that ready application drafts are included in Ukrainian by default; users may choose another language or opt out without blocking search. Skipping the optional items does not block search. Existing profiles are reused without repeating the interview.

The client reads a CV using its existing attachment tools only when asked, then saves concise facts with `update_profile(resume_facts=...)`. No CV file is opened by this server. Later requests reuse the saved profile:

- "Find ten more" — reuse the loaded profile and continue the feed window; no CV reread.
- "Lower my salary expectation" — update the specified questionnaire field; retain the rest.
- "I uploaded a new CV; reread it" — explicitly refresh the CV facts; questionnaire overrides still win.
- "Don't suggest this job again" — exclude that ID; "restore it" reverses the exclusion.

Repeats are allowed and show `previously_recommended_at`. `get_history` supplies their last saved assessments. These are historical context, not an automatic freshness guarantee. Unknown publication age stays unknown; date extraction is unchanged. Each recommendation has two blocks: three sentences about the company's business/product and the role's place in it, then five sentences about the position and candidate fit/gaps/conditions, plus a ready 3–5-sentence draft unless explicitly declined. Company context comes only from the vacancy details: absent or unclear information is marked briefly without padding or guesses, and no web search or company-site visit is made unless the user asks for research. Both blocks are saved in the recommendation summary and Markdown report. Exact phrasing/tool selection remains client/model behavior. Independent Fedora feedback confirmed the default-draft workflow.

Ready application drafts are included by default: an unset `prepare_drafts` enables them, while an explicit saved `no` disables them. Explicit instructions for the current request take priority. Each enabled recommendation includes the actual message in a blockquote, saved in both the structured draft field and Markdown report; an offer to prepare it later is insufficient. Draft language is the explicit current request language, then the saved `draft_language`, then Ukrainian. It is independent of `output_language`, and missing language never blocks a draft. A one-request exception does not silently change saved preferences. Drafts use only supplied experience/achievements; sample-letter claims are never imported as candidate facts.

Candidate wording in assessments and drafts defaults to past tense or experience-based phrases such as "I led a team" and "I have experience managing infrastructure". Completed achievements stay in the past. Historical team sizes and duties are not presented as ongoing unless the user explicitly confirms the specific current scope; an old CV's present tense or a current title alone is insufficient. This wording does not imply that employment ended and does not rewrite saved profiles or historical reports. The rule applies in all output languages.

Search keeps `matched_count` for source/title matches before local exclusions. Excluded jobs are removed from the returned page, so `returned_count` may be smaller than `limit`; use `next_offset` if available to continue. Search only reads local history and never saves recommendations automatically.

## Local files

The default state directory is the platform-specific user-data folder listed in [setup](docs/setup.md), independent of the working directory and uv cache. It contains `state.sqlite3` and `reports/<request_id>.md`. `DJINNI_MCP_DATA_DIR` selects another private persistent folder. Existing source users should retain their explicit setting to reuse old data; no automatic discovery/migration occurs. Development and release checks use ignored `local/` or temporary directories.

The database holds the questionnaire, the latest explicitly imported CV facts, last recommendation summaries and saved report payloads. `get_profile` returns only the merged effective fields to reduce repeated context. Updating a questionnaire patches named fields; null removes an override. Supplying `resume_facts` replaces the CV section. Neither action scans files.

`save_search` takes a new safe `request_id` for each output batch and the profile version used. Identical retries are idempotent. SQLite commits the structured records first; the Markdown file is an atomically written readable copy. If that file fails to write, the tool clearly reports that the database was saved and identical retry can restore the report. Different data under an existing request ID is rejected.

To inspect history, use `get_history` with selected numeric IDs or read the saved reports. To back up/export the complete local state, stop the MCP and copy the private data directory. To reset it, stop the MCP and explicitly remove `state.sqlite3` and the reports directory; this deletes the saved profile/history/reports. No deletion is automatic. The database is ordinary local SQLite, not an encrypted vault. Local storage does not prevent the selected AI provider from processing facts supplied to it.

## Verify

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m pip check
```

The default suite uses synthetic HTTP fixtures and isolated temporary state, including a mocked full workflow and state persistence across two installed stdio processes, without external network access. An optional live smoke test isolates the state and performs one RSS search and up to three detail fetches, plus bounded redirects:

```sh
.venv/bin/python tests/live_smoke.py
```

Live observations are written to ignored `local/implementation/live-smoke.json`. Availability and activity can change; this is a bounded smoke test, not a full-site or long-term reliability check.

## Purpose

Provide consistent, compact job-search results while reducing repeated browsing and unnecessary model context. An MCP Market listing is possible future work.

## Privacy

See the [publication privacy boundary](docs/publication-privacy.md) before creating a public repository. Source-file checks do not sanitize Git commit identities; publish only the reviewed snapshot with deliberately chosen public metadata.

Candidate profiles, CVs, contact details, search preferences, authentication state, and generated private reports belong in ignored `local/` or an explicitly configured private data directory outside Git. Public examples/tests use synthetic placeholders. Never copy personal files from the parent workspace into tracked project files. Candidate facts are not sent to Djinni.

See the [approved research baseline](docs/research-plan.md), [research findings and reuse decisions](docs/research.md), and [dependency notes](docs/dependencies.md). The public repository contains a reviewed source snapshot; MCP Market submission remains pending. The project code is MIT licensed; see [LICENSE](LICENSE). No third-party collector code or real job-description datasets are included.

The implementation uses native RSS discovery with public HTML/JSON-LD enrichment through existing parsers. Coverage and date/status ambiguity prevent a promise of exhaustive results. Existing MCP servers were not selected for unchanged adoption. See the historical [research reproduction steps](docs/research-reproduction.md).

Normal recommendations display activity only when get_job confirms open/closed status. Unknown activity labels are omitted from chat and reports; raw tool uncertainty remains available and is never converted into an active-status claim.
