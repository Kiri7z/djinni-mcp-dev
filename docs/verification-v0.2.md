# v0.2 verification

Date: 2026-11-09. Environment: Python 3.14.7/macOS, installed editable v0.2.0, existing pinned dependencies. Contract: [tool-contract-v0.2.md](tool-contract-v0.2.md). [v0.1 verification](verification.md) remains historical evidence.

## Automated checks

`.venv/bin/python -m unittest discover -s tests -v` — **25 tests passed**. No external network is used in this suite. All state tests use disposable temporary directories; no actual candidate data or host settings are modified.

Verified behavior:

- Original public acquisition/filtering/status/failure checks still pass.
- Questionnaire fields override conflicting CV facts. A salary-only patch retains other data; an explicit CV refresh replaces only the CV section. Removing an override reveals the CV fallback.
- Repeated profile reads do not import a changed PDF-like fixture. No-op updates retain version/time. A fresh store/process restores the same compact profile.
- Saved recommendations keep first/last dates and the last assessment. Ready Markdown is saved verbatim. Identical retries do not record a second presentation; conflicting IDs and stale profile versions are explicit errors.
- Explicit exclusion/restore preserves history. Mixed saves containing excluded jobs roll back. Search omits excluded IDs and labels previous recommendation dates; short pages explain exclusions.
- Invalid keys/IDs/report paths, duplicate recommendations and a corrupt database fail explicitly. Local errors do not reveal internal file errors or data bodies.
- If Markdown writing fails after database commit, the tool reports the partial outcome. An identical retry recreates the report without duplicating history.
- Official SDK protocol tests exercise the complete mocked search/profile/save/repeat/exclude workflow. The installed stdio server is launched twice to verify private-state persistence across process restarts. Tools advertise read/write annotations accurately.
- `pip check` reports no broken requirements.

The live smoke test passed at 10:51 UTC on 2026-11-09 through the installed v0.2 stdio process with isolated empty state: all eight tools were discovered; Sysadmin remote RSS returned 41 items and two summaries; three detail calls returned two open jobs and one explicitly closed job. Descriptions were bounded to 500 characters. The latest summary is in ignored `local/implementation/live-smoke.json`; real descriptions are not committed.

## Manual desktop acceptance

The v0.2 desktop run was inspected on 2026-11-09: it loaded workflow/profile, collected criteria, saved the profile, searched public jobs, inspected details and saved five recommendations. This confirms the basic search/save path. It also exposed an onboarding/draft usability gap: only two required question blocks were presented, and no draft preference or offer was included. The run tried four invalid limit=100 calls before retrying within the supported bound.

v0.2.1 updates existing instructions only: four-item onboarding with optional CV/achievements, explicit draft preference/language, ready blockquoted drafts when enabled, one offer when undecided, and explicit limit 1–50. No private profile/chat bodies or sample-letter facts were copied to the repository. The revised conversational behavior requires another desktop run after MCP restart/refresh; deterministic regression checks do not prove model wording/tool selection.

v0.2.1 checks: all 25 regression tests passed again. A fresh installed stdio process delivered the revised get_workflow text and all eight tools; initialization guidance is 430 characters. The isolated read-only inspection created no state files. Acquisition, storage and model schemas are unchanged.

Company-context update on 2026-11-09: bundled workflow, server initialization guidance, README and output contract now specify three company/role-context sentences followed by five position/fit sentences. Missing company facts are marked without padding or external research unless requested. Both blocks belong in saved summary and Markdown. All 25 existing tests passed, including installed stdio and persistence checks; git diff --check passed. No new manual model acceptance run has been performed for the revised output format, and instruction text does not enforce sentence counts deterministically.

Suggested checks: save criteria once; request five jobs and then more; change only salary; explicitly refresh a CV; repeat a search and see dates; explicitly exclude one result and verify its absence; inspect the saved Markdown. CV reading and the quality/length of prose are AI-client behavior rather than server-side parsing/generation.

No automatic CV refresh, job-content hash/cache engine, application-status detector or age feature was implemented. Token savings have not been measured. GitHub/MCP Market publication and project license selection remain separate release work.

## Pre-publication privacy review — 2026-11-09

Reviewed all 26 previously tracked regular text files, all reachable historical blobs and file paths in seven commits, and commit/tag metadata. No candidate CV/profile/report, private host path or actual credential was found in the inspected source contents. Two pattern matches were manually classified as a public URL slug and synthetic URL credentials in a rejection test. Original commit identities contain personal metadata and are excluded from the separate publication snapshot; the working history is preserved. Dedicated secret-scanner tools were unavailable, so coverage is bounded local pattern matching plus manual source/example review, not a guarantee about every secret format.

Expanded ignore rules passed 11 synthetic document/key/database-sidecar/private-directory/archive checks without creating those files. The private runtime data remains ignored and untracked. All 25 existing regression tests passed again. See [publication privacy boundary](publication-privacy.md) for the intended source-only payload and fresh metadata review required before any actual push. No repository publication or history rewrite was performed.

## Public setup preparation — 2026-11-09

Added a dedicated setup guide linked from README: source clone/install, macOS/Linux and PowerShell paths, Codex registration, generic desktop settings/JSON, stable private data location, eight-tool discovery, first-use prompts, update steps and troubleshooting. Codex registration was checked against official documentation and local CLI help without modifying the user's client configuration. All relative documentation targets and the example JSON parse successfully. All 25 regression tests passed again and pip check found no broken requirements. Other operating systems were not exercised. Public publication uses a new source-only Git history with a GitHub no-reply identity; original private state/history is not imported.

## Public installation acceptance — 2026-11-09

The explicitly authorized public repository is https://github.com/Kiri7z/djinni-mcp-dev. Its 28 source/documentation files were cloned over HTTPS and matched the reviewed per-file SHA-256 manifest. The initial two public commits used GitHub no-reply addresses for both author and committer, with no original development ancestry. A subsequent documentation-only commit records this acceptance and corrects pre-publication README wording; its author metadata and final source tree are checked before completion.

A separate new Python 3.14.7 virtual environment installed the public clone using pip install -c requirements.lock.txt -e . with build isolation and dependencies from PyPI. Installation succeeded, all 25 tests passed from that clone (including installed stdio process checks), and pip check found no broken requirements. No candidate profile or actual host configuration was imported. Raw install output and the release receipt are private local artifacts. Windows/Linux and another user's GUI configuration remain untested.

## Development repository clarification — 2026-11-09

The public source repository was renamed to djinni-mcp-dev. Local AGENTS.md instructions and their README duplicate were removed from the current public tree; application source and tests were retained. Clone URLs and setup directory names now use the development repository name. This documentation-only update does not claim a ready-to-run distribution or certify the absence of vulnerabilities.
