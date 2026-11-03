"""Exercise the code-only archive boundary without using research data."""

from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from .build_release import ReleaseError, build_release, collect_release_files


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "replication"
        shutil.copytree(
            Path(__file__).resolve().parent,
            self.source,
            ignore=shutil.ignore_patterns("__pycache__"),
        )

    def test_archive_is_deterministic_and_contains_exact_source_bytes(self):
        first = build_release(self.source, self.root / "first.zip")
        second = build_release(self.source, self.root / "second.zip")
        self.assertEqual(first["archive_sha256"], second["archive_sha256"])
        with zipfile.ZipFile(self.root / "first.zip") as archive:
            self.assertIn("replication/constraints-py311.txt", archive.namelist())
            for member in first["members"]:
                relative = Path(member["path"]).relative_to("replication")
                self.assertEqual(archive.read(member["path"]), (self.source / relative).read_bytes())

    def test_missing_dependency_constraints_block_the_release(self):
        (self.source / "constraints-py311.txt").unlink()
        with self.assertRaises(ReleaseError):
            collect_release_files(self.source)

    def test_datasets_and_notebooks_cannot_enter_the_release(self):
        for name in ("fixture.csv", "fixture.geojson", "fixture.ipynb"):
            with self.subTest(name=name):
                path = self.source / name
                path.write_text("synthetic fixture", encoding="utf-8")
                try:
                    with self.assertRaises(ReleaseError):
                        collect_release_files(self.source)
                finally:
                    path.unlink()

    def test_credential_assignment_blocks_the_release(self):
        probe = self.source / "credential_fixture.py"
        probe.write_text("api_key = " + repr("synthetic" * 3), encoding="utf-8")
        with self.assertRaises(ReleaseError):
            collect_release_files(self.source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
