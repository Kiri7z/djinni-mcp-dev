# Phase 2: simple local job-search workflow

Date: 2026-11-09. Status: implementation authorized after the owner simplified the proposal. Normative scope: [v0.2 contract](tool-contract-v0.2.md). Phase 1 remains tagged `v0.1.0`.

The goal is a useful personal job-search tool, a future public portfolio repository/listing, and less repeated model context. Keep one local MCP server. The AI client performs the interview, optional document reading, assessment and short drafts; the server handles public acquisition and local persistence.

## Accepted simplifications

- Questionnaire facts always override conflicting CV facts.
- Read/import a CV initially when requested, then only on an explicit refresh request. The user is responsible for notifying the agent of a changed file.
- Read the small saved profile at the beginning of a new search/chat. Reuse it for "five jobs, then ten more"; do not reread the PDF or repeat the interview.
- SQLite is canonical storage; save the AI's prepared Markdown as a readable report.
- Keep prior summaries and recommendation dates. Compare a newly requested job batch against the saved profile, without building content-hash/cache-invalidation machinery.
- Repeats are allowed and labelled. Exclude/restore only on an explicit user instruction; do not infer application/rejection status.
- Use existing date evidence. Unknown age is simply unknown. No date-extraction rewrite or age calculator.
- No own LLM API, document parser, watcher, scheduler, automatic applications, multi-user service, sync or export framework.

## Implementation sequence

1. Record the accepted contract and reuse decision before coding.
2. Add small profile/history/report schemas and a SQLite-backed local store using the standard library and existing Pydantic.
3. Add explicit profile/history/exclusion/save tools, bundled workflow guidance, and history metadata/local exclusion filtering in search. Keep public acquisition behavior and annotations intact.
4. Test meaningful persistence, precedence, repeats, errors, report saving and an installed-stdio workflow with synthetic data. Keep actual CV/profile data out of tracked files.
5. Update English setup/usage/verification documentation, make the implementation reviewable in Git, and give the owner a manual desktop test. Publication remains a separate release step.

## Reuse and scope

The earlier proposal inspected the MIT job-assistant project's SQLite profile/history repositories and prompts. Use Python's existing sqlite3/json/file APIs, the installed official MCP SDK and Pydantic; no collector code is copied and no new general library is created. The previous proposal's automatic fingerprints, elaborate invalidation, extra status tracking and extended age display are superseded by the owner's simpler workflow.

No new runtime dependency is needed. Platform-specific user-directory helpers, direct document import, richer exports and broad release engineering are deferred to an actual need. MCP Market currently accepts GitHub repository submissions, including a free queue: [submission form](https://mcpmarket.com/submit). No publication occurs as part of local implementation.
