# csv-synth

## 1. What it is

`csv-synth` is a free command-line tool. It reads one CSV file and writes a fake copy with the same columns and structure. You can share the fake copy safely.

> Your data never leaves your computer. After installing, the tool makes no network connections.
> ([proof: `test_offline.py`](tests/test_offline.py))

## 2. Typical use

1. Make a synthetic copy of your confidential CSV.
2. Share the copy with an AI tool or a colleague.
3. Get analysis code back.
4. Run that code on your real data, on your own computer.

## 3. Install

Install [uv](https://docs.astral.sh/uv/), then install the tool from GitHub:

```
uv tool install git+https://github.com/dptolle/data-synthesizer
```

Works on Windows, Linux and Apple-chip Macs (Git Bash, PowerShell or a Mac/Linux shell). Python 3.10 to 3.14.

**Linux tip: avoid the huge torch download.** By default, Linux installs a version of torch with several GB of GPU files. The tool does not use them. Use the CPU-only index instead:

```
uv tool install --index https://download.pytorch.org/whl/cpu git+https://github.com/dptolle/data-synthesizer
```

The CI workflow ([`tests.yml`](.github/workflows/tests.yml)) uses the same index on Linux.

## 4. Quick start

The repo has an [`examples/`](examples) folder with two fake hotel CSVs. Every value in them is 100% fake. Download them (or clone the repo), then run:

```
csv-synth inspect examples/hotel_sample.csv
csv-synth generate examples/hotel_sample.csv
```

`examples/hotel_sample_messy.csv` has the same rows in a European Excel style: `;` as separator, a decimal comma, dates like `31.12.2024` and cp1252 encoding. Use it to see the tool detect the format.

The files were made by [`scripts/make_sample_csv.py`](scripts/make_sample_csv.py) with Faker and a fixed seed (42), so the script writes the same files every time. You do not need the script or Faker to use the tool.

This writes two files next to the input, inside `examples/`:

- `hotel_sample_settings.csv`: the Settings file (written by `inspect`, read by `generate`).
- `hotel_sample_synthetic.csv`: the Synthetic CSV.

`generate` prints a short summary. It lists the faked, disguised and dropped columns by name. It shows the result of the privacy check. It never prints data values. It also prints the seed it used. Pass `--seed` with that number to repeat the run.

You can skip `inspect`. Then `generate` guesses the settings and writes them out for next time.

## 5. Workflow

1. **Inspect.** `csv-synth inspect data.csv` guesses a type and an action for every column. It writes them to `data_settings.csv`. It warns if a date column mixes several date styles. It then leaves that column's format empty, so you must set it in the Settings file.
2. **Edit.** Open the Settings file in Excel or a text editor. Fix wrong types. Drop columns you do not need. Mark secret labels as `disguise`.
3. **Generate.** `csv-synth generate data.csv` reads the Settings file and writes `data_synthetic.csv`.

Good to know:

- `generate` never overwrites a Settings file it has just read. Not even with `--force`.
- Use `--settings my_file.csv` to keep several versions. The same name works for both commands.
- You can reuse a Settings file on a new export of the same data. If the columns do not match, the tool stops and lists the differences.
- The tool refuses to overwrite any other existing output file unless you add `--force`.
- The output uses the same separator, encoding, decimal mark and date format as your input. Code written for one file works on the other.

## 6. Settings file

A CSV with one row per column of your data. It holds column names and settings only. It never holds data values, so it is safe to share too. It is saved as UTF-8 with a BOM so that Excel shows special letters correctly. It uses the same separator as your data.

```
column,type,action,format
email,email,keep,
check_in,date,keep,%Y-%m-%d
room_type,category,disguise,
```

**Types**

| Type | Meaning | What happens |
|---|---|---|
| `email`, `name`, `address`, `phone`, `card` | Personal data | Replaced by fake values |
| `id` | Identifiers | Replaced by fake identifiers |
| `text` | Free text such as notes | Replaced by fake sentences of similar length |
| `category` | A short list of labels | Learned. Rare labels are merged into "Other" |
| `number` | Numbers | Learned. The real minimum and maximum are not copied |
| `date` | Dates | Learned. Written in the `format` you set |

**Actions**

| Action | Meaning |
|---|---|
| `keep` | Use the column |
| `drop` | Leave the column out of the output |
| `disguise` | Replace each label with a stand-in such as `room_type_1`. Only valid for `category` columns |

**Format** is a date format such as `%d.%m.%Y`. It is filled in for `date` columns and empty for the rest.

The tool finds personal data by looking at the values, not only the column names. A column called `contact` that holds emails is still faked. Check the types anyway.

## 7. All options

| Option | Commands | Default | What it does |
|---|---|---|---|
| `-o`, `--output <file>` | generate | `<input>_synthetic.csv` next to the input | Name of the Synthetic CSV |
| `--settings <file>` | both | `<input>_settings.csv` next to the input | `inspect`: where to write. `generate`: read it if it exists, otherwise write it there |
| `--force` | both | off | Allow overwriting existing output files |
| `--rows <n>` | generate | Row count of the input | Rows to generate |
| `--seed <n>` | generate | Random, and printed | Makes the output repeatable |
| `--fit-rows <n>` | generate | 100,000 | Learn from a random sample of this many rows if the input is larger |
| `--rare-threshold <n>` | generate | 5 | Labels seen in fewer rows become "Other" |
| `--disguise-all` | generate | off | Disguise every `category` column. When `generate` writes the Settings file, it records `disguise` for them. A Settings file that already exists is not changed |
| `--delimiter <c>` | both | Detected | Separator of the input |
| `--encoding <name>` | both | Detected (UTF-8, then cp1252) | Encoding of the input |
| `--decimal <c>` | both | Detected | Decimal mark of the input (`,` or `.`) |

Run `csv-synth inspect --help` or `csv-synth generate --help` for the same list in the terminal.

## 8. Privacy

**What is promised**

> Your data never leaves your computer. After installing, the tool makes no network connections.
> ([proof: `test_offline.py`](tests/test_offline.py))

> Emails, names, addresses, phone numbers, card numbers and free text from your file never appear in the output. The tool checks this before it saves.
> ([proof: `test_personal_columns.py`](tests/test_personal_columns.py), [`test_free_text.py`](tests/test_free_text.py), [`test_privacy.py`](tests/test_privacy.py), [`test_generate.py`](tests/test_generate.py))

> The output still shows your column names, common category labels and overall patterns. Check it before you share it.
> ([proof: `test_disguise.py`](tests/test_disguise.py), [`test_rare_cli.py`](tests/test_rare_cli.py), [`test_generate.py`](tests/test_generate.py))

**What the privacy check does**

- It compares the output with your data before saving.
- If any personal or free-text value appears in the output, the tool saves no file. It names the columns and suggests a change to the Settings file. It still writes the Settings file (unless it read one), so you can apply the fix.
- If a whole real row appears in the output, the tool saves the file and prints a warning with the count only. In small tables this can happen by chance.

**Other protections**

- Category labels seen in fewer than 5 rows are merged into "Other". Change this with `--rare-threshold` ([test](tests/test_rare_cli.py)).
- Real minimum and maximum values of numbers and dates are not reproduced ([number test](tests/test_rare_cli.py), [date test](tests/test_dates.py)).
- Secret labels can be replaced by stand-ins. The mapping is kept in memory only and is written to no file ([test](tests/test_disguise.py)).
- The trained model is never saved.
- Summaries and messages contain column names and counts, never data values ([test](tests/test_privacy.py)).

**What is not promised**

- Column names stay visible. Common category labels stay visible, unless you disguise them. Overall patterns stay visible. Check the output before you share it.
- **This tool is not a legal guarantee of anonymisation**, for example under the GDPR. Follow your own organisation's rules.
- The tool writes only the Synthetic CSV and the Settings file next to your data. But the SDV library it uses copies a small settings file for its own logging into your user data folder (for example `%LOCALAPPDATA%\sdv-dev\sdv` on Windows). It holds no data from your file. The linked test only checks that a run adds no other files to the data folder ([test](tests/test_generate.py)). It does not check your user data folder.
- If your output encoding cannot hold a character, the tool replaces it with `?` and warns you with the count (the warning does not name the character).
- If a date column uses slashes and is ambiguous (in every date both numbers are 12 or less, such as `03/04/2024`), the tool assumes month first. It warns you and names the column. `inspect` and a `generate` that has no Settings file yet give this warning. Set the right format in the Settings file.

## 9. Limits

- **Structural proxy only.** The fake file has the right structure. Its statistics are not reliable enough for conclusions. Use it to write code, not to find results.
- One table (one CSV file) per run.
- The install is large: about 840 MB (with the CPU-only torch tip on Linux).
- Intel Macs are not supported.
- Large files: the tool learns from a random sample of 100,000 rows by default. Change this with `--fit-rows`. A run on 100,000 rows takes about 90 seconds on a laptop ([test](tests/test_large_files.py)).
- The method is always GaussianCopula. You cannot choose another.

## 10. License

This tool is MIT licensed (see [LICENSE](LICENSE)).

It uses [SDV](https://github.com/sdv-dev/SDV) as a dependency. SDV and some of its parts (RDT, Copulas) are licensed under the Business Source License 1.1 (BSL). The BSL is not an open-source license. Using SDV on your own computer, including at work, is allowed. Hosted commercial services for outside third parties are not covered. Read the [SDV license](https://github.com/sdv-dev/SDV/blob/main/LICENSE) before you build one. Some organisations ban non-open-source licenses. Ask yours if unsure.
