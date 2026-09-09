# Week 2 - Branch Transaction File Processing Pipeline

## Overview

This project processes daily transaction CSV files received from multiple bank branches.

The pipeline reads all branch files, validates the transactions, separates valid and invalid records, and generates summary output files.

## Technologies

* Python
* Pandas

## Project Structure

```text
week2_branch_pipeline/
├── input/                  # Branch transaction CSV files
├── test/                   # Test CSV files for pipeline testing
├── output/                 # Generated output files
├── pipeline.py             # Main pipeline
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## Validation Rules

The pipeline checks:

* Required columns are present
* Transaction ID is not missing
* Account ID is not missing
* Transaction date is valid and follows `YYYY-MM-DD`
* Transaction type is `CREDIT` or `DEBIT`
* Amount is numeric and greater than 0
* Currency is `USD`
* Transaction IDs are unique across all branch files

All applicable errors are recorded in the `error_reason` column.

## Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Pipeline

From the project root directory:

```bash
python pipeline.py
```

## Testing

The pipeline includes test CSV files in the `test/` folder for checking different scenarios.

### Run a test individually

You can run a specific test without moving the test file into the `input/` folder.

Use:

```bash
python pipeline.py <TEST_ID>
```

For example:

```bash
python pipeline.py T01
python pipeline.py T02
python pipeline.py T03
```

The pipeline will automatically find the corresponding test file in the `test/` folder.

For example:

```text
python pipeline.py T04
```

will process files beginning with `T04` in the `test/` folder.

### Test together with other input files

You can also copy or drag a test CSV file from the `test/` folder into the `input/` folder.

Then run the normal pipeline:

```bash
python pipeline.py
```

In this mode, the pipeline processes all CSV files currently present in the `input/` folder. This allows you to test a scenario together with the normal branch transaction files.

For example, if you place `T02_HEADER_ONLY.csv` in the `input/` folder alongside the original branch files:

```text
input/
├── BR001_20260906_TRANSACTION.csv
├── BR002_20260906_TRANSACTION.csv
├── BR003_20260906_TRANSACTION.csv
└── T02_HEADER_ONLY.csv
```

run:

```bash
python pipeline.py
```

The pipeline will process all four files and report the header-only file with a warning.

After testing, move the test file back to the `test/` folder to keep the project organized.

## Output

The pipeline generates:

* `output/valid_transactions.csv` - valid transactions
* `output/invalid_transactions.csv` - invalid transactions with error reasons
* `output/summary.csv` - total, valid, and invalid record counts

The pipeline automatically processes CSV files placed in the `input` directory following the expected structure.
