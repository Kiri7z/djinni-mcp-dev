# Job acquisition research plan — approved baseline

Baseline date: 2026-11-09. Version: 1.

The project owner approved this research scope and requested a durable baseline before research begins. This document records that scope. Record progress and findings in `research.md`; do not silently rewrite this baseline. Record material scope changes as dated amendments.

## Objective

Select the smallest practical, reusable way to acquire Djinni job listings for recurring searches, with predictable results and less unnecessary browsing/model context. A public MCP server is a later portfolio goal, not an assumption about the best acquisition method.

## Scope and boundaries

- Research public job discovery, vacancy details, activity/status evidence, and repeat-run behavior.
- Inspect available tools/skills, standard libraries, maintained packages, existing MCP servers, and hosted services before proposing custom implementation.
- No account sign-in, candidate profile access, applications, messages, purchases, paid runs, publishing, or server implementation in this phase.
- Inspect third-party code and dependencies before any installation/execution. Do not execute downloaded code merely to discover what it does.
- Keep source captures, downloaded research material, private measurements, and generated artifacts under ignored `local/`. Track only sanitized research documentation and synthetic examples.
- Use existing parsers and tooling. Small disposable measurement/extraction commands are research aids, not a new application or reusable custom parsing library.

## Stages and deliverables

### 1. Define the result contract and comparison criteria

Target fields: source ID, canonical URL, title, company, work format, eligible countries, English requirement, public salary with currency/period if stated, published/updated dates if stated, description, source activity evidence, and retrieval/check time.

Missing fields remain unknown. Never substitute salary analytics or dollar-sign tiers for the employer's salary, remote for worldwide eligibility, or a retrieval error for a closed job.

Evaluate discoverability, source coverage, filter behavior, pagination, freshness, authentication, repeatability, cost, maintenance, and licensing. Separate acquisition capability from personal candidate assessment.

### 2. Discover existing options

Check Djinni-supported public interfaces/feeds, direct public pages and structured metadata, existing collectors/MCP servers, and hosted services. Use primary documentation and source repositories. Produce a short candidate list rather than an exhaustive catalog.

### 3. Check license and access conditions

For each viable candidate, identify software license, dependency/service constraints, attribution and redistribution conditions, subscription/usage costs, and relevant source-site restrictions. Distinguish software licensing, service terms, and rights to captured data. Lack of a verified license is not permission to redistribute.

### 4. Inspect candidates before running them

Check actual data source, dependencies, release/commit identity, authentication requirements, write operations, maintenance signals, and installation burden. Select at most three options for practical evaluation; rejected candidates do not count as tested.

### 5. Run bounded, comparable public-data checks

- Use a small set of generic job categories/keywords and fixed filters, without candidate personal data.
- Compare overlapping jobs against directly retrieved source cards, as close in time as practical.
- Inspect discovery filters and pagination separately from detail accuracy. A few correct cards do not establish exhaustive coverage.
- Check available active/closed examples, absent fields, duplicate identities, and public-vs-authenticated limitations without signing in.
- Distinguish empty, partial, blocked, invalid, failed, and successful results. Make completeness unknown when it cannot be established.
- Repeat a request to inspect stable identity and duplicate behavior. Do not claim incremental-update support from two identical responses; document that observing future changes needs a later test.
- Compare the existing web-search/page-reading workflow with viable acquisition paths using equivalent tasks where possible. Report request count, response/model-context volume, elapsed time, and manual steps. Bytes/characters are proxies, not measured model tokens.
- Limit troubleshooting to identifying the cause and one straightforward corrective attempt. No proxy infrastructure, CAPTCHA bypasses, or attempts to defeat access controls. A blocker is a valid research outcome.

### 6. Compare and recommend

Deliver a comparison matrix with verified behavior, unknowns, deviations, source provenance, total cost considerations, license/access conditions, and maintenance burden. Recommend a primary path and a fallback only if justified. If no candidate meets the minimum, explain the exact gap; this does not authorize a custom collector.

### 7. Verify reproducibility and publication readiness

Record versions/commit identities and enough commands or steps to reproduce public-data checks without the owner's identity, credentials, browser session, absolute local paths, or personal preferences. Identify unresolved licensing/publication questions. Do not add a public project license on behalf of third-party authors.

### 8. Record completion against this baseline

Write English findings in `research.md`, mark each stage complete/partial/blocked, link supporting sources, and record material limitations. Give the owner a Russian recommendation. Implementation and external publication are separate later decisions.

## Acceptance and stopping criteria

- A bounded shortlist and a documented reason for every practical test/rejection.
- No more than three practically evaluated acquisition options.
- Actual public-source responses inspected where accessible; documented blockers where not.
- Explicit coverage, freshness, error, repeat-run, cost, and license limitations.
- Measured efficiency where feasible; no unmeasured token-saving claims.
- Reproducible, sanitized evidence record and a recommendation that favors reuse and minimal scope.
- Stop when these decision inputs are sufficient. Do not continue searching for an ideal solution or build a server to compensate for uncertainty.

## Amendments

None.
