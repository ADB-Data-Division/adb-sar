"""Check tracked publication contents, notebook state, and code archive integrity.

Run Gitleaks separately for credentials. File checks cannot establish data
licensing, scientific provenance, or whether source text embeds restricted data.
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile


ALLOWED_SUFFIXES = {".py", ".md", ".ipynb", ".txt", ".yml", ".yaml", ".toml", ".cff"}
ALLOWED_NAMES = {".gitattributes", ".gitignore", ".gitmodules", ".env.example", "LICENSE", "LICENCE"}
FORBIDDEN_DIRECTORIES = {"datasets", "inputs", "outputs", "release_outputs", ".task_tmp", ".venv", ".git", "__pycache__"}
GITLINK = "src/gee_s1_ard"


def check_paths(names: list[str]) -> None:
    for name in names:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"unsafe tracked path: {name}")
        if FORBIDDEN_DIRECTORIES.intersection(part.casefold() for part in path.parts):
            raise ValueError(f"local data or generated directory is tracked: {name}")
        if name == GITLINK:
            continue
        if path.name not in ALLOWED_NAMES and path.suffix.lower() not in ALLOWED_SUFFIXES:
            raise ValueError(f"disallowed publication file type: {name}")
        if path.name.casefold().startswith(".env") and path.name != ".env.example":
            raise ValueError(f"environment credentials must not be tracked: {name}")


def check_notebook(path: Path) -> None:
    notebook = json.loads(path.read_text(encoding="utf-8-sig"))
    if notebook.get("nbformat") != 4 or not isinstance(notebook.get("cells"), list):
        raise ValueError(f"expected a version 4 notebook: {path}")
    if notebook.get("metadata", {}).get("widgets"):
        raise ValueError(f"saved widget state in {path}")
    for number, cell in enumerate(notebook["cells"], 1):
        if cell.get("attachments") or cell.get("outputs"):
            raise ValueError(f"saved output or attachment in {path}, cell {number}")
        if cell.get("execution_count") is not None or cell.get("metadata", {}).get("execution"):
            raise ValueError(f"saved execution state in {path}, cell {number}")


def check_repository(root: Path) -> dict[str, object]:
    raw = subprocess.check_output(["git", "ls-files", "--stage", "-z"], cwd=root).decode("utf-8")
    entries = [record.split("\t", 1) for record in raw.split("\0") if record]
    check_paths([name for _, name in entries])
    python_files = notebooks = 0
    for metadata, name in entries:
        mode, _, stage = metadata.split()
        if stage != "0":
            raise ValueError(f"unmerged tracked file: {name}")
        if name == GITLINK:
            if mode != "160000":
                raise ValueError(f"expected a pinned Git dependency: {name}")
            continue
        if mode not in {"100644", "100755"}:
            raise ValueError(f"unexpected tracked file mode: {name}")
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"expected a regular tracked file: {name}")
        if path.stat().st_size > 2 * 1024 * 1024:
            raise ValueError(f"publication source exceeds the 2 MiB review limit: {name}")
        if path.suffix == ".py":
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=name)
            python_files += 1
        elif path.suffix == ".ipynb":
            check_notebook(path)
            notebooks += 1

    sys.path.insert(0, str(root))
    from replication.build_release import build_release

    with tempfile.TemporaryDirectory() as temporary:
        first = build_release(root / "replication", Path(temporary) / "first.zip")
        second = build_release(root / "replication", Path(temporary) / "second.zip")
        if first["archive_sha256"] != second["archive_sha256"]:
            raise ValueError("code archive is not deterministic")
    return {"status": "pass", "tracked_entries": len(entries), "python_files": python_files,
            "notebooks": notebooks, "archive_members": first["member_count"],
            "archive_sha256": first["archive_sha256"],
            "scope": "Tracked file types, notebook state, Python syntax, and code-only archive; "
                     "credential scanning, data rights, and scientific provenance are separate checks."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        print(json.dumps(check_repository(args.root.resolve()), indent=2, sort_keys=True))
    except (OSError, ValueError, SyntaxError, subprocess.CalledProcessError) as exc:
        print(f"publication check failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
