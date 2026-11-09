"""Check the Djinni release file allowlist, public metadata and archive hashes."""

import argparse
import hashlib
import json
import re
import tarfile
import tomllib
import zipfile
from email import policy
from email.parser import BytesParser
from pathlib import Path

MODULES = {"__init__.py", "models.py", "server.py", "source.py", "state.py", "workflow.py"}
EGG_INFO = {"PKG-INFO", "SOURCES.txt", "dependency_links.txt", "entry_points.txt", "requires.txt", "top_level.txt"}
PRIVATE_PATH = re.compile(rb"/Users/|/home/|/private/var/folders/|/var/folders/|[A-Za-z]:\\Users\\")
EMAIL = re.compile(rb"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")


def check(directory: Path, expected_tag: str | None = None):
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]
    version = project["version"]
    assert project["name"] == "djinni-mcp" and project["license"] == "MIT"
    if expected_tag:
        assert expected_tag == f"v{version}", "release tag must match package version"
    stem = f"djinni_mcp-{version}"
    distributions = sorted(directory.glob("*.whl")) + sorted(directory.glob("*.tar.gz"))
    assert {p.name for p in distributions} == {f"{stem}-py3-none-any.whl", f"{stem}.tar.gz"}
    manifest = {}
    for archive in distributions:
        if archive.suffix == ".whl":
            with zipfile.ZipFile(archive) as opened:
                assert all((i.external_attr >> 16) & 0o170000 != 0o120000 for i in opened.infolist())
                entries = {i.filename: opened.read(i) for i in opened.infolist() if not i.is_dir()}
            info = f"{stem}.dist-info/"
            expected = {f"djinni_mcp/{name}" for name in MODULES} | {
                info + name for name in {"METADATA", "WHEEL", "entry_points.txt", "top_level.txt",
                                       "RECORD", "licenses/LICENSE"}}
            assert set(entries) == expected, (archive.name, sorted(set(entries) ^ expected))
            metadata = entries[info + "METADATA"]
            init = entries["djinni_mcp/__init__.py"]
        else:
            with tarfile.open(archive) as opened:
                members = opened.getmembers()
                assert all(m.isfile() or m.isdir() for m in members), "archive contains links/special files"
                entries = {m.name.removeprefix(stem + "/"): opened.extractfile(m).read()
                           for m in members if m.isfile()}
            expected = {f"src/djinni_mcp/{name}" for name in MODULES} | {
                "pyproject.toml", "MANIFEST.in", "LICENSE", "docs/package-readme.md", "PKG-INFO", "setup.cfg"}
            allowed = expected | {f"src/djinni_mcp.egg-info/{name}" for name in EGG_INFO}
            assert expected <= set(entries) <= allowed, (archive.name, sorted(set(entries) ^ expected))
            metadata = entries["PKG-INFO"]
            init = entries["src/djinni_mcp/__init__.py"]
        for name, payload in entries.items():
            assert not PRIVATE_PATH.search(payload), f"personal absolute path in {name}"
            assert not EMAIL.search(payload), f"email address in {name}"
        parsed = BytesParser(policy=policy.default).parsebytes(metadata)
        assert parsed["Name"] == "djinni-mcp" and parsed["Version"] == version
        assert parsed["License-Expression"] == "MIT" and parsed.get("Author-email") is None
        assert f'__version__ = "{version}"'.encode() in init, "runtime/package version mismatch"
        assert "Source, https://github.com/Kiri7z/djinni-mcp-dev" in parsed.get_all("Project-URL", [])
        manifest[archive.name] = {"sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                                  "size": archive.stat().st_size, "files": sorted(entries)}
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--tag")
    arguments = parser.parse_args()
    check(arguments.directory, arguments.tag)
