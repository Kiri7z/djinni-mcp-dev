"""Exercise a supplied installed/uvx command over real stdio with synthetic state."""

import argparse
import asyncio
import json
import tempfile
from pathlib import Path

from mcp import Client, StdioServerParameters


async def verify(command: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="djinni-package-") as directory:
        root = Path(directory)
        data = root / "private-data"
        first, second = root / "first-launch", root / "second-launch"
        first.mkdir()
        second.mkdir()

        def parameters(cwd):
            return StdioServerParameters(command=command[0], args=command[1:],
                env={"DJINNI_MCP_DATA_DIR": str(data), "UV_TOOL_DIR": str(root / "uv-tools")}, cwd=str(cwd))

        async def call(client, name, arguments=None):
            result = await client.call_tool(name, arguments or {})
            if result.is_error:
                raise AssertionError(f"{name}: {result.content}")
            return result

        async with Client(parameters(first)) as client:
            names = {tool.name for tool in (await client.list_tools()).tools}
            assert names == {"get_workflow", "get_profile", "update_profile", "search_jobs", "get_job",
                             "get_history", "save_search", "set_job_excluded"}, names
            await call(client, "get_workflow")
            empty = (await call(client, "get_profile")).structured_content
            assert empty["version"] == 0 and empty["fields"] == {}, empty
            assert not data.exists(), "read-only startup created private state"
            profile = (await call(client, "update_profile", {
                "questionnaire": {"target_roles": "Synthetic operations role"}})).structured_content
            receipt = (await call(client, "save_search", {"request": {
                "request_id": "package_smoke", "profile_version": profile["version"],
                "recommendations": [{"job_id": "123", "title": "Synthetic vacancy",
                                     "summary": "Synthetic company and fit assessment."}],
                "report_markdown": "# Synthetic package check\n\nNo real candidate data.\n"
            }})).structured_content
            assert Path(receipt["report_path"]).read_text(encoding="utf-8").startswith("# Synthetic")
            await call(client, "set_job_excluded", {"job": "123", "reason": "Synthetic user request"})

        async with Client(parameters(second)) as client:
            profile = (await call(client, "get_profile")).structured_content
            assert profile["fields"]["target_roles"] == "Synthetic operations role", profile
            history = (await call(client, "get_history", {"job_ids": ["123"]})).structured_content
            item = history["items"][0]
            assert item["excluded"] and item["last_recommended_at"] == receipt["saved_at"], item
        assert not (first / "local").exists() and not (second / "local").exists()
        print(json.dumps({"stdio": "passed", "tools": len(names), "persistence_across_processes": "passed",
                          "working_directory_independence": "passed", "data": "synthetic"}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    arguments = parser.parse_args().command
    if arguments[:1] == ["--"]:
        arguments = arguments[1:]
    if not arguments:
        parser.error("supply -- followed by the server executable and arguments")
    asyncio.run(verify(arguments))
