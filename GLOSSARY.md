# Glossary

**Source CSV**
The user's real, possibly confidential, single-table CSV file given to the tool as input. It never leaves the user's machine.
_Avoid_: real data, input data, original

**Synthetic CSV**
The output: a CSV with the same columns, types and structure as the Source CSV, but whose rows are generated rather than copied.
_Avoid_: fake data, twin, synthetic proxy (use **Structural proxy** for its purpose)

**Structural proxy**
The purpose a Synthetic CSV serves: safe to share, and realistic enough to write and test analysis code against. It does not promise statistical fidelity good enough to draw conclusions from.
_Avoid_: faithful copy

**Identifying value**
A value that can point to a real person or company: an email, name, address, card number, free text, or a Rare category. It must never appear in a Synthetic CSV.
_Avoid_: real value (too broad)

**Shared label**
A category value that describes the business, not a person, such as a room type or a rewards tier. It may appear in a Synthetic CSV.
_Avoid_: category (ambiguous)

**Rare category**
A category value that appears in so few rows of the Source CSV that it could identify someone. It counts as an Identifying value.

**Metadata**
A description of the Source CSV's shape: column names and each column's semantic type (e.g. email, address, datetime, categorical, numerical, ID). It holds no row values.
_Avoid_: schema, blueprint

**Settings file**
A file the user can edit that lists every column of a Source CSV, its type, and what to do with it (keep, drop or disguise). It holds column names only, never data values.
_Avoid_: config, metadata file
