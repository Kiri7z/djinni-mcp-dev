# Source development setup

This is a local stdio MCP server: your AI client launches a Python process on your computer and calls its tools. It is not a hosted HTTP service or a Djinni account integration.

## Requirements

- Git and Python 3.11 or newer, including pip and venv.
- A local MCP client with stdio support.
- Access to PyPI for installation and to public djinni.co pages for searches.

Tested: Python 3.14.7 on macOS. Windows/Linux instructions below are setup guidance, not platform acceptance claims. The constraints file records the tested dependencies, not a hash-verified cross-platform lock. These are developer instructions. End users should use the uvx setup in setup.md once the package is published.

## 1. Install from source

Run in a terminal in the directory where you keep projects.

### macOS or Linux

```sh
git clone https://github.com/Kiri7z/djinni-mcp-dev.git
cd djinni-mcp-dev
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -c requirements.lock.txt -e .
.venv/bin/python -m pip check
DJINNI_REPO="$(pwd -P)"
DJINNI_DATA_DIR="$HOME/.local/share/djinni-mcp"
mkdir -p "$DJINNI_DATA_DIR"
printf '%s\n' "$DJINNI_REPO/.venv/bin/djinni-mcp" "$DJINNI_DATA_DIR"
```

The last command prints the executable and private data paths for the next step. Keep the repository in place: this editable installation depends on its source folder. No virtual-environment activation is needed when using the full executable path.

### Windows PowerShell

```powershell
git clone https://github.com/Kiri7z/djinni-mcp-dev.git
Set-Location djinni-mcp-dev
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -c requirements.lock.txt -e .
.\.venv\Scripts\python.exe -m pip check
$DjinniRepo = (Get-Location).Path
$DjinniDataDir = Join-Path $env:LOCALAPPDATA "djinni-mcp"
New-Item -ItemType Directory -Force -Path $DjinniDataDir | Out-Null
Write-Output (Join-Path $DjinniRepo ".venv\Scripts\djinni-mcp.exe")
Write-Output $DjinniDataDir
```

Check that the selected Python is at least 3.11. These commands do not require changing PowerShell execution policy.

## 2. Connect one MCP client

Use absolute paths, replacing placeholders with the values printed above. Do not put cd, source or export into the executable field. This server has no HTTP endpoint or OAuth login.

### Codex CLI

From the same terminal where the variables above were set:

```sh
codex mcp add djinni --env "DJINNI_MCP_DATA_DIR=$DJINNI_DATA_DIR" -- "$DJINNI_REPO/.venv/bin/djinni-mcp"
codex mcp get djinni
```

PowerShell equivalent:

```powershell
codex mcp add djinni --env "DJINNI_MCP_DATA_DIR=$DjinniDataDir" -- (Join-Path $DjinniRepo ".venv\Scripts\djinni-mcp.exe")
codex mcp get djinni
```

Restart or refresh the client connection. If djinni is already registered, inspect its configuration first and update that entry instead of creating another data directory. The command syntax follows [official Codex MCP documentation](https://developers.openai.com/codex/mcp) and was checked against local CLI help. This option requires the codex command; other desktop clients may have their own settings.

### Desktop clients with MCP settings

Create a local/stdio entry; labels vary by client/version:

| Field | Value |
| --- | --- |
| Name | djinni |
| Transport | stdio / local process |
| Command | Full executable path from step 1 |
| Arguments | None |
| Environment | DJINNI_MCP_DATA_DIR = full private directory from step 1 |

For clients using mcpServers JSON, use the full executable path above rather than the uvx entry in [examples/mcp.json](../examples/mcp.json) into the existing client configuration, preserving unrelated servers. Replace both absolute path placeholders. On Windows use forward slashes in JSON paths or escape backslashes. Keep actual client configuration private.

No working-directory setting is needed with an explicit DJINNI_MCP_DATA_DIR. Without it, storage uses the persistent platform-specific user-data folder described in setup.md. For isolated development and tests, explicitly select an ignored local/ or temporary directory.

## 3. Verify the connection

The client should discover **eight tools**: get_workflow, get_profile, update_profile, search_jobs, get_job, get_history, save_search and set_job_excluded.

Ask your AI client, in your preferred language:

> Use Djinni MCP. Read get_workflow and get_profile. If my profile is empty, ask for target roles, experience, languages, location, work format and minimum salary. Offer optional CV and achievement details, and ask whether I want application drafts. Save my answers, find five suitable jobs, describe the company and role, assess the fit and gaps, and save the report. Do not send applications.

Version 0 for an empty profile is expected. The server never opens a CV itself: if you request an import, the client reads the attachment and saves selected facts.

For a quick public-source check, ask the client to call search_jobs with:

```json
{"category":"Sysadmin","remote_only":true,"limit":5}
```

Use get_job on returned IDs before assessing activity or eligibility. Acquisition failures are errors/unknowns, not proof of zero jobs.

## 4. Use and retain your profile

Later requests can be short:

- "Find five more using my saved profile."
- "Change only my minimum salary to EXAMPLE AMOUNT monthly net."
- "Include short application drafts in Ukrainian."
- "Do not suggest vacancy EXAMPLE_ID again." (Replace with a returned numeric ID.)
- "I attached a new CV; refresh the saved CV facts."

Each recommendation has three sentences about the company and role when the vacancy supplies that information, then five about the position and candidate fit. Missing company context is marked briefly; external company research requires an explicit request. Drafts describe completed work in the past or use experience-based wording. Drafts and exclusions are explicit choices.

The private data directory contains state.sqlite3 (profile, history, exclusions and saved output) and reports/ (Markdown copies). Only selected recommendations are saved, not every fetched vacancy. Retain the data-directory setting across updates. There is no document watcher, automatic application sending or background schedule.

## 5. Update and test

Stop the MCP connection before updating, run from the repository directory, then restart the connection:

```sh
git pull --ff-only
.venv/bin/python -m pip install -c requirements.lock.txt -e .
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m pip check
```

On Windows use .\.venv\Scripts\python.exe instead of .venv/bin/python. Default tests use synthetic source responses and isolated temporary state. The optional live smoke test is in [README](../README.md#verify). Code updates do not require rereading the CV or resetting private state.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Running djinni-mcp waits silently | Expected: stdio waits for the MCP client. Ctrl+C stops a manual launch; configure the executable in your client. |
| Executable not found | Use the full venv executable path; keep the repository and venv in place. |
| Dependency installation failure | Check Python version and the exact pip error. Do not bypass failures with --no-deps; this pinned environment was not verified on every platform. |
| Profile unexpectedly empty | Compare DJINNI_MCP_DATA_DIR across clients/projects before re-entering private data. |
| Old workflow or missing tools | Restart MCP, refresh tools and read get_workflow again; expect eight tools. |
| Permission denied saving data | Choose a private writable data directory; do not elevate the whole AI client unnecessarily. |
| HTTP 403, timeout or changed source page | The public source can block/change. Retry later; do not infer vacancy closure from an acquisition failure. |
| Fewer results than requested | Exclusions and the bounded RSS window can reduce results. Continue next_offset if available; do not silently widen required criteria. |
| Repeated recommendation | Repeats are allowed and dated; explicitly exclude the numeric ID if unwanted. |

## Privacy and limits

No Djinni credentials, browser session or personal API key belongs in this repository. Candidate data stays in the configured private directory and is returned to your AI client, which may process it under that provider's policy. This implementation does not submit candidate facts to Djinni. SQLite is ordinary local storage, not an encrypted vault.

Do not attach populated data directories or actual MCP configuration to issues. Use synthetic examples and redact local user paths. Source coverage is unknown, remote does not imply worldwide eligibility, and absent salary remains unknown. See [publication privacy](publication-privacy.md), [tool contract](tool-contract-v0.2.md) and [verification evidence](verification-v0.2.md).
