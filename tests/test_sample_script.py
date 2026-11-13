"""The Sample CSV script also writes a messy-format variant (ticket 09)."""

import subprocess
import sys
from pathlib import Path

import pandas as pd

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "make_sample_csv.py"


def test_script_writes_semicolon_decimal_comma_cp1252_variant(tmp_path):
    out = tmp_path / "hotel.csv"
    subprocess.run([sys.executable, str(SCRIPT), str(out), "60"], check=True, capture_output=True)

    messy = tmp_path / "hotel_messy.csv"
    assert messy.exists()
    plain = pd.read_csv(out)
    got = pd.read_csv(messy, sep=";", decimal=",", encoding="cp1252")
    assert list(got.columns) == list(plain.columns)
    assert got["total_price"].tolist() == plain["total_price"].tolist()
    assert b";" in messy.read_bytes().splitlines()[0]


def test_script_adds_check_in_and_out_dates_in_both_variants(tmp_path):
    out = tmp_path / "hotel.csv"
    subprocess.run([sys.executable, str(SCRIPT), str(out), "60"], check=True, capture_output=True)

    plain = pd.read_csv(out, dtype=str)
    messy = pd.read_csv(tmp_path / "hotel_messy.csv", sep=";", encoding="cp1252", dtype=str)
    for frame, fmt in ((plain, "%Y-%m-%d"), (messy, "%d.%m.%Y")):
        for col in ("check_in", "check_out"):
            assert pd.to_datetime(frame[col], format=fmt, errors="coerce").notna().all()
    delta = pd.to_datetime(plain["check_out"]) - pd.to_datetime(plain["check_in"])
    assert (delta.dt.days == pd.read_csv(out)["nights"]).all()
