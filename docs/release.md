# Package release procedure

This is maintainer documentation. Users only need [setup.md](setup.md).

## Release identity

- PyPI project: `djinni-mcp` ([PyPI releases](https://pypi.org/project/djinni-mcp/)).
- Console command: `djinni-mcp`.
- Public source: `Kiri7z/djinni-mcp-dev`.
- Current stable package version: `0.3.0`.
- Required matching source tag: `v0.3.0`.
- License: MIT, with a project/contributors identity and no personal email metadata.

The source repository is not a separate runtime dependency. Installable archives contain runtime Python modules, package metadata, the MIT license and the user-facing package description. Developer instructions, agent files, tests, private data and Git history are excluded by the distribution allowlist.

## Preparation record — 2026-11-09

At the end of local preparation: PyPI upload, source tag, remote workflow execution and account link were still pending. Publication has since completed through the tagged GitHub workflow; see [verification-v0.3.md](verification-v0.3.md#publication-verification--2026-11-09) for file hashes, CI and signature checks. The source release must be tied to a reviewed public commit before publication. macOS checks and their limits are recorded in [verification-v0.3.md](verification-v0.3.md); the owner's independent Linux acceptance comes after the prerelease upload. Do not describe pending CI jobs as platform test results.

## Prepare and inspect

Use the existing source development environment or a separate temporary environment with uv and twine. From the repository root:

```sh
uv build --no-sources --out-dir local/release/dist
python scripts/check_dist.py local/release/dist --tag v0.3.0
python -m twine check --strict local/release/dist/*
```

Use only reviewed source files. A fresh source snapshot without `.git`, `local/`, virtual environments or AGENTS.md is preferable on a developer laptop. The artifact checker uses a project-specific file allowlist and rejects personal absolute paths, email addresses, unexpected modules/metadata, version mismatches and links/special files. It prints per-archive SHA-256 hashes and inventories. It does not replace a secret scanner or manual review.

Run a local detect-secrets scan with `--no-verify` on the selected source and safely unpacked archives. Review findings privately; do not upload candidate data to scanners or issues. Audit the resolved public dependency names/versions using pip-audit. A clean scan is evidence, not a security certification. Do not use editable source installation as the only package test.

Install the built wheel in a fresh environment, run `python -m unittest discover -s tests -v` against that installed package, and run `python -m pip check` (or uv pip check). `tests/package_smoke.py` accepts `--` followed by an installed server/uvx command. It starts two real MCP processes in different working directories with temporary synthetic data, verifies eight tools and saved profile/history/exclusions, and checks the Markdown copy. Pass an absolute wheel path when testing uvx, because the test deliberately changes the child's working directory. Also verify the source archive installs through uvx and `--version` matches the wheel.

Any runtime/package-readme/metadata change invalidates the archive review: rebuild, inspect and retest the resulting artifacts. Development-only documentation changes do not alter the distribution payload, but any new public source snapshot still requires a privacy review.

## Link the owner's PyPI account

After registration, email confirmation and 2FA, open [PyPI Publishing settings](https://pypi.org/manage/account/publishing/). Add a pending GitHub Trusted Publisher with:

| Field | Value |
| --- | --- |
| PyPI project name | `djinni-mcp` |
| GitHub repository owner | `Kiri7z` |
| GitHub repository name | `djinni-mcp-dev` |
| Workflow filename | `release.yml` |
| GitHub environment | `pypi` |

In that GitHub repository, create environment `pypi` and restrict deployment branches/tags to the intended release tags. An owner review gate is recommended if available for this repository. Account configuration is separate from application code; no login password, recovery code or permanent PyPI token belongs in files or chat. Configure through the owner's authenticated account session.

The [official PyPI guide](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/) explains pending publishers. Creating one does not reserve the package name. If the name cannot be registered, agree on a replacement and update metadata, docs, workflow and checks before rebuilding.

## Public source and workflow

Publish only the reviewed source snapshot using a deliberate public/no-reply commit identity. Do not push the original private local Git history. Attach the matching release tag to the reviewed public commit, never an unrelated working branch.

The prepared `.github/workflows/release.yml` uses commit-pinned existing actions. A manual workflow run on main builds/verifies without publishing. A matching `v*` tag triggers:

1. Build wheel and sdist; check tag/version, metadata and exact artifact contents.
2. Test the same wheel on macOS, Ubuntu and Windows with Python 3.11 and 3.14, including real uvx MCP exchanges and sdist installation.
3. Publish only after all checks pass, from the `pypi` environment, using a separate job with only `id-token: write`, no source checkout and no permanent credential.

The PyPA publishing action produces PyPI publish attestations. These verify publisher identity/workflow for a file digest; they do not certify harmless code or a reproducible build. Users can inspect the readable Python in the actual wheel and compare it with the tagged source. Optional stronger build/source attestations can be considered separately; no custom signing system is implemented.

After upload, verify the PyPI project metadata, source link, file hashes, version, license and provenance display. Then perform a genuinely fresh PyPI `uvx djinni-mcp@0.3.0 --version` and MCP smoke test rather than a local-file/cached-only test. Keep the selected version pinned in the client configuration. Publish stable releases without GitHub's pre-release label after the owner's acceptance; an MCP Market listing is separate work.


## Update lifecycle

A normal source commit does not publish a package. Review changes and privacy, assign a new package version, update its connection examples, publish the reviewed public commit, then create the matching vVERSION release tag. The existing workflow builds and tests that tag and uploads a new PyPI version only after all jobs pass. Existing PyPI release files are not overwritten and the workflow does not skip a version conflict silently.

Users pin the desired version in their MCP arguments and restart the server after changing it. For bundled workflow/instruction changes, begin a new chat or explicitly read get_workflow again, because an existing conversation may retain the older instructions. Keep the same data directory; a code update does not require a CV refresh or re-entering a profile. Future storage-schema changes require their own compatibility review; the 0.3.0rc2 draft-default update has no schema change. No background updater or automatic push of the private laptop repository is configured.
