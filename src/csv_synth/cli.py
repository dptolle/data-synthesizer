"""The csv-synth command line."""

import random
from pathlib import Path
from typing import Optional

import typer

from csv_synth import csvio, privacy, settings as settings_mod

app = typer.Typer(
    help=(
        "Make a synthetic copy of a CSV file, entirely on this computer. "
        "The copy has the same columns and similar statistics, but no real rows."
    ),
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def main() -> None:
    """Make a synthetic copy of a CSV file, entirely on this computer."""


def _default_settings(file: Path) -> Path:
    return file.with_name(f"{file.stem}_settings.csv")


@app.command()
def inspect(
    file: Path = typer.Argument(..., help="The Source CSV to look at."),
    settings_file: Optional[Path] = typer.Option(
        None,
        "--settings",
        help="Where to write the Settings file. Default: <input>_settings.csv next to the input.",
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite the Settings file if it already exists."
    ),
) -> None:
    """Guess how each column is handled and write it to a Settings file you can edit."""
    if not file.is_file():
        typer.echo(f"Error: cannot find the file {file}.", err=True)
        raise typer.Exit(1)
    target = settings_file or _default_settings(file)
    if target.exists() and not force:
        typer.echo(
            f"Error: {target} already exists. Use --force to overwrite it, "
            "or --settings to choose another name.",
            err=True,
        )
        raise typer.Exit(1)
    found = settings_mod.detect_settings(csvio.read_source(file))
    settings_mod.write_settings(found, target)
    typer.echo(f"Wrote settings for {len(found)} columns to {target}.")
    typer.echo("Check the types in the file, then run: csv-synth generate " + str(file))


@app.command()
def generate(
    file: Path = typer.Argument(
        ..., help="The Source CSV to learn from (comma-separated, UTF-8)."
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Name of the Synthetic CSV. Default: <input>_synthetic.csv next to the input.",
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite the output file if it already exists."
    ),
    rows: Optional[int] = typer.Option(
        None,
        "--rows",
        min=1,
        help="How many rows to generate. Default: as many as the Source CSV has.",
    ),
    seed: Optional[int] = typer.Option(
        None,
        "--seed",
        min=0,
        help="Number that makes the output repeatable: same file and same seed give the same result. "
        "Default: a random seed, which is printed.",
    ),
    fit_rows: int = typer.Option(
        100_000,
        "--fit-rows",
        min=1,
        help="Learn from a random sample of this many rows if the Source CSV is larger. Default: 100,000.",
    ),
    settings_file: Optional[Path] = typer.Option(
        None,
        "--settings",
        help="Settings file. Default: <input>_settings.csv next to the input. "
        "If it exists it is read and used, otherwise the detected settings are written there.",
    ),
    rare_threshold: int = typer.Option(
        5,
        "--rare-threshold",
        min=1,
        help="Category labels seen in fewer rows than this become \"Other\".",
    ),
) -> None:
    """Read FILE and write a Synthetic CSV next to it."""
    if not file.is_file():
        typer.echo(f"Error: cannot find the file {file}.", err=True)
        raise typer.Exit(1)

    target = output or file.with_name(f"{file.stem}_synthetic.csv")
    if target.exists() and not force:
        typer.echo(
            f"Error: {target} already exists. Use --force to overwrite it, "
            "or -o to choose another name.",
            err=True,
        )
        raise typer.Exit(1)

    if seed is None:
        seed = random.SystemRandom().randrange(2**32)
    typer.echo(f"Using seed {seed} (pass --seed {seed} to repeat this run).")

    from csv_synth.synth import synthesize  # SDV import is slow; keep --help fast

    real = csvio.read_source(file)
    settings_path = settings_file or _default_settings(file)
    settings_read = settings_path.exists()
    if settings_read:
        try:
            chosen = settings_mod.read_settings(settings_path)
            settings_mod.check_matches(chosen, real)
        except settings_mod.SettingsError as exc:
            typer.echo(f"Error: {exc}", err=True)
            raise typer.Exit(1)
    else:
        chosen = settings_mod.detect_settings(real)
    dropped = [s.column for s in chosen if s.action == "drop"]
    types = settings_mod.types_of_kept(chosen)
    if not types:
        typer.echo("Error: every column is set to drop, so there is nothing to generate.", err=True)
        raise typer.Exit(1)
    real = real[list(types)]
    personal = {c: t for c, t in types.items() if t in settings_mod.FAKED_TYPES}
    total = len(real)
    out_rows = rows if rows is not None else total
    if total > fit_rows:
        typer.echo(
            f"Note: the file is large, so the tool learns from a random sample "
            f"of {fit_rows} of {total} rows. The output still has {out_rows} rows."
        )
    synthetic = synthesize(real, out_rows, seed, rare_threshold, types, fit_rows)
    # The Settings file's types drive the overlap check.
    findings = privacy.check_overlap(real, synthetic, types)
    blocking = [f for f in findings if f.blocks]
    warnings = [f for f in findings if not f.blocks]
    if blocking:
        typer.echo(
            "Error: the privacy check failed, so no file was written. "
            "Nothing was changed automatically.",
            err=True,
        )
        for line in privacy.describe(blocking):
            typer.echo(line, err=True)
        raise typer.Exit(1)

    csvio.write_synthetic(synthetic, target)
    if not settings_read:
        settings_mod.write_settings(chosen, settings_path)

    typer.echo(
        "Faked (personal data): "
        + (", ".join(f"{c} ({t})" for c, t in personal.items()) or "none")
        + "."
    )
    typer.echo("Dropped: " + (", ".join(dropped) or "none") + ".")
    typer.echo(
        f"Wrote {len(synthetic)} rows and {len(synthetic.columns)} columns to {target}."
    )
    if warnings:
        typer.echo("Warning: the file was saved, but note:", err=True)
        for line in privacy.describe(warnings):
            typer.echo(line, err=True)
        typer.echo("Privacy check passed for personal values.")
    else:
        typer.echo("Privacy check passed: no personal values and no real rows in the output.")
