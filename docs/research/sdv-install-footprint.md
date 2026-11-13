# How heavy is SDV to install, and on which platforms?

Researched 2026-11-13. SDV 2.2.0 was the current release.
Scope: a local CLI that turns one CSV into a synthetic CSV with `GaussianCopulaSynthesizer` only.

## Short answer

- A plain `pip install sdv` pulls in PyTorch. On Windows that is about 840 MB on disk.
- GaussianCopula does not need torch. SDV can now be imported and used without it.
- The no-torch install is about 320 MB on disk. It works, but SDV has no official "light" extra for it.
- A PyInstaller exe from the no-torch install was not measured (the build did not finish in about 15 minutes). Expect roughly 100 to 200 MB; this is a guess.

## 1. What `pip install sdv` pulls in

SDV 2.2.0 core dependencies (from PyPI metadata and `pyproject.toml`):

- Data stack: `numpy`, `pandas` (below 3), `scipy` (via copulas, rdt), `scikit-learn` (via rdt, sdmetrics), `plotly` (via copulas, sdmetrics).
- AWS: `boto3`, `botocore`.
- SDV family: `copulas`, `rdt`, `sdmetrics`, `ctgan`, `deepecho`.
- Small ones: `cloudpickle`, `graphviz`, `tqdm`, `platformdirs`, `pyyaml`.

`ctgan` and `deepecho` both require `torch`. That is the only route to torch. `torch` then adds `sympy`, `networkx`, `jinja2`, `fsspec`, `filelock`, `mpmath`.

Sources:
- https://pypi.org/pypi/sdv/json (`requires_dist`)
- https://github.com/sdv-dev/SDV/blob/main/pyproject.toml
- https://pypi.org/pypi/ctgan/json and https://pypi.org/pypi/deepecho/json (both list `torch`)

### Measured (Windows 11, Python 3.13, `uv pip install`, fresh venv)

| Install | Packages | Size on disk |
|---|---|---|
| `sdv` (default) | 41 | 841 MB |
| `sdv` without torch (see section 3) | about 35 | 317 MB |

- `torch` alone is 489 MB of the 841 MB. The next biggest are scipy (87 MB), pandas (40 MB), plotly (37 MB).
- The torch 2.15.0 wheel for Windows is 121 MB to download. This is the CPU build, because PyPI's Windows wheels have no CUDA.
- Total download for the default install was not read directly. Torch's 121 MB plus the other wheels puts it at roughly 250 MB. Treat that as an estimate.
- On Linux x86_64 the torch wheel is 514 MB, and it depends on many `nvidia-*` CUDA packages (cuDNN, NCCL, cuda-toolkit and others). On Linux a default install is therefore multiple GB. This is read from the torch metadata, not measured here. A CPU-only torch on Linux needs `--index-url https://download.pytorch.org/whl/cpu`.
- On macOS, torch 2.15.0 has only an Apple Silicon (arm64) wheel, 132 MB. There is no Intel Mac wheel in this release.

Source for torch wheels and dependencies: https://pypi.org/pypi/torch/json

## 2. Supported Python versions and operating systems

- SDV 2.2.0: `requires-python >=3.10,<3.15`. Classifiers list 3.10 to 3.14. Source: https://pypi.org/pypi/sdv/json
- SDV is a pure-Python wheel (`py3-none-any`, 195 KB). It has no OS limit of its own. The OS limit comes from its dependencies, mostly torch, numpy, scipy.
- SDV's metadata lists no operating systems. Its README says to install with pip or conda. Source: https://github.com/sdv-dev/SDV/blob/main/README.md
- Torch 2.15.0 supports Python 3.11 to 3.15. So with default install, SDV in practice needs Python 3.11 or newer (3.10 would resolve to an older torch). Source: https://pypi.org/pypi/torch/json
- Without torch, Python 3.10 to 3.14 works.
- New Python releases lag: SDV caps at 3.14. A user with Python 3.15 will get an error. This matters for `pip`/`pipx` users who have the newest Python.

## 3. Can torch be avoided?

Yes, for GaussianCopula.

- SDV issue #2551 asked for SDV to work without torch. It was closed as done by PR #2570, "Allow importing sdv with torch not installed". Before that fix, even `import sdv` crashed without torch. The PR changes `ctgan.py`, `par.py` and `mixins.py`. Torch errors now appear only when a torch synthesizer (CTGAN, TVAE, PAR) is used.
  - https://github.com/sdv-dev/SDV/issues/2551
  - https://github.com/sdv-dev/SDV/pull/2570
- A maintainer says to install SDV from a requirements file that leaves torch out. `sdv[light]` is not a real extra. So there is no official light install. The no-torch route is supported by the code but not packaged.
- I tested it. Steps in a clean venv:
  1. `uv pip install --no-deps sdv ctgan deepecho`
  2. `uv pip install boto3 botocore cloudpickle graphviz numpy pandas tqdm copulas rdt sdmetrics platformdirs pyyaml`
  3. Result: `from sdv.single_table import GaussianCopulaSynthesizer` works. `fit` and `sample` work. `torch` was never loaded. Import took about 6 s on first run, against 37 s in the full install on first run (cold disk, antivirus scan; not a clean comparison).
- Pitfall: you must keep the version floors from SDV's metadata (`sdmetrics>=0.32`, `rdt>=2.0`, `copulas>=0.12.1`). My first try without floors picked old `sdmetrics 0.25` and `rdt 1.19`, and `import sdv` failed with `cannot import name 'DiagnosticReport'`.
- `--no-deps` is a workaround, not a documented path. Pip's resolver would not know the real needs. The `ctgan` and `deepecho` packages are still installed, only torch is missing.
- Cleaner idea for our tool: our own package declares only the dependencies it needs (`sdv` itself must still be listed, and `sdv` declares `ctgan`, which declares `torch`). A dependency list cannot drop a transitive dependency. So the options are:
  1. Depend on `sdv` and accept torch.
  2. Use uv's `override-dependencies` (uv-only, in `pyproject.toml` under `[tool.uv]`). It works for `uv tool install` from a source checkout but not for plain pip, so it is not a good fit for a published tool.
  3. Depend on `copulas` and `rdt` directly and write our own thin wrapper. This drops SDV, and so drops its metadata detection, constraints and `sdmetrics`. About 250 MB saved on top. It is more work and gives up what SDV adds.
  4. Ship a standalone exe built from the no-torch environment (section 4).
- Remaining weight without torch: scipy 93 MB, pandas 45 MB, plotly 38 MB, scikit-learn 31 MB, numpy 23 MB, botocore 21 MB. `plotly` and `boto3` are pulled in by `sdmetrics`/`copulas`/`sdv` and cannot be dropped without the `--no-deps` approach.
- CPU-only torch: if torch must stay, Windows and Mac PyPI wheels are already CPU. Only Linux needs the PyTorch CPU index. Source: https://pypi.org/pypi/torch/json (Linux CUDA dependencies).

## 4. Install routes for non-expert users

### pip

- Needs Python installed first. On Windows that is a separate step for an analyst.
- Typical failures: `pip` not on PATH, Python too new for SDV (3.15), dependency conflicts in a shared environment. SDV's own troubleshooting page says to use a fresh virtual environment. Source: https://docs.sdv.dev/sdv/support/troubleshooting/installation.md
- Size: 841 MB default, about 317 MB without torch.
- Verdict: fine for Python users. Poor for analysts.

### pipx

- Isolates the tool in its own venv. Same size as pip.
- Still needs Python. pipx itself is installed by Scoop (`scoop install pipx`) or `py -m pip install --user pipx`. Then `pipx ensurepath` and a new terminal. The docs warn that the pip route often ends with pipx not on PATH. Source: https://pipx.pypa.io/latest/how-to/install-pipx.html
- Verdict: one more step than uv, same Python problem.

### uv (`uv tool install` / `uvx`)

- uv downloads Python itself if none is found: "By default, uv will automatically download Python versions if they cannot be found on the system." The builds come from Astral's python-build-standalone. So the user does not need Python. Source: https://docs.astral.sh/uv/concepts/python-versions/
- `uv tool install` makes an isolated persistent environment. `uvx` runs the tool from a cached temporary environment, reused afterwards. Source: https://docs.astral.sh/uv/concepts/tools/
- Executables are copied into a bin directory (Windows) or symlinked (Unix). That directory must be on PATH. `uv tool update-shell` fixes it. Same source.
- uv installs with one line. Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`. Mac/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`. Also `winget install --id=astral-sh.uv -e`, `scoop install main/uv`, `brew install uv`. Source: https://docs.astral.sh/uv/getting-started/installation/
- Pitfalls: first run downloads hundreds of MB (long silent wait with torch). The `irm | iex` line looks alarming to analysts and may be blocked on managed company PCs. Users on a locked-down machine may not be allowed to run it.
- uv can choose a Python that SDV supports (`--python 3.13`), which avoids the 3.15 problem.
- Verdict: best script-based route. Two commands: install uv, then `uv tool install <our-package>`.

### Standalone executable (PyInstaller, Nuitka)

- Not measured. I started a PyInstaller `--onefile` build of a GaussianCopula script from the no-torch environment. It had not finished after about 15 minutes, so I stopped it. Build time alone is a pitfall. The FAQ says onefile compresses the libraries. The no-torch install is 317 MB on disk, so a rough guess is 100 to 200 MB. This is an estimate, not a result.
- With torch, expect a much larger exe. Torch alone is 489 MB installed. This was not built.
- PyInstaller does not cross-compile. A Windows exe must be built on Windows, and a Mac build on a Mac. We would need CI with three runners (Windows, Mac Intel/arm, Linux). Source: https://pyinstaller.org/en/stable/operating-mode.html
- One-file exes unpack to a temporary `_MEI...` folder on every start. This makes startup slow and leaves folders if the app crashes. Same source. Onedir builds start faster but can be 50-100% larger and are a folder, not one file. Source: https://github.com/pyinstaller/pyinstaller/wiki/FAQ
- Hidden imports: PyInstaller cannot see imports made at run time and fails with `ImportError`. They must be added with `--hidden-import` or hooks. Source: https://pyinstaller.org/en/stable/when-things-go-wrong.html . SDV, rdt and copulas load things dynamically, so expect some tuning.
- Antivirus: false positives on PyInstaller exes are a known, recurring problem. A PyInstaller maintainer called them a recurring problem in issue #5579, and another thread says to report them to the antivirus vendor. Users report Microsoft Defender flags and that submitting the file to Microsoft clears it. Code signing is the usual mitigation, but I found no primary source that proves it works, and a code-signing certificate costs money. Sources: https://github.com/pyinstaller/pyinstaller/issues/5579 , https://github.com/pyinstaller/pyinstaller/issues/6062
- Nuitka: sold as having fewer false positives, but the only source I found is a blog post (https://dev.to/weisshufer/from-pyinstaller-to-nuitka-convert-python-to-exe-without-false-positives-19jf). I did not verify it. It also needs a C compiler on Windows, and builds are slow.
- macOS: unsigned binaries are blocked by Gatekeeper until the user overrides it. Not checked against a primary source here.
- Verdict: the friendliest for analysts if we can accept the antivirus risk and three CI builds. The most work for us.

### Windows long paths

- Windows has a 260 character path limit by default. Apps must opt in to longer paths and the registry value `LongPathsEnabled` must be 1. Source: https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation
- I measured the longest file path inside the installed packages: 104 characters (no torch) and 127 characters (with torch), counted from `site-packages`. The venv root adds to that. With `uv tool install` the root is short (under your user folder), so the risk is low. It is higher with a venv deep inside a long project folder or OneDrive path. I did not hit it in testing.

## 5. Unknowns

- PyInstaller exe size and whether it runs without hidden-import fixes were not confirmed.
- Real total download size of the default install was not measured. The estimate is above.
- Linux and macOS installs were not run. Only Windows was measured. Linux and Mac numbers come from PyPI metadata.
- Code signing and Nuitka claims are not backed by a primary source.
- SDV 2.x `fit` takes a `{table_name: dataframe}` dict, and `sample` returned a dict in my test. This is an API detail for the spec, not an install fact.

## Answer

- Use GaussianCopula only, and avoid torch. Default `pip install sdv` is about 840 MB on Windows, and multiple GB on Linux (CUDA packages). Without torch it is about 320 MB.
- SDV supports Python 3.10 to 3.14 (not 3.15), and has no OS limit of its own. Torch is the only part that narrows platforms (for example, no Intel Mac wheel in torch 2.15).
- Torch-free use works in code (SDV PR #2570) but is not an official install. There is no `sdv[light]`. A dependency list cannot remove torch, so a torch-free package needs either an exe built from a no-torch environment, a uv-only override, or dropping SDV for `copulas` + `rdt`.
- For analysts, the best routes are: (1) a standalone exe per OS from CI, built from the no-torch environment (size unmeasured, guess 100 to 200 MB), accepting the antivirus risk, or (2) `uv tool install`, which brings its own Python. Plain pip and pipx need the user to have a working Python, and are only for technical users.
- Recommended: ship the exe as the main route for analysts and `uv tool install` as the second route for technical users. First decide whether to accept torch (simple, 840 MB) or build the no-torch environment (more work, 320 MB).
