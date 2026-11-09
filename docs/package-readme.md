# Djinni MCP

Find public Djinni jobs from a local MCP client, keep your search preferences, and save recommendations without repeatedly entering your profile.

## Connect

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) once. In an MCP client that supports local stdio servers and `mcpServers` configuration, add:

```json
{
  "mcpServers": {
    "djinni": {
      "command": "uvx",
      "args": ["djinni-mcp@0.3.0"]
    }
  }
}
```

The client starts the server; uvx obtains the package, compatible Python if needed under uv's normal download policy, and dependencies. No Git clone, manual virtual environment, Djinni account, API key or separate development package is required. If the client cannot find uvx, use its full executable path. Other clients may use a different configuration format.

Restart the MCP connection and ask:

> Use Djinni MCP to find five jobs for me. Read the workflow and my saved profile first. Ask for missing preferences, offer an optional CV and achievements, and include a ready Ukrainian application draft for each suitable job unless I decline. Save the recommendations. Do not send applications.

## What it does

- Searches public Djinni vacancies and reads their public details.
- Reuses your explicitly saved profile, labels previous recommendations and supports manual exclusions.
- Saves recommendation history in SQLite and readable Markdown reports.
- Supplies guidance for company context, candidate fit and ready drafts to your AI client.

Your AI client performs matching and writes summaries. Company context comes from vacancy text; external company research requires your request. Search covers publicly accessible vacancies and may not include every listing. Remote vacancies may still restrict eligible countries.

## Your data

Your profile and search history are stored locally when you ask the client to save or update them. Default data folders are:

| OS | Default location |
| --- | --- |
| macOS | `~/Library/Application Support/djinni-mcp` |
| Linux | `${XDG_DATA_HOME:-~/.local/share}/djinni-mcp` |
| Windows | `%LOCALAPPDATA%\djinni-mcp` |

The folder contains `state.sqlite3` and `reports/`. It is independent of the source checkout and uv cache. Set `DJINNI_MCP_DATA_DIR` to a private absolute directory if you want a different location; keep it stable across clients and updates. To reuse an older source installation's profile, point this variable at its existing data directory. Existing data is never searched for or migrated automatically.

There is no Djinni account access, document scanning, automatic application sending or background job. The server does not read CV files itself. Saved candidate facts are returned to your chosen AI client and may be processed by its provider. SQLite is ordinary local storage, not an encrypted vault. uvx isolates dependencies, not operating-system permissions.

## Inspect and troubleshoot

Expected tools: `get_workflow`, `get_profile`, `update_profile`, `search_jobs`, `get_job`, `get_history`, `save_search`, `set_job_excluded`.

`uvx djinni-mcp@0.3.0 --version` prints the release version. Starting without arguments waits for an MCP client; it is not an interactive terminal interface.

The [public source repository](https://github.com/Kiri7z/djinni-mcp-dev) contains the implementation and tests. Published wheels contain readable Python source; download and inspect the actual release as well as its source tag. Open source and provenance records help review but do not guarantee safety. The code is MIT licensed; dependency licenses and Djinni content are separate.

See [connection and troubleshooting](https://github.com/Kiri7z/djinni-mcp-dev/blob/main/docs/setup.md). Report problems using synthetic examples, without CVs, populated data folders, credentials or personal paths.

Application drafts are included by default in Ukrainian. To change this, request another draft language or opt out explicitly; the client can save that preference. A language chosen for the current request takes priority over the saved draft language. Changing the chat/report language alone does not change the Ukrainian fallback. No application is sent automatically.

Vacancy status is shown only when confirmed by the public detail page. Unavailable status is omitted from recommendations instead of repeating an unknown-status label.
