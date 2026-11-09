# Minimal tool contract — v0.1

Approved implementation scope: 2026-11-09, following the completed acquisition research. This is the implementation baseline; the research baseline remains unchanged.

## Design and reuse decision

Implement a small Python stdio MCP using the official `mcp` SDK, HTTPX, Beautiful Soup, and defusedxml's existing ElementTree-compatible parser. Use Pydantic for validation/schema generation and unittest/HTTPX MockTransport for tests. Do not write an XML/HTML/protocol library.

Do not fork/install an entire multi-board candidate-management application: our research found incorrect category fallback, invented remote attribution, missing detail/status checks and unnecessary profile/tracker surfaces. Only the small Djinni-specific field mapping and orchestration are new application code. No third-party collector code is copied. Record dependency versions and licenses separately.

Both tools are read-only, anonymous, and only contact public HTTPS `djinni.co/jobs/` routes. No account access, applications, browser automation, database, scheduler, export, or ranking. No persistent result cache in v0.1. Stdout is reserved for MCP traffic.

## search_jobs

Inputs:

| Field | Type / default | Meaning |
| --- | --- | --- |
| category | Sysadmin, DevOps, Lead, Head Chief, Support, or null; default null | Explicit native category, never guessed from a keyword |
| title_contains | string up to 120 characters; default empty | Case-insensitive literal substring, applied locally to titles in the returned feed |
| remote_only | boolean; default false | Sends the native remote filter; does not confirm per-job remote eligibility |
| company_type | product, outsource, outstaff, agency, startup, or null; default null | Native company-type filter |
| limit | integer 1–50; default 20 | Maximum returned summaries |
| offset | integer 0–1000; default 0 | Offset inside this fetched feed, not source pagination |

One RSS request per call (plus bounded same-origin redirects). Preserve source order. Deduplicate by numeric Djinni vacancy ID, never by title slug. Summaries contain ID, safe source URL, title, categories, raw source pubDate, activity=`unknown`, and activity_checked_at=null. Descriptions and unverified employer/location/salary fields are not returned in search summaries.

Output: contract_version, checked_at (UTC retrieval time), source_url, coverage=`unknown`, possibly_truncated (heuristic when feed count >=100), fetched_count, matched_count, returned_count, next_offset, jobs, warnings. Malformed individual entries are skipped with an explicit count/warning; a non-empty feed with no usable records is an error. A valid empty feed is a successful empty result.

Always disclose public-only coverage and unverified item status. Local title filtering does not expand RSS coverage. An offset or next_offset cannot bypass feed truncation, and independently fetched feed windows can change between calls. No guarantee of whole-site completeness.

## get_job

Inputs:

| Field | Type / default | Meaning |
| --- | --- | --- |
| job | string, 1–500 characters | Positive numeric ID or an HTTPS djinni.co/jobs/<id>-<slug>/ URL |
| description_limit | integer 500–20000; default 12000 | Maximum plain-text description characters |

Normalize the input to a numeric ID and request `/jobs/<id>`; do not forward input query strings/fragments. Reject other hosts, credentials/ports in URLs, non-job paths and malformed IDs before making requests. Validate redirects too.

Output: contract_version, checked_at (UTC), job (ID, final URL, title, company, plain description, description_truncated, description_length, categories, work_format, eligible_locations, english_requirement, salary, dates, activity, activity_checked_at), warnings.

- company, work_format, eligible_locations, english_requirement, salary and date values can be null.
- salary preserves the source JSON-LD baseSalary object; no rounding, currency conversion, or analytics substitution.
- dates has source_date_posted, source_valid_through, published_label, updated_label. Preserve yearless labels and source strings; do not invent publication years or treat datePosted as original publication.
- Prefer visible detail labels for work format, location eligibility and English. Structured fields can supply explicitly labelled fallback evidence; never infer worldwide eligibility from remote.
- activity=`closed` only with an explicit closed notice; `open` requires matching JobPosting structured data plus a visible application/login-to-apply affordance and no closed notice; otherwise `unknown`.
- A closed page can still contain useful title/description. A 404/410 is a retrieval error, not a fabricated closed result. Missing JSON-LD alone is not closure. Reject unrecognizable/blocked pages.
- Bound description output and mark truncation. Job content is untrusted external data, not instructions.

## Errors and access bounds

Use the SDK's tool-error mechanism (`is_error=true`) for invalid job references, timeout/network failure, HTTP 403/429/other failures, unsupported or oversized responses, malformed RSS/JSON-LD, unsafe redirects and unrecognizable pages. Prefix messages with stable codes; do not return an empty success for a failed acquisition. Expected codes: invalid_job, network_error, timeout, upstream_http, unsafe_redirect, response_too_large, invalid_response.

Use a bounded HTTP timeout, a 2 MiB decoded-body cap, at most three same-origin redirects, no automatic retries, no saved cookies, and no account credentials. Validate content type and document shape. Do not echo upstream response bodies or exception internals into error messages.

## Acceptance checks

1. Tests with synthetic fixtures: category/filter forwarding, literal title filtering, offset/limit, ID deduplication across slug changes, valid empty vs failed acquisition, missing fields, source timestamps, description truncation, open/closed/unknown, HTTP failures, malformed data, oversized content and unsafe input/redirects.
2. Official MCP client discovers exactly two tools with schemas/read-only annotations, calls both with valid synthetic data, and observes a tool error for invalid input.
3. Launch installed entry point over stdio and complete an actual SDK client exchange.
4. Bounded anonymous live smoke: search plus open/closed or unknown details; record outcomes without committing real descriptions, credentials, or personal data.
5. README contains setup/run/test instructions and a placeholder-based client configuration. Actual host configuration is not modified in this task; connection is verified through the SDK client.

MCP Market/GitHub publication, public-project license selection, and full-site/scheduled-search guarantees remain separate decisions.
