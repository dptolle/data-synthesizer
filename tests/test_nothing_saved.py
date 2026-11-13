"""No model file and no SDV log file is written anywhere the tool can write.

The tool can write to the input folder, the output folder, the Settings folder and
the current folder. This test runs a full `generate` with all four apart and lists
every file afterwards. It does not look at your user data folder.
"""


def test_only_the_synthetic_csv_and_settings_file_are_written(
    invoke, source_csv, tmp_path, monkeypatch
):
    out_dir, settings_dir, cwd = (tmp_path / d for d in ("out", "settings", "cwd"))
    for d in (out_dir, settings_dir, cwd):
        d.mkdir()
    monkeypatch.chdir(cwd)
    before = {p for p in tmp_path.rglob("*") if p.is_file()}

    result = invoke(
        "generate", source_csv, "-o", out_dir / "o.csv", "--settings", settings_dir / "s.csv"
    )

    assert result.exit_code == 0, result.output
    new = {p for p in tmp_path.rglob("*") if p.is_file()} - before
    assert new == {out_dir / "o.csv", settings_dir / "s.csv"}
    names = {p.name.lower() for p in tmp_path.rglob("*")}
    assert "sdv_logs.csv" not in names
    assert not [n for n in names if n.endswith((".pkl", ".pickle", ".sdv"))]
    assert not list(cwd.iterdir())
