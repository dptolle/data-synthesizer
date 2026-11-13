"""The csv-synth command line."""

import random
from pathlib import Path
from typing import Optional

import typer

from csv_synth import csvio

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

    from csv_synth.detect import detect_personal_columns
    from csv_synth.synth import synthesize  # SDV import is slow; keep --help fast

    real = csvio.read_source(file)
    personal = detect_personal_columns(real)
    synthetic = synthesize(
        real, rows if rows is not None else len(real), seed, rare_threshold, personal
    )
    csvio.write_synthetic(synthetic, target)

    typer.echo(
        "Faked (personal data): "
        + (", ".join(f"{c} ({t})" for c, t in personal.items()) or "none")
        + "."
    )
    typer.echo(
        f"Wrote {len(synthetic)} rows and {len(synthetic.columns)} columns to {target}."
    )
