import pandas as pd


def test_generate_writes_synthetic_csv_next_to_input(invoke, source_csv):
    result = invoke("generate", source_csv)

    assert result.exit_code == 0, result.output
    out = source_csv.parent / "hotel_synthetic.csv"
    assert out.exists()
    real = pd.read_csv(source_csv)
    synth = pd.read_csv(out)
    assert list(synth.columns) == list(real.columns)
    assert len(synth) == len(real)


def test_summary_reports_rows_and_columns_without_values(invoke, source_csv):
    result = invoke("generate", source_csv)

    assert "120 rows" in result.output
    assert "5 columns" in result.output
    assert "single" not in result.output and "suite" not in result.output


def test_output_option_sets_name(invoke, source_csv, tmp_path):
    target = tmp_path / "other.csv"
    result = invoke("generate", source_csv, "-o", target)

    assert result.exit_code == 0, result.output
    assert target.exists()
    assert not (tmp_path / "hotel_synthetic.csv").exists()


def test_existing_output_stops_unless_force(invoke, source_csv):
    out = source_csv.parent / "hotel_synthetic.csv"
    out.write_text("keep me")

    result = invoke("generate", source_csv)
    assert result.exit_code != 0
    assert "already exists" in result.output
    assert "--force" in result.output
    assert out.read_text() == "keep me"

    result = invoke("generate", source_csv, "--force")
    assert result.exit_code == 0, result.output
    assert out.read_text() != "keep me"


def test_rows_option(invoke, source_csv):
    result = invoke("generate", source_csv, "--rows", 37)

    assert result.exit_code == 0, result.output
    synth = pd.read_csv(source_csv.parent / "hotel_synthetic.csv")
    assert len(synth) == 37


def test_same_seed_gives_identical_output(invoke, source_csv, tmp_path):
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    assert invoke("generate", source_csv, "--seed", 7, "-o", a).exit_code == 0
    assert invoke("generate", source_csv, "--seed", 7, "-o", b).exit_code == 0
    assert a.read_bytes() == b.read_bytes()


def test_random_seed_is_printed_and_reproduces_output(invoke, source_csv, tmp_path):
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    first = invoke("generate", source_csv, "-o", a)
    assert first.exit_code == 0, first.output
    line = next(l for l in first.output.splitlines() if "seed" in l.lower())
    seed = int("".join(c for c in line.split("seed")[-1] if c.isdigit()))

    assert invoke("generate", source_csv, "--seed", seed, "-o", b).exit_code == 0
    assert a.read_bytes() == b.read_bytes()


def test_empty_column_stays_empty_and_missing_values_keep_rate(invoke, source_csv):
    assert invoke("generate", source_csv, "--rows", 400, "--seed", 1).exit_code == 0
    synth = pd.read_csv(source_csv.parent / "hotel_synthetic.csv")

    assert synth["empty_col"].isna().all()
    assert abs(synth["rating"].isna().mean() - 0.25) < 0.1


def test_no_files_written_besides_outputs(invoke, source_csv, monkeypatch):
    monkeypatch.chdir(source_csv.parent)
    before = {p.name for p in source_csv.parent.iterdir()}
    assert invoke("generate", source_csv).exit_code == 0
    new = {p.name for p in source_csv.parent.iterdir()} - before
    # sdv_logs.csv is handled in ticket 02
    assert new - {"sdv_logs.csv"} == {"hotel_synthetic.csv"}


def test_help_explains_every_option(invoke):
    top = invoke("--help")
    assert top.exit_code == 0 and "generate" in top.output
    gen = invoke("generate", "--help")
    assert gen.exit_code == 0
    for opt in ["--output", "--force", "--rows", "--seed"]:
        assert opt in gen.output
