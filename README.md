# Djinni MCP

A small local MCP server for public Djinni job discovery, a saved candidate profile and repeat-aware recommendations.

Version: v0.2.1, checked on 2026-11-09. The default suite checks source behavior, saved profiles/history and actual stdio process exchanges. Research and implementation baselines are recorded separately.

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

Public discovery is anonymous/read-only; profile, report and exclusion changes are explicit local writes. The connected AI client handles the interview, optional document reading, matching and short drafts. There is no Djinni login, automatic application sending, document watcher, scheduler, CV parser, own LLM API or numeric scoring framework. No new runtime dependency was added for v0.2.

The [v0.1 acquisition contract](docs/tool-contract.md) and [v0.2 local workflow contract](docs/tool-contract-v0.2.md) define inputs, outputs and limits. [v0.2 verification results](docs/verification-v0.2.md) describe what was actually checked.

## Install and run

Requires Python 3.11 or newer; verified on Python 3.14.7/macOS. Run in a terminal:

```sh
git clone https://github.com/Kiri7z/djinni-mcp.git
cd djinni-mcp
python3 -m venv .venv
.venv/bin/python -m pip install -c requirements.lock.txt -e .
.venv/bin/djinni-mcp
```

The last command starts a stdio MCP server: it waits for a client and is not an interactive terminal application. Stop a manual run with Ctrl+C. Runtime dependencies are constrained to the tested environment; no browser, API key, login or Docker is required.

Configure a client to launch the absolute path to `.venv/bin/djinni-mcp` (Windows: `.venv/Scripts/djinni-mcp.exe`). Set `DJINNI_MCP_DATA_DIR` to an absolute private directory and keep it stable across projects and updates. For clients that use an `mcpServers` JSON section, adapt [this placeholder example](examples/mcp.json); other clients have their own configuration format. Do not commit your actual client configuration. See [the setup guide](docs/setup.md) for Codex commands, desktop configuration, Windows installation, verification and troubleshooting. SDK-client and installed-stdio checks passed on macOS; other platforms are not verified.

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

After updating this editable installation, restart the configured MCP server in the desktop client's MCP settings and refresh its tools. The v0.2 catalog contains eight tools. The same launch command and working directory remain valid.

Start with a request such as:

> Use Djinni MCP. Read get_workflow and my saved profile. If essential criteria are missing, ask me once and save my answers. Then find five suitable jobs, show a short assessment and optional draft, label previous recommendations with their date, and save the report.

For a new profile the initial interview explicitly has four items: roles/experience/languages; work conditions/geography/salary; an optional CV invitation; optional significant projects/achievements. It also asks whether to include short application drafts and in which language. Skipping the optional items does not block search. Existing profiles are reused without repeating the interview.

The client reads a CV using its existing attachment tools only when asked, then saves concise facts with `update_profile(resume_facts=...)`. No CV file is opened by this server. Later requests reuse the saved profile:

- "Find ten more" — reuse the loaded profile and continue the feed window; no CV reread.
- "Lower my salary expectation" — update the specified questionnaire field; retain the rest.
- "I uploaded a new CV; reread it" — explicitly refresh the CV facts; questionnaire overrides still win.
- "Don't suggest this job again" — exclude that ID; "restore it" reverses the exclusion.

Repeats are allowed and show `previously_recommended_at`. `get_history` supplies their last saved assessments. These are historical context, not an automatic freshness guarantee. Unknown publication age stays unknown; date extraction is unchanged. Each recommendation has two blocks: three sentences about the company's business/product and the role's place in it, then five sentences about the position and candidate fit/gaps/conditions, plus an optional 3–5-sentence draft. Company context comes only from the vacancy details: absent or unclear information is marked briefly without padding or guesses, and no web search or company-site visit is made unless the user asks for research. Both blocks are saved in the recommendation summary and Markdown report. Exact phrasing/tool selection remains client/model behavior and needs a manual acceptance run.

When `prepare_drafts` is yes or the user requests drafts, each recommendation includes a ready message in a blockquote, saved in both the structured draft field and Markdown report. `draft_language` can differ from `output_language`. If preference is unset, the client makes one explicit offer after the first shortlist; if no, it omits drafts and repeat offers. Drafts use only supplied experience/achievements; sample-letter claims are never imported as candidate facts.

Candidate wording in assessments and drafts defaults to past tense or experience-based phrases such as "I led a team" and "I have experience managing infrastructure". Completed achievements stay in the past. Historical team sizes and duties are not presented as ongoing unless the user explicitly confirms the specific current scope; an old CV's present tense or a current title alone is insufficient. This wording does not imply that employment ended and does not rewrite saved profiles or historical reports. The rule applies in all output languages.

Search keeps `matched_count` for source/title matches before local exclusions. Excluded jobs are removed from the returned page, so `returned_count` may be smaller than `limit`; use `next_offset` if available to continue. Search only reads local history and never saves recommendations automatically.

## Local files

With the documented project working directory, state goes to ignored `local/state.sqlite3`, and reports to `local/reports/<request_id>.md`. `DJINNI_MCP_DATA_DIR` can select another private persistent folder. Keep that location stable across chats/updates. Paths inside the installed source tree should be reviewed before a public package release.

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

Provide consistent, compact job-search results while reducing repeated browsing and unnecessary model context. This public repository is a portfolio project, not a commercial product launch. An MCP Market listing is possible future work.

## Working agreements

- Maintain project documentation in English; discuss work with the owner in Russian.
- Research existing services, libraries, SDKs, skills, and standards before implementing functionality.
- Prefer a maintained, suitable existing solution over custom infrastructure. Explain concrete limitations before choosing a custom implementation.
- Use the official MCP SDK if an MCP server is justified; do not implement the protocol from scratch.
- Keep the initial scope small: public job discovery and vacancy details. Applications and recruiter messages remain manual.
- Verify source capabilities before relying on them. Previously observed RSS response headers do not establish feed completeness or filtering support.
- Keep missing values explicit. Do not infer salary, location eligibility, or job status from unrelated signals.
- Separate deterministic data handling from model-based assessment.
- Do not reuse third-party code without checking its license. Public visibility alone is not a redistribution license.

## Privacy

See the [publication privacy boundary](docs/publication-privacy.md) before creating a public repository. Source-file checks do not sanitize Git commit identities; publish only the reviewed snapshot with deliberately chosen public metadata.

Candidate profiles, CVs, contact details, search preferences, authentication state, and generated private reports belong in ignored `local/` or an explicitly configured private data directory outside Git. Public examples/tests use synthetic placeholders. Never copy personal files from the parent workspace into tracked project files. Candidate facts are not sent to Djinni.

See the [approved research baseline](docs/research-plan.md), [research findings and reuse decisions](docs/research.md), and [dependency notes](docs/dependencies.md). The public repository contains a reviewed source snapshot; MCP Market submission and project license selection remain pending. No third-party collector code or real job-description datasets are included.

The implementation uses native RSS discovery with public HTML/JSON-LD enrichment through existing parsers. Coverage and date/status ambiguity prevent a promise of exhaustive results. Existing MCP servers were not selected for unchanged adoption. See the historical [research reproduction steps](docs/research-reproduction.md).
