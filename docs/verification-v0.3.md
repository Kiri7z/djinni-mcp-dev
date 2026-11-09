# Package candidate 0.3.0rc1 verification

Checked locally on 2026-11-09. This records completed checks, not future CI or independent acceptance.

## Completed

| Check | Result |
| --- | --- |
| Installed wheel, Python 3.14.7 / macOS arm64 | 27 unittest cases passed; dependency compatibility passed |
| Installed wheel, Python 3.11.18 / macOS arm64 | 27 unittest cases passed; dependency compatibility passed |
| Real stdio from installed package | Eight tools; synthetic profile, Markdown, history and exclusions survived a second process in a different working directory |
| Real uvx launch from local wheel | Passed on both tested Python versions; no editable checkout dependency |
| uvx source archive installation | Passed with isolated setuptools build; --version reports 0.3.0rc1 |
| Cold uvx cache | Downloaded public dependencies and started the local wheel successfully |
| Source and final archive secret scans | detect-secrets 1.5.0, --no-verify; no findings in selected package source/final unpacked archives |
| Artifact contents | Exact allowlist passed; wheel has 12 files, source archive has 13; no personal paths/emails, CV, database, private report, Git history, development instructions or tests |
| Negative artifact checks | A deliberately added AGENTS.md and a synthetic personal absolute path were rejected |
| Package metadata | twine 7.0.0 --strict passed for both archives; matching distribution/runtime/tag version, source URL and MIT license |
| Dependency advisory audit | pip-audit 2.10.1 checked 35 resolved public dependency names/versions; no known vulnerabilities found at check time |
| Bounded live public-source check | One anonymous RSS search returned two jobs; three detail pages checked; coverage remains unknown |
| Release workflow | YAML parsed and shell syntax checked locally; remote workflow has not run |

The separate 36-file public source snapshot was also scanned. Its one credential-shaped finding is a synthetic URL in a negative test that verifies such input is rejected before any request; it is not a real credential and is excluded from both distribution archives.

Only runtime code, package metadata and the user-facing description are shipped. No authentication token or candidate data was used in tests. Test state and release artifacts are isolated under ignored local/ or temporary directories. The final description update did not change runtime modules; the rebuilt final archives were reinspected, metadata-checked and exercised through uvx.

## Candidate artifact identity

These hashes identify the local reviewed candidate, not a PyPI publication. Any rebuild (including a package description edit) may change them and requires fresh artifact inspection. The eventual CI-built/uploaded files must be identified separately.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `djinni_mcp-0.3.0rc1-py3-none-any.whl` | 20201 | `ee51c6a2b78f0310303e71b64bf55404c3e03665f67dd32aca51c5d9e0d522c6` |
| `djinni_mcp-0.3.0rc1.tar.gz` | 17792 | `87d65e3b89258f0130a940731e6807bdc8a148b3f07cf208e9f9d783a80806ab` |

Raw manifests, scanner output, dependency resolution, installation environments and live observations remain under ignored local/release/0.3.0rc1/. They are not included in the archives or public source snapshot.

## Pending and limits

- PyPI ownership/name acceptance, Trusted Publisher registration and GitHub pypi environment configuration.
- Publication of the reviewed source changes and matching tag; GitHub workflow execution and all six OS/Python matrix results.
- A clean install by package name from PyPI rather than a local archive.
- The owner's independent Linux acceptance, Windows execution and a stable release/MCP Market listing.
- PyPI publisher attestations are prepared in the workflow but do not exist until a real publication.

A source archive README warning from setuptools is nonfatal: the intentionally excluded developer README is replaced by the declared docs/package-readme.md, which is present in both sdist and distribution metadata. Strict PyPI metadata validation passed. Open source, clean scanners and known-advisory checks are not guarantees that all vulnerabilities or secrets are absent. uvx environments isolate dependencies, not OS permissions; top-level version pinning does not freeze every transitive dependency.


## Publication verification — 2026-11-09

This section supersedes the pending publication/automated-platform items in the local preparation record above. Independent owner acceptance remains pending.

- Source/tag: [v0.3.0rc1](https://github.com/Kiri7z/djinni-mcp-dev/releases/tag/v0.3.0rc1), commit bdf42ba1a4ad02adffd566a9469110b0f0ba57bc. The 36-file public tree matched the reviewed snapshot. Author and committer use GitHub's no-reply address; the laptop's private Git history was not pushed.
- [Main validation](https://github.com/Kiri7z/djinni-mcp-dev/actions/runs/42651940048) passed all six macOS/Ubuntu/Windows + Python 3.11/3.14 jobs. Logs confirmed 27 unittest cases and real uvx stdio checks per environment, plus sdist installation.
- [Tagged release workflow](https://github.com/Kiri7z/djinni-mcp-dev/actions/runs/42652422517) passed its build, six verification jobs and PyPI publish job. The pypi environment permits v* tags only. No permanent PyPI API token was configured.
- [PyPI 0.3.0rc1](https://pypi.org/project/djinni-mcp/0.3.0rc1/) contains the wheel and sdist, MIT metadata and the correct source link. Both files were downloaded from PyPI and their SHA-256 hashes matched the tagged CI artifacts exactly. Runtime module hashes matched the reviewed source; the CI artifacts also passed allowlist, personal-path/email, secret-scan and strict metadata checks.
- pypi-attestations 0.0.31 cryptographically verified both downloaded files using the expected GitHub repository. PyPI provenance identifies Kiri7z/djinni-mcp-dev, release.yml, environment pypi. This verifies publisher provenance, not absence of vulnerabilities.
- A fresh-cache, by-name `uvx djinni-mcp@0.3.0rc1 --version` downloaded from PyPI and reported 0.3.0rc1. A separate fresh-cache MCP client launch by package name passed eight-tool discovery, synthetic profile/history/exclusion/report checks and persistence across processes/working directories. No local --from archive was used in these post-publication checks.

An extra offline-only probe initially lacked a wheel for the interpreter selected under the MCP client's environment. The ordinary network-enabled first-run test above passed; offline first installation is not promised. Runtime source was not changed to work around the test environment.

### Published file identity

| PyPI file | SHA-256 |
| --- | --- |
| `djinni_mcp-0.3.0rc1-py3-none-any.whl` | `59ec1bd884942e567ba2dfbc7005f7376e015c953ad74358c95fb548f6637a43` |
| `djinni_mcp-0.3.0rc1.tar.gz` | `0fe6a9a9b818474c15387eaea422814907040831a1196fa7dc5a0d388891af34` |

Remaining: the owner's independent Linux PC test, any additional client/Windows manual acceptance, stable release and MCP Market listing. Automated Linux CI does not replace the independent test. Raw API/provenance/signature logs and the publication receipt remain under ignored local/release/0.3.0rc1/.


## 0.3.0rc2 draft-default update — local preparation, 2026-11-09

Independent Fedora feedback confirmed that 0.3.0rc1 installed, collected the CV/conditions and found three vacancies, but offered to prepare messages later. This is consistent with the former unset-preference offer branch; the actual Linux profile was not accessed here. The owner selected ready drafts by default and Ukrainian as the fallback language.

The existing workflow and server guidance now include an actual 3–5-sentence message per suitable vacancy without another confirmation when preferences are unset. Explicit per-request instructions take priority, then saved prepare_drafts/draft_language, then enabled/Ukrainian defaults. A saved opt-out is retained. Chat/report language does not determine the draft fallback. No storage schema, candidate data, source collector, dependencies or automatic sending behavior changed.

Local validation: 27 existing tests passed; built wheel/sdist passed exact artifact/metadata/privacy checks; uvx real-stdio checks passed with Python 3.11 and 3.14. The actual get_workflow response exposed the new defaults, reading an empty profile did not fabricate settings, and explicit no/English settings persisted across processes. These checks validate transport/state/guidance exposure; they do not simulate or guarantee the AI client's final drafted prose. Retest the drafted output in a new chat or explicitly reload get_workflow after changing package version and restarting MCP. Release CI, PyPI publication and end-user draft acceptance are pending at this preparation point.
