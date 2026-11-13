import warnings


def test_generate_does_not_show_sdvs_save_to_json_advice(invoke, source_csv):
    # SDV advises saving the Metadata to a JSON file. csv-synth never writes
    # Metadata to disk on purpose, so the advice only confuses users.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = invoke("generate", source_csv, "--rows", 50, "--seed", 1)

    assert result.exit_code == 0, result.output
    messages = [str(w.message) for w in caught]
    assert not any("save_to_json" in m for m in messages)
