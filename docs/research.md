# Djinni job acquisition research

Checked on 2026-11-09 against [approved baseline v1](research-plan.md), committed before research as `96ada0a`. Anonymous, public, read-only access only.

## Decision

The leading acquisition approach is Djinni's native RSS for discovery, enriched and checked through public HTML/JobPosting JSON-LD. Existing XML/HTML parsers suffice; the tested public scenarios do not require browser automation.

No inspected MCP server meets our requirements unchanged. The smallest MIT candidate runs but has significant data-contract gaps. A later decision should compare targeted reuse of that adapter with a thin official-SDK integration. Research completion does not authorize a custom collector or server implementation.

Fallback: public HTML listings with JSON-LD and pagination, particularly when RSS coverage is uncertain. Neither approach establishes access to all authenticated jobs.

Exactly three acquisition options were practically evaluated: native RSS; public HTML/JSON-LD; the Djinni adapter from `kaidashova/job-assistant-mcp`. Other candidates were inspected, not run. No account, candidate profile, paid service, recruiter message, or application action was used.

## 1. Result contract

Target fields: numeric source ID, canonical URL, title, company, description, work format, eligible locations, English requirement, stated employer salary, source dates, activity evidence, and check time.

- Missing or ambiguous fields remain unknown/raw values.
- `TELECOMMUTE` is not worldwide eligibility. Structured region data may omit country restrictions from visible text.
- Dollar-sign tiers and platform salary analytics are not employer salaries.
- HTTP success and a future `validThrough` do not by themselves establish current activity.
- Failed acquisition means error/unknown, not zero matches or closed.
- RSS `pubDate` and JSON-LD `datePosted` are not safely interpreted as original publication dates.

## 2. Practical option A: native RSS

Source: [Djinni RSS](https://djinni.co/jobs/rss/). The [filtered public search](https://djinni.co/jobs/?primary_keyword=Sysadmin&employment=remote) itself links to the corresponding filtered feed. This is not an invented endpoint.

Actual anonymous HTTP returned 200 and parseable RSS. Python's existing `xml.etree.ElementTree` parsed it; no XML parser was implemented. Requests used an explicit research user agent.

| Query | RSS count | Public HTML comparison | Finding |
| --- | ---: | --- | --- |
| Unfiltered | 100 | Not exhaustive | Potentially truncated |
| `primary_keyword=Sysadmin&employment=remote` | 42 | Three pages, 15 + 15 + 12 unique IDs | Exact ID-set agreement for this snapshot |
| Same query plus `page=2` | 42 | Identical RSS bytes | Parameter did not advance feed |
| `primary_keyword=DevOps&employment=remote` | 84 | No exhaustive HTML comparison | DevOps category tags |
| `primary_keyword=Lead&employment=remote&company_type=product` | 9 | Nine matching IDs; HTML cards labelled Product | Exact ID-set agreement for this snapshot |
| Site title-search fields: `all_keywords` / `search_type=title-only` | 100 | First HTML page had 15 IDs | Wide query; phrase/AND semantics not established |
| Synthetic no-match title query | 0 | Valid XML | Empty differs from failed parsing |

Items provided title, link, GUID, description HTML, pubDate, categories. Dedicated company, location, salary, English, and active/closed fields were absent from the inspected item schema. Information embedded in prose is not verified normalized coverage.

An immediate repeat was byte-identical. `If-Modified-Since` using the observed Last-Modified returned 200 and the full 238,271-byte body, not 304. No ETag was observed in the initial response; conditional-GET savings cannot be assumed.

Coverage limits: 100 entries were observed in broad feeds; this does not prove a documented universal cap. The one paging check did not advance results. Agreement for the 42/9-item cohorts is not whole-site completeness. Long-term changes, ordering ties, additional filters, and authenticated coverage remain untested.

## 3. Practical option B: public HTML/JSON-LD

Listing pages contain `script[type="application/ld+json"]` with JobPosting records. Existing Beautiful Soup 4.15.0 plus Python's HTML parser located it, and `json.loads` decoded it. No custom parsing library or browser was written.

Across the same 42 listing records:

- All 42 numeric IDs matched RSS.
- JSON-LD included company, title, URL, description, category, experience, employment type, source dates.
- 35 contained `jobLocationType=TELECOMMUTE`; seven omitted it despite appearing in the remote search. The filter is not per-item proof.
- 29 contained applicantLocationRequirements; completeness of country eligibility was not established.
- Six contained employer baseSalary with currency and monthly min/max. Absent salaries remained absent.
- English was visible in the sampled detail HTML, but not a dedicated JSON-LD field. Extraction across all jobs was not implemented/validated.
- A login-to-see-all-jobs notice appeared on listings; label anonymous coverage public-only.

One [open card](https://djinni.co/jobs/837568-it-service-desk-and-ai-helpdesk-lead/) and one [explicitly closed card](https://djinni.co/jobs/845892-team-lead-infrastructure-noc-sre-lead/) both returned HTTP 200. The closed card said the ad was no longer active and had no JobPosting JSON-LD. The open card had JSON-LD and no closed notice. This is a bounded observation, not a universal detector: missing JSON-LD alone must not mean closed.

Timestamp counterexample: the open card visibly said `Published 16 July` / `Updated 3 November`, while RSS pubDate and JSON-LD datePosted pointed to November 3. Do not invent a year for a yearless label or treat source dates as original publication dates. Its December 3 validThrough does not guarantee it stays open until then.

## 4. Practical option C: existing MIT adapter

[kaidashova/job-assistant-mcp](https://github.com/kaidashova/job-assistant-mcp), commit `0e49431c85a9f1aaff9f52ce745d4fdebe5035ae`, package 0.1.0, initial commit October 5, 2026. Sustained maintenance was not established.

[MIT license](https://github.com/kaidashova/job-assistant-mcp/blob/0e49431c85a9f1aaff9f52ce745d4fdebe5035ae/LICENSE): retain applicable notices when reusing code. This does not license Djinni content.

The [adapter](https://github.com/kaidashova/job-assistant-mcp/blob/0e49431c85a9f1aaff9f52ce745d4fdebe5035ae/app/sources/djinni.py) uses HTTPX and standard-library XML parsing. Its import closure was inspected before execution: no import-time network, candidate/profile/database reads, subprocesses or writes. Only `DjinniSource.fetch` was run, with HTTPX and Pydantic. The full MCP server, matching service, tracker and profile layer were not started or tested.

| Probe | Observed result |
| --- | --- |
| DevOps remote | 84 results, DevOps tags; no company/location/salary populated |
| Sysadmin remote | 100 results across many categories; Sysadmin absent from category mapping |
| Remote attribution | Every result marked true from the request flag, without item-level confirmation |
| Valid empty RSS, local mock | Empty list |
| HTTP 200 malformed HTML, local mock | ParseError, not empty success |
| HTTP 403, local mock | HTTPStatusError, not empty success |
| Synthetic same numeric vacancy with renamed URL slug | Different generated IDs |

These are raw-adapter results. Higher layers apply additional text filtering and were not run; do not claim the full server returns the same unfiltered output. A broad recent feed can nevertheless omit category results before local filtering occurs.

Source-inspected gaps: get_job reads cache instead of live status; no closed field/check time; no pagination; URL-hash identity changes with slug; missing company defeats company/title deduplication. README claims SDK v2, but [pyproject](https://github.com/kaidashova/job-assistant-mcp/blob/0e49431c85a9f1aaff9f52ce745d4fdebe5035ae/pyproject.toml) permits `mcp>=1.2.0`; full-server compatibility untested.

Decision: a permissible targeted-reuse/PR candidate, not a ready solution. No fixes were made during research.

## 5. Inspected alternatives, not executed

| Candidate | License/access | Reason not tested |
| --- | --- | --- |
| [facetoplace/Workix](https://github.com/facetoplace/Workix), `403d4210566f1ca15b21e293813699a354f4d6c8` | [`mcp/` has MIT LICENSE](https://github.com/facetoplace/Workix/blob/403d4210566f1ca15b21e293813699a354f4d6c8/mcp/LICENSE); root has separate noncommercial terms | Same RSS, larger multi-board/proxy/hub scope. Existing rss-parser, but missing dates replaced with current time; no live closure check. Source version 1.2.7; current npm version unverified. |
| [dvoichuck/ai-job-hunt-kit-public](https://github.com/dvoichuck/ai-job-hunt-kit-public), `176b558036422a00283a6fc0209371c09821d631` | No license file found; disclaimer is not reuse permission | Current public name found; earlier 404 did not prove permanent disappearance. Browser/account/write scope unnecessary, redistribution unresolved. |
| [YaroslavMichkivskyi/djinni-mcp](https://github.com/YaroslavMichkivskyi/djinni-mcp), `6119b1e27a9cf9da040ad0b8a0b0743c75612c9d` | No license file found; personal/still testing | Custom protocol machinery plus account/write features; no verified redistribution grant. |
| [bovi/djinni-scraper](https://apify.com/bovi/djinni-scraper) | Hosted, no OSS source/license established | Account/metered dependency; documented capabilities untested, header/README pricing inconsistent. |
| [blackfalcondata/djinni-scraper](https://apify.com/blackfalcondata/djinni-scraper) | Hosted, no OSS source/license established | Incremental/compact output untested; post-fetch filters/default page cap complicate coverage. Contact extraction unnecessary. |

bovi header advertised from USD 0.70/1,000 while README stated USD 0.00099/result for a platform tier. This discrepancy is unresolved. blackfalcondata README listed USD 0.005/start plus USD 0.00095/result. Neither is a verified total including plans, optional proxies, failures and repeat detail requests. [Apify pricing](https://apify.com/pricing) listed USD 5 Free credit; no account or eligibility test was performed.

The [Standard Actor Contract](https://docs.apify.com/legal/standard-actor-contract) is a default platform-use contract, not an OSS redistribution license; actor-specific overrides were not verified. Separate use of a hosted service, copying its code, and rights to third-party output. [General terms](https://docs.apify.com/legal/general-terms-and-conditions) describe a business-oriented service; applicability to this personal portfolio use is unresolved. Hosted options remain documented fallbacks, not the selected local solution.

## 6. Access and publication conditions

- [PeopleForce's own guide](https://help.peopleforce.io/en/articles/9299327-integration-with-djinni) verifies employer API-key integration, posting and applicant synchronization. It does not establish an anonymous candidate-search API. No public candidate-search documentation was found in this bounded check.
- [Djinni Terms of Use](https://djinni.co/terms-of-use) prohibit spam and sharing recruiter correspondence. The inspected page does not explicitly grant bulk job-text republication rights or settle all automated public-read uses.
- [robots.txt](https://djinni.co/robots.txt) returned 200: disallowed `/jobs2`, `/q`, `/developers`, `/free-jobs`, `/set_lang`; tested `/jobs/` routes were not disallowed. This is not a copyright/redistribution grant.
- Source access, library licensing and rights to captured job text are separate. Public repository examples should be synthetic, with source links rather than copied real description/contact datasets. Recheck source conditions before publication or wider deployment.

## 7. Efficiency and repeated searches

One observed 42-job cohort, not a performance SLA:

| Representation | Requests | Size |
| --- | ---: | ---: |
| Original HTML listing bodies | 3 | 1,075,385 bytes |
| Filtered RSS | 1 | 238,271 bytes |
| Extracted full JSON-LD | Local processing | 197,744 bytes |
| Selected compact JSON fields, without descriptions | Local processing | 16,646 UTF-8 bytes / 16,528 characters |

Compact output omits 119,628 description characters, so it is not information-equivalent to full results. RSS and HTML have different metadata. This shows a context-reduction opportunity from parsing and selective retrieval, not measured token savings or an inherent benefit of MCP.

Opening the same three listing URLs through the existing web-reading tool returned a serialized payload of 28,921 characters in 1.476 seconds. It extracts/truncates content, and timing includes different work than raw HTTP. Direct page request times summed to 1.555 seconds; RSS took 0.459 seconds. No quality-equivalent end-to-end speed, ranking or actual token benchmark was performed.

Recurring search needs numeric identity and locally stored observations for first-seen/changed/already-shown/closed. Immediate repeat stability was observed; future changes, update latency and scheduling were not tested or implemented. Missing from a limited feed must not mean closed.

## 8. Recommendation and next decision

1. Use native RSS plus public HTML/JSON-LD enrichment and existing parsers as the leading source path.
2. Keep candidate assessment/reporting in a skill or existing tools; do not start with spreadsheets, proxies, account automation or a scheduler.
3. Decide separately whether to adapt the MIT project or build a minimal official-SDK interface around the verified source path. Preserve notices for reused code. No custom XML/HTML/protocol libraries are justified.
4. Define date, location and activity uncertainty before implementation. Do not promise exhaustive search or guaranteed token savings.

## 9. Evidence and baseline completion

See [reproduction steps](research-reproduction.md). Python 3.14.7; parsing dependencies and downloaded inspected adapter exist only under ignored `local/`. Tested archive SHA-256: `6277da13643bc752bee670002531a15aa735baa77534a8a53c6604608fbca7a5`.

Ignored `local/research/2026-11-09/` contains HTTP bodies/metadata, structured captures, a SHA-256 manifest, dependency metadata, adapter/error probes and size measurements. This tracked report contains sanitized findings, not candidate data or copied job-description datasets.

| Approved stage | Status | Qualification |
| --- | --- | --- |
| 1. Contract/criteria | Complete | Fields and unknown-preserving rules |
| 2. Discovery | Complete | Bounded shortlist, not exhaustive ecosystem coverage |
| 3. License/access | Complete for research decision | Hosted overrides/data republication rights unresolved; neither adopted |
| 4. Inspection/selection | Complete | Exactly three options tested; import closure reviewed first |
| 5. Practical comparison | Complete within bounded scope | 42/9-ID matches, repeat/paging/conditional checks, adapter/failure probes; long-term/full-site/auth behavior untested |
| 6. Recommendation | Complete | Source combination/fallback; no server built |
| 7. Reproducibility | Complete for research | Versions and relative-path steps recorded; full server not tested |
| 8. Record outcomes | Complete | This report; baseline unchanged |

## 10. Implementation decision — 2026-11-09

After research, the owner explicitly requested that the tool contract be recorded and the minimal version implemented. The original research baseline and observations above remain historical evidence.

Selected: a standalone, small official-SDK stdio interface around the verified RSS + public HTML/JSON-LD path. Reusing the complete MIT candidate-management application would retain unrelated profile/tracker surfaces and require correcting its identity, filtering and status behavior. No collector code was copied. Only Djinni-specific mapping, URL boundaries and two-tool orchestration are new application code; no protocol, XML/HTML, export or comparison library was created.

Components selected before integration: official MCP SDK 2.3.0 (MIT), HTTPX 0.28.1 (BSD-3-Clause), Beautiful Soup 4.15.0 (MIT), defusedxml 0.7.1 (PSF), and Pydantic 2.14.3 (MIT). The SDK supplies protocol/client/schema/error handling; existing parsers handle source documents. See [dependency metadata and primary documentation](dependencies.md), [v0.1 contract](tool-contract.md), and [verification results and limits](verification.md).

Implemented: anonymous `search_jobs` and `get_job`, numeric identity, bounded acquisition/output, explicit errors, source dates and open/closed/unknown evidence. Deferred: private history, scheduling, ranking/reporting, accounts, applications, publication and public-project license selection. These are scope boundaries, not evidence of exhaustive coverage or measured token savings.

## 11. Phase 2 reuse decision — 2026-11-09

The owner authorized a deliberately simple local workflow, superseding the broader draft: questionnaire precedence; explicit CV refresh; saved profile reused across batches; recommendation history, manual exclusions and saved Markdown; no automatic content hash/invalidation, application-status inference or age feature. See [the accepted v0.2 contract](tool-contract-v0.2.md).

Use existing Python sqlite3/json/file operations (PSF-licensed Python; SQLite is public domain) plus the already adopted official SDK and Pydantic (MIT). SQLite availability was verified in the development Python. The earlier phase-2 inspection considered the existing MIT job-assistant profile/database/application repositories; a standalone application dependency or copied architecture is unnecessary for this small schema. New code is limited to project-specific state/tool glue. No new runtime dependency, Markdown parser/exporter, CV parser or external model service is justified.

## 12. Manual-workflow usability correction — 2026-11-09

A real desktop run successfully saved the profile, searched public jobs and saved five recommendations. It exposed an instruction gap: asking only essential criteria omitted the optional CV/achievement invitation, and opt-in drafts were neither enabled nor offered. Correct the existing bundled workflow and server guidance: four-item initial onboarding, explicit draft preference/language and a short draft/offer branch. Existing profile/history/report fields already support this; no new library, tool, database schema or CV read is needed. Also state the existing search limit (1–50) explicitly to avoid observed invalid 100-item requests. Private chat/profile content and real application examples are not copied into tracked artifacts.

## 13. Company context in recommendations — 2026-11-09

The owner requested three sentences about the company and the role's place in its business, followed by five sentences assessing the position and candidate fit. Reuse the existing get_job description and bundled client workflow; no new service, library, copied code or license is involved. The current tool contract already supplies vacancy text and accepts plain-text summaries and Markdown reports. Use only company context stated in the vacancy. Missing context must be marked briefly, without padding, inferred business activities, external searches or company-site visits unless the user explicitly requests research. This is client instruction behavior, not deterministic sentence-count enforcement; source acquisition and storage schemas stay unchanged.

## 14. Candidate experience tense — 2026-11-09

The owner requested experience-based or past-tense candidate wording rather than automatically presenting historical team sizes, achievements and duties as ongoing work. Reuse the existing bundled workflow and server guidance, with no new dependency, copied code, license or schema change. This applies to assessments and application drafts in every language; known completed outcomes stay completed, and ongoing duties require explicit confirmation. Neutral wording must not imply that employment ended. This is a client drafting rule, not an automatic edit of stored profiles or historical reports.

## 15. Pre-publication privacy review — 2026-11-09

The owner requested a privacy review of the proposed GitHub publication, including history. Reuse Git's tracked-file/object inventory and existing Python standard-library read/hash/copy operations (PSF); no scanner dependency, generic scanning library or external data upload is introduced. Dedicated secret scanners were not installed in the inspected environment. Bounded local pattern checks and manual review cover the selected files and reachable history; they are not a proof that every possible secret format is detected. Keep raw findings and candidate data under ignored local/ or temporary storage. Prepare a tracked-files-only publication snapshot without .git, ignored runtime data or original commit identities, preserving the working repository and its private state. Publication still requires a fresh inspection and deliberate choice of non-private Git author metadata.

## 16. Public setup documentation — 2026-11-09

The owner explicitly authorized a public GitHub repository and requested complete installation/connection instructions. Reuse the current Python virtual-environment installation, standard MCP stdio command/environment settings and existing placeholder configuration; no runtime code, dependency or protocol change is needed. Codex registration syntax was checked against the official MCP documentation and locally installed CLI help. Document an explicit persistent DJINNI_MCP_DATA_DIR so client working-directory changes do not create different profiles. Include macOS/Linux and PowerShell commands, expected tool discovery and troubleshooting, distinguishing tested macOS behavior from untested platform instructions. The GitHub plugin provides repository reads and content writes but no repository-creation tool in this session; use the official website for creation and retain safe public author metadata for publication.

## 17. PyPI / uvx release preparation — 2026-11-09

The owner approved the proposed `djinni-mcp` package name (subject to PyPI availability), MIT license and a prerelease for independent Linux testing. The public PyPI JSON endpoint returned 404 for that name during research; this does not reserve the name or prove it can be registered. Publication awaits the owner's PyPI account configuration.

Selected: keep the existing setuptools backend and official MCP SDK; build a normal wheel and sdist with uv, test those artifacts, and publish through GitHub Actions with PyPI Trusted Publishing and publish attestations. No separate development package, custom installer, protocol or exporter is needed. The official [Fetch server](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch) documents the same uvx launch pattern. Sources: [uv tools](https://docs.astral.sh/uv/guides/tools/), [building/publishing](https://docs.astral.sh/uv/guides/package/), [setuptools file selection](https://setuptools.pypa.io/en/latest/userguide/miscellaneous.html), [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/using-a-publisher/). uv is MIT/Apache-2.0; setuptools is MIT; the adopted MCP SDK is MIT. PyPA's publishing action is an existing BSD-3-Clause component ([license](https://github.com/pypa/gh-action-pypi-publish/blob/7245906fb61fa33a13554f9d5fb856fe61758086/LICENSE.md)); retain its upstream action rather than implementing authentication/signing.

For stable data paths, select [platformdirs](https://platformdirs.readthedocs.io/en/latest/api.html), [MIT licensed](https://github.com/platformdirs/platformdirs/blob/main/LICENSE), rather than implementing OS path conventions. Minimal application glue selects the `djinni-mcp` user-data directory while preserving the explicit argument and DJINNI_MCP_DATA_DIR override. Do not scan for or migrate existing private data automatically. Developer tests and release preparation must pass isolated temporary/local data paths.

Use standard-library argparse for --version, zipfile/tarfile for archive inspection, hashlib for manifests and unittest plus the existing SDK Client for package checks. These are Python/PSF components; there is no custom archive/parser/protocol implementation. Build from a reviewed allowlist without private Git history. Include only runtime modules, user package documentation, license and packaging metadata in distributable archives. Inspect both archives and test the installed wheel from outside the checkout. Virtual-environment isolation is not a security sandbox, and a publish attestation identifies the publisher rather than certifying safe code. Cross-platform claims remain limited to actually completed tests.

Release checks reuse detect-secrets 1.5.0 (Apache-2.0, local scan with network verification disabled), pip-audit 2.10.1 (Apache-2.0, known-advisory checks of public dependency names/versions), and PyYAML 6.0.3 (MIT, workflow syntax inspection). Sources: [detect-secrets](https://github.com/Yelp/detect-secrets), [pip-audit](https://github.com/pypa/pip-audit), [PyYAML](https://pyyaml.org/). These development-only tools are not dependencies of the shipped MCP. Scanners supplement manual artifact review; they cannot certify absence of secrets or vulnerabilities.


## 18. Publication provenance verification — 2026-11-09

The owner authorized publication after preparing the PyPI account and explicitly confirmed the narrowly scoped Trusted Publisher: Kiri7z/djinni-mcp-dev, release.yml, environment pypi. The environment permits only v* tags. Publish the reviewed public source snapshot and a matching tag; do not push the laptop repository's private Git history.

For post-upload signature verification, reuse pypi-attestations 0.0.31 (Apache-2.0; development-only) and its existing verify pypi command with the expected repository URL. Do not implement certificate, Sigstore, identity or signature validation ourselves. Primary evidence: [PyPI consuming attestations](https://docs.pypi.org/attestations/consuming-attestations/), [Integrity API](https://docs.pypi.org/api/integrity/), [tool source/license](https://github.com/pypi/pypi-attestations). The CLI is marked experimental upstream; a passing result supports artifact/publisher identity, not absence of malicious code or vulnerabilities. Compare downloaded archive contents and hashes using existing zipfile/tarfile/hashlib checks as a separate source-to-release check. Keep raw downloaded attestations and test artifacts under ignored local/.


## 19. Draft defaults after independent Fedora feedback — 2026-11-09

The owner reported that the published client workflow found vacancies but offered to prepare drafts later. Existing code explicitly instructs the client to offer once when prepare_drafts is unset; absence of draft_language is not a requirement to stop drafting. The Linux profile itself has not been inspected from this workspace, so its saved preference remains unknown.

The owner explicitly selected Ukrainian as the fallback application-draft language. Reuse the existing saved draft_language field, bundled workflow and SDK server instructions. An explicit language in the current request takes priority for that request, then the saved language, then Ukrainian. Mention this default during initial onboarding without requiring a separate language answer or silently editing an existing profile. No new library, model service, schema, protocol, document access or license is needed. The owner subsequently confirmed that an unset prepare_drafts must enable ready drafts by default. Honor explicit per-request instructions first; otherwise preserve a saved refusal or selected language. Defaults are client guidance, not invented questionnaire answers or a profile migration.

Client wording is instruction-driven, not deterministic model execution. Existing SDK and state tests can check that guidance is exposed and explicit preferences remain stored, but cannot prove that every AI client follows the prose. Keep this limitation visible in release acceptance.


The owner also requested an update lifecycle. Reuse the already verified tag-triggered GitHub release workflow: reviewed public source commit and matching new package version/tag, then build, six platform/Python checks and Trusted Publishing to PyPI. No new service, dependency, credentials or custom release framework is needed. Normal commits do not upload a package, private laptop history is never automatically pushed, and existing PyPI versions are not overwritten. Users change the pinned argument and restart MCP; instruction changes also require a fresh chat or get_workflow refresh. The current storage schema/data directory remains compatible.


## 20. Stable release and unknown-status presentation — 2026-11-09

The owner confirmed that 0.3.0rc2 works in the independent Fedora client, requested a normal stable release without preview/testing text in the user description, and reported repetitive unknown status labels. Select stable version 0.3.0, retaining the existing uv/setuptools/official-SDK/Trusted Publishing release path and licenses. No new tool, library, service, protocol, parser or storage schema is needed.

Inspection confirms that RSS summaries deliberately carry unknown activity, while get_job can return open/closed only when its existing public-page evidence is sufficient (matching JobPosting plus apply UI, or the explicit closed notice). Do not remove uncertainty from the raw contract or claim unknown means open. Use get_job rather than the RSS placeholder for any displayed status. Omit unknown activity labels from normal chat/Markdown recommendations, but retain confirmed statuses and transparent detail-fetch failures; preserve existing unknown salary/location/date behavior. Reuse the bundled workflow and SDK instructions for this presentation change; do not expand source-detection heuristics on unverified assumptions.

Keep historical release/verification notes in developer documentation. The shipped package description and connection guide should focus on normal installation/use and meaningful source/privacy limits, not development-phase commentary. Run existing source/state/protocol checks, review the selected source before building and both archives afterward, and publish only through the tested tag pipeline. Client rendering remains model-driven and requires normal client acceptance after instruction refresh.
