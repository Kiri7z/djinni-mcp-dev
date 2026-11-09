"""Opt-in, bounded anonymous smoke test; not part of unittest discovery.

Run from the project root with .venv/bin/python tests/live_smoke.py.
Real source observations stay in ignored local/implementation/.
"""

import asyncio
import json
import os
import sys
import sysconfig
import tempfile
from pathlib import Path

from mcp import Client, StdioServerParameters


async def main():
    executable = Path(sysconfig.get_path("scripts")) / ("djinni-mcp.exe" if os.name == "nt" else "djinni-mcp")
    with tempfile.TemporaryDirectory() as temporary:
        await check(executable, temporary)


async def check(executable, temporary):
    async with Client(StdioServerParameters(command=str(executable),
            env={'DJINNI_MCP_DATA_DIR':temporary})) as client:
        names = sorted(t.name for t in (await client.list_tools()).tools)
        assert len(names) == 8 and {"get_job", "search_jobs"}.issubset(names), names

        async def call(name, arguments):
            result = await client.call_tool(name, arguments)
            if result.is_error:
                raise RuntimeError(f"{name} failed: {result.content}")
            return result.structured_content

        search = await call("search_jobs", {"category": "Sysadmin", "remote_only": True, "limit": 2})
        assert search["coverage"] == "unknown"
        assert 0 < search["returned_count"] <= 2, "Live source has no test jobs"
        assert all(j["activity"] == "unknown" for j in search["jobs"])
        observations = []
        # Public research examples: status may change, so report current evidence.
        for identity in dict.fromkeys([search["jobs"][0]["id"], "837568", "845892"]):
            detail = await call("get_job", {"job": identity, "description_limit": 500})
            job = detail["job"]
            assert job["id"] == identity and job["title"]
            assert job["description"] is None or len(job["description"]) <= 500
            observations.append({k: job[k] for k in [
                "id", "title", "company", "activity", "activity_checked_at",
                "work_format", "eligible_locations", "english_requirement",
                "description_length", "description_truncated", "dates",
            ]})
        report = {
            "tools": names,
            "search": {k: search[k] for k in ["checked_at", "source_url", "fetched_count",
                "matched_count", "returned_count", "coverage", "possibly_truncated"]},
            "details": observations,
        }
    destination = Path("local/implementation/live-smoke.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
