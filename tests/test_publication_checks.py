"""Regression checks for accidental data and saved notebook-state publication."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.check_publication import check_notebook, check_paths


class PublicationChecks(unittest.TestCase):
    def test_data_archives_unknown_files_and_environment_secrets_are_disallowed(self):
        check_paths(["README.md", "replication/config.py", ".gitmodules", "src/gee_s1_ard"])
        for name in ("raw.csv", "raw.json", "raw.bin", "backup.bundle", ".env.production",
                     "inputs/notes.txt", "OUTPUTS/table.md", "private.pem"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                check_paths([name])

    def test_hidden_notebook_attachments_widgets_and_saved_execution_are_disallowed(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "synthetic.ipynb"
            clean = {"nbformat": 4, "metadata": {}, "cells": [
                {"cell_type": "code", "source": ["print('synthetic')"],
                 "metadata": {}, "execution_count": None, "outputs": []}]}
            path.write_text(json.dumps(clean), encoding="utf-8")
            check_notebook(path)
            cases = [
                {"metadata": {"widgets": {"synthetic": {}}}},
                {"cells": [{"cell_type": "markdown", "attachments": {"synthetic.png": {}}}]},
                {"cells": [{"cell_type": "code", "outputs": [{"output_type": "stream"}]}]},
                {"cells": [{"cell_type": "code", "execution_count": 1}]},
            ]
            for changes in cases:
                path.write_text(json.dumps(clean | changes), encoding="utf-8")
                with self.subTest(changes=changes), self.assertRaises(ValueError):
                    check_notebook(path)

    def test_data_gate_still_rejects_a_tracked_dataset_with_python_optimization_enabled(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "raw.csv").write_text("synthetic\n1\n", encoding="utf-8")
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "add", "raw.csv"], check=True)
            script = Path(__file__).resolve().parents[1] / "tools" / "check_publication.py"
            result = subprocess.run([sys.executable, "-O", str(script), "--root", str(root)],
                                    capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 2)
            self.assertIn("disallowed publication file type: raw.csv", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
