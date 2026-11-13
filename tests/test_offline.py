"""The main promise: after install, a full run needs no network."""

import socket

import pytest

from csv_synth.cli import app  # noqa: F401  (import before sockets are blocked)


@pytest.mark.disable_socket
def test_blocked_sockets_really_block_connections():
    # Guards the guard: if this stops raising, the offline test below proves nothing.
    with pytest.raises(Exception, match="(?i)socket"):
        socket.socket().connect(("127.0.0.1", 9))


@pytest.mark.disable_socket
def test_full_generate_runs_with_network_blocked(invoke, source_csv):
    result = invoke("generate", source_csv, "--seed", 3)

    assert result.exit_code == 0, result.output
    assert (source_csv.parent / "hotel_synthetic.csv").exists()


def test_generate_never_calls_sdv_demo_downloads(invoke, source_csv, monkeypatch):
    import sdv.datasets.demo as demo

    def forbidden(*args, **kwargs):
        raise AssertionError("SDV demo download was called")

    # Every public demo function, plus the one place an S3 client is created.
    for name in (
        "download_demo",
        "get_available_demos",
        "get_source",
        "get_readme",
        "save_resource",
        "_create_s3_client",
    ):
        assert hasattr(demo, name), f"SDV changed: {name} is gone, update this test"
        monkeypatch.setattr(demo, name, forbidden)

    result = invoke("generate", source_csv, "--seed", 3)
    assert result.exit_code == 0, result.output
