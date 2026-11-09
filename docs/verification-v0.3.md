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
