"""Exercise CSV/JSON assembly through its real CLI using synthetic inputs only."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class AssemblyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.output = self.root / "assembled.csv"

    def write_csv(self, name, rows, header=("Timestamp", "lon", "lat", "value")):
        path = self.root / name
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(rows)
        return path

    def run_cli(self, paths, *options, success=True):
        result = subprocess.run(
            [sys.executable, "-m", "replication.assemble_outputs", *map(str, paths),
             "--output", str(self.output), *options],
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
            encoding="utf-8", timeout=90,
        )
        self.assertEqual(result.returncode, 0 if success else 2, result.stdout + result.stderr)
        return result

    def read_output(self):
        with self.output.open(encoding="utf-8", newline="") as handle:
            return list(csv.reader(handle))

    def test_csv_preserves_text_precision_leading_zeros_and_quoted_newlines(self):
        first = self.write_csv("first.csv", [["2019-01-01", "0", "0", "00001"]])
        second = self.write_csv("second.csv", [
            ["2019-02-01", "0", "0", "0.0000000000000001"],
            ["2019-03-01", "0", "0", "synthetic\nCaf\u00e9"],
        ])
        report = json.loads(self.run_cli([first, second], "--duplicate-check", "sqlite").stdout)
        self.assertEqual(report["row_count"], 3)
        self.assertTrue(report["duplicate_check_complete"])
        self.assertEqual([r[-1] for r in self.read_output()[1:]],
                         ["00001", "0.0000000000000001", "synthetic\nCaf\u00e9"])

    def test_header_mismatch_preserves_existing_output_and_cleans_temporary_files(self):
        first = self.write_csv("first.csv", [["2019-01-01", "0", "0", "1"]])
        second = self.write_csv("second.csv", [["2"]], header=("different",))
        self.output.write_text("existing output\n", encoding="utf-8")
        self.run_cli([first, second], "--duplicate-check", "sqlite", success=False)
        self.assertEqual(self.output.read_text(), "existing output\n")
        self.assertFalse(list(self.root.glob(".sar-keys-*")))
        self.assertFalse(list(self.root.glob(".assembled.csv.*")))

    def test_full_duplicate_check_catches_duplicates_after_the_sample_limit(self):
        path = self.write_csv("input.csv", [
            ["2019-01-01", "0", "0", "1"],
            ["2019-02-01", "0", "0", "2"],
            ["2019-02-01", "0", "0", "3"],
        ])
        result = self.run_cli([path], "--duplicate-check", "sqlite",
                              "--sample-key-limit", "1", success=False)
        self.assertIn("duplicate key in full check", result.stderr)
        self.assertFalse(self.output.exists())

    def test_output_cannot_overwrite_an_input(self):
        path = self.write_csv("input.csv", [["2019-01-01", "0", "0", "1"]])
        original = path.read_bytes()
        self.output = path
        self.run_cli([path], success=False)
        self.assertEqual(path.read_bytes(), original)

    def test_json_union_preserves_missing_values_and_text(self):
        first, second = self.root / "first.json", self.root / "second.json"
        first.write_text(json.dumps({"GID": "synthetic-A", "date": "2019-01", "code": "00001"}))
        second.write_text(json.dumps({"GID": "synthetic-B", "date": "2019-01", "other": None}))
        self.run_cli([first, second], "--json-records", "--duplicate-check", "sqlite")
        self.assertEqual(self.read_output(), [
            ["GID", "date", "code", "other"],
            ["synthetic-A", "2019-01", "00001", ""],
            ["synthetic-B", "2019-01", "", ""],
        ])

    def test_ambiguous_or_nonfinite_json_is_rejected_without_replacing_output(self):
        cases = [
            '{"GID":"synthetic-A","date":"2019-01","value":1,"value":2}',
            *['{"GID":"synthetic-A","date":"2019-01","value":' + number + '}'
              for number in ("NaN", "Infinity", "-Infinity", "1e9999")],
        ]
        for contents in cases:
            with self.subTest(contents=contents):
                source = self.root / "invalid.json"
                source.write_text(contents, encoding="utf-8")
                self.output.write_text("existing output\n", encoding="utf-8")
                self.run_cli([source], "--json-records", success=False)
                self.assertEqual(self.output.read_text(), "existing output\n")

    def test_streaming_assembly_bounds_python_allocations_for_100000_rows(self):
        source = self.root / "large.csv"
        rows = 100_000
        with source.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["Timestamp", "lon", "lat", "value"])
            for number in range(rows):
                writer.writerow([str(number), "0", "0", "synthetic" * 24])
        probe = (
            "import json,sys,time,tracemalloc; "
            "from replication.assemble_outputs import main; "
            "tracemalloc.start(); started=time.perf_counter(); "
            "code=main(sys.argv[1:]); peak=tracemalloc.get_traced_memory()[1]; "
            "print(json.dumps({'python_peak_bytes':peak,'seconds':time.perf_counter()-started})); "
            "sys.exit(code)"
        )
        result = subprocess.run(
            [sys.executable, "-c", probe, str(source), "--output", str(self.output),
             "--duplicate-check", "sqlite"],
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
            encoding="utf-8", timeout=90,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        metrics = json.loads(result.stdout.splitlines()[-1])
        self.assertGreater(source.stat().st_size, 16 * 1024 * 1024)
        self.assertLess(metrics["python_peak_bytes"], 8 * 1024 * 1024)
        with self.output.open(encoding="utf-8", newline="") as handle:
            self.assertEqual(sum(1 for _ in csv.reader(handle)), rows + 1)
        print(json.dumps({"synthetic_rows": rows, "input_bytes": source.stat().st_size,
                          **metrics}), file=sys.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
