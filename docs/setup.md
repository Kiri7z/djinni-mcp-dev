# Connect Djinni MCP

A local MCP client starts this server on your computer. No Djinni account, API key or source checkout is required.

**Preview version:** 0.3.0rc2, with ready Ukrainian application drafts enabled by default. Local package checks passed on macOS with Python 3.11 and 3.14. Independent Linux acceptance is pending; see verification-v0.3.md for completed automated checks and their limits.

## 1. Install uv once

Use the [official uv installation instructions](https://docs.astral.sh/uv/getting-started/installation/) for your OS. Confirm in a terminal:

```sh
uvx --version
```

uv can obtain a compatible Python when needed under its normal download policy. Initial setup requires network access to obtain the package, dependencies and possibly Python. Searches require access to public djinni.co pages.

## 2. Connect your MCP client

For clients with an mcpServers configuration section, merge this entry into the existing configuration:

```json
{
  "mcpServers": {
    "djinni": {
      "command": "uvx",
      "args": ["djinni-mcp@0.3.0rc2"]
    }
  }
}
```

Other clients may use separate command/arguments fields. Select local/stdio transport, command `uvx`, and argument `djinni-mcp@0.3.0rc2`. Preserve unrelated server settings. A hosted-URL-only client cannot launch a local stdio process.

If the client cannot find uvx, enter its full executable path. Find it with `command -v uvx` on macOS/Linux or `(Get-Command uvx).Source` in PowerShell. Restart/refresh the MCP connection after saving. Keep your actual client configuration private.

## 3. Start a search

Expected tools: get_workflow, get_profile, update_profile, search_jobs, get_job, get_history, save_search and set_job_excluded.

Ask in your preferred language:

> Use Djinni MCP to find five suitable jobs. Read the workflow and my saved profile first. Ask for missing preferences, offer optional CV and achievement details, and include a ready Ukrainian application draft for each suitable job unless I decline. Save the recommendations and report. Do not send applications.

The AI client does matching and writes assessments. A CV is read by that client only when you request it; the server never opens CV files. Later you can ask for more jobs using the saved profile, change individual preferences, or exclude a vacancy explicitly.

## Data and updates

| OS | Default private data folder |
| --- | --- |
| macOS | `~/Library/Application Support/djinni-mcp` |
| Linux | `$XDG_DATA_HOME/djinni-mcp`, or `~/.local/share/djinni-mcp` when unset |
| Windows | `%LOCALAPPDATA%/djinni-mcp` |

The folder holds state.sqlite3 and reports/ and is independent of the working directory, release version and uv cache. Reads of an empty profile do not create it. Back up the folder while the MCP process is stopped.

Optional: set the environment variable DJINNI_MCP_DATA_DIR in your MCP client to a private absolute directory. Existing source-install users should retain that setting to reuse their existing data. There is no automatic search for old data or migration. A first packaged run may therefore show an empty profile until you explicitly select the old data directory.

Update by changing the configured package version and restarting the connection. For changed workflow instructions, start a new chat or explicitly ask the client to read get_workflow again; an existing conversation may retain the earlier guidance. Pinned versions avoid implicit application upgrades; dependencies are still resolved from the package requirements. Do not reset your data or reread your CV merely to update the program.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| uvx not found | Install uv, restart the client, or use the full uvx executable path. |
| Version not found | Check the configured version and PyPI/network availability; prereleases must be selected explicitly. |
| Manual launch waits silently | Expected: it waits for an MCP client. Ctrl+C stops a manual run. Use --version for a non-server check. |
| Profile appears empty | Compare DJINNI_MCP_DATA_DIR and the default data folder across clients; do not overwrite old data. |
| Missing tools or old guidance | Restart/refresh the MCP connection; expect eight tools. |
| Installation fails | Check network access and the exact Python/dependency error; do not silently bypass dependencies. |
| HTTP 403/timeout | Public Djinni access can fail or change. Failure does not prove no jobs exist or a vacancy closed. |
| Fewer results than requested | RSS coverage is bounded/unknown and explicit local exclusions can reduce the result count. |

Source inspection and development instructions are in [development.md](development.md). Release preparation and PyPI account linking are in [release.md](release.md).

Candidate data is returned to the chosen AI client and may be processed by its provider. It is not submitted to Djinni by this implementation. SQLite is not encrypted; uvx dependency isolation is not an OS security sandbox. Do not attach populated data folders, CVs, real client configurations or credentials to issues.

Application drafts are included by default in Ukrainian. To change this, request another draft language or opt out explicitly; the client can save that preference. A language chosen for the current request takes priority over the saved draft language. Changing the chat/report language alone does not change the Ukrainian fallback. No application is sent automatically.
