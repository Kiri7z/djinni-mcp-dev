# Publication privacy boundary

Publish the reviewed source snapshot, not the developer's workspace or private data directory. The working Git repository may contain personal author/committer metadata even when every source file is clean. Original Git history and tags must not be pushed without a separate metadata review.

## Intended public contents

- Project source, synthetic tests, dependency declarations and lock snapshot.
- Project documentation and placeholder MCP/profile examples.
- .gitignore without host-specific configuration.

## Excluded contents

- Local AGENTS.md development instructions; these are not required to run or connect the MCP server.

- .git and its original history, identities, remotes, hooks, logs and local configuration.
- local/, including candidate profiles, CV facts, SQLite databases, reports, audit details, HTTP captures and release preparation artifacts.
- Virtual environments, caches, generated package metadata and build outputs.
- Actual MCP client configuration, environment files, credentials, browser sessions and user documents.
- Files from the parent workspace or other directories on the developer's computer.

## Reviewed snapshot

The local publication snapshot is assembled from an explicit source/documentation allowlist that excludes local AGENTS.md. It contains current saved edits, rather than only the last commit. No recursive copy of the workspace or private directories is used. Its per-file SHA-256 manifest is stored beside the snapshot, outside the public payload. Any later source change makes that snapshot stale and requires regeneration/review.

The 2026-11-09 review checked 26 previously tracked file paths, all reachable historical blobs in seven commits and commit/tag metadata. No candidate documents, personal host paths or actual credentials were found in source contents. A URL slug resembling a token and a synthetic URL containing test credentials were false positives. Personal commit identities were found; the snapshot excludes all original Git metadata. Raw findings remain private.

Local pattern checks and manual review cannot prove the absence of every possible secret. Git ignores are a preventive measure, not protection for already tracked files or old commits. Do not use git add -f for private paths. For a new public repository, initialize only the reviewed snapshot and explicitly set a public project identity or a reviewed GitHub no-reply identity before creating any commits. Avoid broad git push --mirror or --all from the working repository.

## Runtime data boundary

The server reads explicit local profile/history files and fetches public Djinni job routes. It does not scan the user's documents or import a CV itself. Candidate facts and reports are deliberately returned to the connected AI client; they are not sent to Djinni by this implementation. They may still be processed by that AI provider. Source publication must not include a populated data directory. The .gitignore rules cover private runtime files, documents and credential artifacts but cannot prevent users from explicitly publishing their own private data.

## Before the actual push

Inspect the staged file list and the new repository's commit author/committer metadata. Recheck the final tree for private documents, absolute user paths and credentials. Ensure the published tree matches the reviewed manifest or repeat the review for changes. No publication was performed as part of this privacy review.
