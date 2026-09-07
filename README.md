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

## Output

The pipeline generates:

* `output/valid_transactions.csv` - valid transactions
* `output/invalid_transactions.csv` - invalid transactions with error reasons
* `output/summary.csv` - total, valid, and invalid record counts

The pipeline automatically processes CSV files placed in the `input` directory following the expected structure.
