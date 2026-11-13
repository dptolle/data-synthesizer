# SDV: network calls and leakage of real values

Applies to: `sdv` 2.2.0 (released 2026-11-06), with `rdt` 2.1.0, `copulas` 0.15.0, `sdmetrics` 0.33.0, `ctgan` 0.13.0, `deepecho` 0.9.0, `faker` 40.54.0. These were the latest PyPI versions on 2026-11-13.

Method: I downloaded the wheels from PyPI and read the source. I searched all of it for network code and telemetry. I also read the SDV docs and the changelog. I tried an offline run test (network blocked, real data in, output compared). The process was killed before it printed results. So every claim below comes from source and docs, not from a run. Re-check the points marked "verify" with a real test in our repo.

## Part 1. Network

### Short answer

For `GaussianCopulaSynthesizer` on a local CSV, SDV 2.2.0 makes no network calls. It sends no telemetry. Nothing needs a network after install.

### Facts

1. The only network code in SDV and its dependencies is the demo dataset module `sdv/datasets/demo.py`. It uses `boto3` with unsigned requests to the public S3 bucket `sdv-datasets-public`. It runs only when you call demo functions such as `download_demo`, `get_available_demos`, `load_demo`. Nothing else in the package calls these. The docs say: "These methods require an internet connection."
   - Source: https://github.com/sdv-dev/SDV/blob/main/sdv/datasets/demo.py
   - Docs: https://docs.sdv.dev/sdv/integration/utils/demo
   - Our tool must never call these.
2. `boto3` and `botocore` are hard dependencies of `sdv` (only for that demo module). Importing `sdv` does not import `boto3` in the modules we checked, but `sdv.datasets.demo` does. It makes no connection at import time. Verify: import `sdv` with sockets blocked.
3. I searched `sdv`, `rdt`, `copulas`, `sdmetrics`, `ctgan` and `deepecho` for `requests`, `urllib`, `socket`, `http`, `urlopen`, `telemetry`, `analytics`, `posthog`, `mixpanel`, `sentry`, update checks. The only hits were `pip install ...` text inside error messages. No telemetry, no update check.
4. `faker` (a dependency of `rdt`) generates values locally from built-in data. It makes no network calls.
5. `torch` comes in through `ctgan`. It is not used by `GaussianCopulaSynthesizer`. It makes no calls at import in normal use. `sdv` still imports `ctgan`, so `torch` must be installed.
6. "SDV Enterprise" and DataCebo license keys: in the community package these only appear in demo code and error messages (for example "Private buckets are only supported in SDV Enterprise"). `sdv.version.enterprise` is `None`. There is no license check and no phone-home. Add-ons: at import SDV loads Python entry points in the group `sdv_modules` from packages you installed yourself. That is local code only. Do not install the enterprise add-on packages.
7. Usage logging exists, but it is local only. Added in SDV 1.13.0 (2024-05-15, issue #1903). Synthesizers write rows to a CSV file `sdv_logs.csv` in the user data dir (`platformdirs.user_data_dir('sdv', 'sdv-dev')`). Config is copied to `sdv_logger_config.yml` in the same dir. Each row has only: level, event, timestamp, synthesizer class name, synthesizer id, number of tables, rows, and columns. No cell values, no column names. It is a plain `logging.FileHandler`, so nothing is sent anywhere.
   - Source: https://github.com/sdv-dev/SDV/blob/main/sdv/logging/logger.py, `sdv/logging/utils.py`, `sdv/logging/sdv_logger_config.yml`
   - Changelog: https://github.com/sdv-dev/SDV/blob/main/HISTORY.md
   - This is a privacy note, not a leak. The README should not claim "writes no files". It writes a small log of row and column counts. To stop it, you can pre-create a `sdv_logger_config.yml` in that dir with no loggers, or make the dir unwritable (SDV falls back to a null handler on `PermissionError`). Verify before promising this.
8. Install time: `pip install sdv` downloads packages from PyPI. That is the only network use. The wheel has no post-install hook. After install, you can run with the network off. The tool should be installed once while online, then used offline. Torch is large, so consider pinning versions and shipping a wheelhouse for fully offline install.
9. I found no setting or environment variable for telemetry because there is no telemetry. I found no docs page about telemetry, logging opt-out, or an offline mode in the docs index (https://docs.sdv.dev/sdv/llms.txt).
10. License: SDV is BUSL-1.1 (Business Source License), not an open-source licence. Check it fits the tool's use. Source: package metadata of `sdv` 2.2.0.

## Part 2. Leakage of real values

### Short answer

Real values reach the output in these cases. The first four are likely traps for a CLI.

| Column case | What happens | Real values in output? |
|---|---|---|
| `categorical`, `boolean` (the default for text columns) | Sampled from the categories seen in fit, with the seen frequencies (`UniformEncoder`). Rare values included, even a value that appears once. | Yes, always, verbatim |
| PII sdtype with `pii: False` (email, phone, name ...) | Treated as plain categorical, "the exact set of values can be reused" | Yes, verbatim |
| PII-looking column that is not detected or named by the user | Auto-detect uses the column name only, never the values. A column called `name`, `address`, `customer`, `Kunde` stays `categorical`. | Yes, verbatim |
| `id` column that is not a key and has no `regex_format` | Modelled as categorical | Yes, verbatim |
| `numerical`, `datetime` with `enforce_min_max_values=True` (default) | Output is clipped to the real min and max, so the real min and max often appear | Min and max only |
| PII sdtype with `pii: True` (default) | Faker generates new values | No, only by chance |
| `id` with `regex_format`, primary or alternate key | Generated, not copied | No, only by chance |
| `unknown` sdtype | Always random placeholders (`sdv-pii-?????` or random digits) | No |

### Details

**Categorical.** The default transformer for `categorical` and `boolean` is `UniformEncoder`. It keeps every category from the fit data with its frequency. Nulls are a category too. The copula only models the mix of columns. The labels themselves come straight from the real data. SDV has no rare-value suppression. A category that occurs once will appear in the output.
- `rdt/transformers/__init__.py` (`DEFAULT_TRANSFORMERS`), `rdt/transformers/categorical.py`: https://github.com/sdv-dev/RDT

**Metadata sdtypes and the `pii` flag.** From the docs: `pii: true` is the default for the domain sdtypes. It means "The column is sensitive, meaning the values should be anonymized." `pii: false` means "The column is not sensitive, meaning the exact set of values can be reused in the synthetic data". The docs also say "Your synthetic data will contain entirely new values that do not necessarily appear in the original data."
- https://docs.sdv.dev/sdv/reference/metadata-spec/sdtypes
- Listed domain sdtypes: `phone_number`, `email`, `ssn`, `first_name`, `last_name`, `country_code`, `administrative_unit`, `state_abbr`, `city`, `postcode`, `street_address`, `secondary_address`, `latitude`, `longitude`, `ipv4_address`, `ipv6_address`, `mac_address`, `user_agent_string`, `iban`, `swift11`, `swift8`, `credit_card_number`, `vin`, `license_plate`, plus any Faker function name (for example `passport_number`).
- In the code (`sdv/data_processing/data_processor.py`, `_get_column_config`): a column gets an `AnonymizedFaker` when its sdtype is not a default sdtype and `pii` is not `False`. If `pii` is `False` it falls to `_get_fallback_column_config`, which returns the categorical transformer. That is the real-value path.
- In 2.2.0 the `pii` key is only allowed on `unknown` and on non-core sdtypes. It is not allowed on `categorical`, `numerical`, `datetime`, `id` etc. (`_SDTYPE_KWARGS` in `sdv/metadata/_single_table.py`).
- `AnonymizedFaker` calls Faker. It never looks at real values. Because Faker draws from a limited pool, a generated value can equal a real one by chance (the docs say a 9-digit SSN can collide). SDV's own docs warn that avoiding all real values on purpose could itself leak information. Source: https://docs.sdv.dev/sdv/evaluation/privacy/anonymizing-pii-values
- `PseudoAnonymizedFaker` (a mapping from real to fake values, stored inside the model) is not used by SDV's default processing in 2.2.0. I found no use of it in the `sdv` package. If a user sets it manually, the fitted model holds a real-to-fake map.
- Locales: pass `locales=[...]` to the synthesizer. Default is `en_US`.

**Auto-detection of PII.** `Metadata.detect_from_dataframe` guesses PII sdtypes from the column name only (tokens such as `email`, `phonenumber`, `firstname`, `lastname`, `ssn`, `zipcode`, `streetaddress`, `creditcardnumber`, `iban`). `name`, `address`, `full_name`, `customer` are not in the list. Values are never inspected. So the tool must make the user review and confirm sdtypes for every text column before fit. Code: `_REFERENCE_TO_SDTYPE`, `_detect_pii_column` in `sdv/metadata/_single_table.py`.

**ID columns.**
- Primary and alternate keys: replaced by generated unique values. With `regex_format`, a `RegexGenerator` (unique, scrambled). Without it, `AnonymizedFaker` with `sdv-id-??????` for text, or `random_int` for numbers.
- A non-key `id` column without `regex_format`: goes to `_get_id_column_no_regex_format_no_key_config`, which returns the categorical transformer. Real IDs get resampled. Set `regex_format` on every `id` column, or mark such columns `unknown`/PII.
- Generated IDs can collide with real IDs by chance, mainly with short numeric regexes.
- Docs sdtype `id`: "New, randomly generated IDs based on the regex."

**Numeric and datetime.** `GaussianCopulaSynthesizer` fits a parametric marginal per column (default `beta`) plus a Gaussian copula. New values are drawn from the fitted curves, so single real values are not copied. Exceptions:
- `enforce_min_max_values=True` (default) clips output to the real min and max seen in fit. Many output rows can sit exactly on those bounds. The real min and max (for example the highest salary, the oldest date) are therefore exposed. Setting it to `False` removes the clipping but allows out-of-range values.
- `numerical_distributions={'col': 'gaussian_kde'}` is non-parametric and keeps closer to the real points. Do not use it if leakage matters.
- `enforce_rounding=True` (default) rounds to the real decimal places.
- Source: https://github.com/sdv-dev/SDV/blob/main/sdv/single_table/copulas.py
- Metadata `range_min`, `range_max`, `range_values` for categoricals also come from user-set or fitted data.

**The saved model.** `synthesizer.save()` uses cloudpickle on the whole fitted object. It contains the category lists, min and max, and so on. It is not safe to share. A CLI that only writes a CSV should not save the model.

**Whole rows.** A real row can reappear in the output if every column of it is a categorical value, or by chance. SDV does not remove such rows.

### Privacy checks that exist

- `sdv.evaluation.utils.get_pii_overlap(real, synthetic, table_name, pii_column_name)`: counts synthetic values of a PII column that also exist in the real data. It warns when the overlap is under 2% of synthetic points and says a few overlaps are not necessarily bad. `get_combination_overlap(...)`: counts column combinations that appear in both. Docs: https://docs.sdv.dev/sdv/evaluation/privacy/anonymizing-pii-values
- `sdmetrics` 0.33.0 (a dependency, local, no network): `NewRowSynthesis` (share of synthetic rows that are not an exact copy of a real row), `DCRBaselineProtection`, `DCROverfittingProtection`, `DisclosureProtection`, `DisclosureProtectionEstimate`, `CategoricalCAP`. Source: https://github.com/sdv-dev/SDMetrics/tree/main/sdmetrics/single_table
- `sdv.evaluation.single_table.run_diagnostic` / `evaluate_quality` do not include privacy. In sdmetrics 0.33.0 the single-table diagnostic report has only Data Validity and Structure. `NewRowSynthesis` is a separate metric you call yourself (its `Synthesis` report property exists, but the diagnostic does not list it). Verify before use.
- Docs overview: https://docs.sdv.dev/sdv/evaluation/privacy. It makes no guarantee. It says to "Evaluate the privacy of your data and synthesizer before sharing it with others".
- Empirical differential privacy needs the Differential Privacy bundle, an SDV Enterprise add-on. Not available. SDV Community has no differential privacy guarantee.

## Answer

- Network: safe to promise "no data leaves your machine". SDV 2.2.0 has no telemetry and no phone-home. Its only network code is the demo dataset download, which we never call. Install once online (PyPI), then run offline. Do not promise "no files written": SDV writes a local `sdv_logs.csv` with counts only. Verify offline behaviour with a real run in CI (block sockets, run fit and sample).
- Leakage: do not promise "no real values in output". Every categorical value is copied verbatim, including rare ones. `pii: False` columns are copied. PII is replaced only for columns the metadata marks as a PII sdtype, and auto-detect checks column names only. Non-key `id` columns without `regex_format` are copied. Real min and max of numeric and date columns appear by default.
- Safe design for the tool: make the user confirm sdtype for every text column. Treat any text column as PII (or `unknown`) unless the user opts in to categorical. Require `regex_format` on every `id`. Warn about rare categories. Never call demo functions, never save the model. Run `get_pii_overlap`, `NewRowSynthesis` and a DCR metric after sampling and print the results.
- README wording that is true: "No network access is used when generating data. The output can still contain real category values, and the real min/max of numeric and date columns, unless you mark columns as PII. SDV does not give a formal privacy guarantee."
