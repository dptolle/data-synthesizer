import pandas as pd


def test_large_source_is_sampled_and_note_printed(invoke, source_csv):
    result = invoke("generate", source_csv, "--fit-rows", 30, "--seed", 1)

    assert result.exit_code == 0, result.output
    assert "30 of 120 rows" in result.output
    synth = pd.read_csv(source_csv.parent / "hotel_synthetic.csv")
    assert len(synth) == 120  # output size is unchanged


def test_rows_option_still_wins_when_sampling(invoke, source_csv):
    result = invoke("generate", source_csv, "--fit-rows", 30, "--rows", 50)

    assert result.exit_code == 0, result.output
    assert len(pd.read_csv(source_csv.parent / "hotel_synthetic.csv")) == 50


def test_no_note_when_file_fits(invoke, source_csv):
    result = invoke("generate", source_csv, "--fit-rows", 120)

    assert result.exit_code == 0, result.output
    assert "random sample" not in result.output


def test_sampling_is_repeatable_with_seed(invoke, source_csv, tmp_path):
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    for target in (a, b):
        assert invoke(
            "generate", source_csv, "--fit-rows", 30, "--seed", 5, "-o", target
        ).exit_code == 0
    assert a.read_bytes() == b.read_bytes()


def test_fit_rows_must_be_positive(invoke, source_csv):
    assert invoke("generate", source_csv, "--fit-rows", 0).exit_code != 0


def test_default_fit_rows_is_100000(invoke):
    result = invoke("generate", "--help")

    assert "--fit-rows" in result.output
    assert "100,000" in result.output
