"""The committed example CSVs are fake, load with the tool's reader, and match the script."""

import subprocess
import sys
from pathlib import Path

from csv_synth import csvio

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
SCRIPT = ROOT / "scripts" / "make_sample_csv.py"


def test_both_example_files_exist_and_load_with_the_tool_reader():
    plain = csvio.read_source(EXAMPLES / "hotel_sample.csv")
    messy = csvio.read_source(EXAMPLES / "hotel_sample_messy.csv")
    assert len(plain) == len(messy) == 500
    assert list(plain.columns) == list(messy.columns)
    fmt = csvio.detect_format(EXAMPLES / "hotel_sample_messy.csv")
    assert (fmt.delimiter, fmt.decimal, fmt.encoding) == (";", ",", "cp1252")


def test_example_files_are_what_the_script_makes(tmp_path):
    out = tmp_path / "hotel_sample.csv"
    subprocess.run([sys.executable, str(SCRIPT), str(out)], check=True, capture_output=True)
    for name in ("hotel_sample.csv", "hotel_sample_messy.csv"):
        assert (tmp_path / name).read_bytes() == (EXAMPLES / name).read_bytes()
