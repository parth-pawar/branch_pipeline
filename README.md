# Week 3 - Branch Transaction File Processing Pipeline

## Overview

This project processes daily transaction CSV files received from multiple bank branches.

The pipeline reads branch files, validates transactions, detects duplicates across files, separates valid and invalid records, generates data-quality metrics, and records important execution events in a log file.

The Week 3 version focuses on making the Week 2 pipeline more testable, observable, and safer to run under realistic conditions.

## Technologies

* Python
* Pandas
* pytest

## Project Structure

```text
week2_branch_pipeline/
├── input/                  # Branch transaction CSV files
├── test/                   # Test CSV files for pipeline scenarios
├── tests/                  # Automated pytest tests
│   ├── test_validation.py
│   └── test_pipeline.py
├── output/                 # Generated output files
├── logs/
│   └── pipeline.log        # Pipeline execution log
├── pipeline.py             # Main pipeline
├── validation.py           # Transaction validation functions
├── config.py               # Validation constants and rules
├── dq_metrics.py           # Data-quality metric generation
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## Validation Rules

The pipeline checks:

* Required columns are present
* Transaction ID is not missing
* Account ID is not missing
* Transaction date follows `YYYY-MM-DD` and represents a valid date
* Transaction type is `CREDIT` or `DEBIT`
* Amount is numeric and greater than 0
* Currency is `USD`
* Transaction IDs are unique across all successfully read branch files

All applicable row-level errors are retained in the `error_reason` column.

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

```powershell
py -m pip install -r requirements.txt
```

## Run the Pipeline

From the project root directory:

```powershell
py pipeline.py
```

The pipeline automatically creates the `output/` directory if it does not already exist.

It processes CSV files found in the `input/` directory.

The terminal displays a short run summary:

```text
Pipeline completed successfully.
Total records: 24
Valid records: 10
Invalid records: 14
```

Detailed execution events are written to:

```text
logs/pipeline.log
```

## Week 2 to Week 3 Changes

The main Week 2 weaknesses addressed in Week 3 were testability, observability, and handling of realistic file-level failures.

Changes include:

* Moved validation rules into reusable functions in `validation.py`.
* Moved shared validation constants into `config.py`.
* Added `dq_metrics.py` for automated data-quality reporting.
* Added structured logging using Python's built-in `logging` module.
* Added deliberate handling for empty, malformed, unreadable, and schema-invalid files.
* The output directory is created automatically when required.
* Preserved multiple validation errors for the same row.
* Preserved source-file information for processed records.
* Added automated pytest unit, integration, and regression tests.
* Kept the original `summary.csv` while adding a more detailed `dq_summary.csv`.

These changes make the pipeline easier to test and provide more evidence about what happened during a run.

## Data-Quality Metrics

The pipeline generates:

```text
output/dq_summary.csv
```

The DQ summary includes:

* Files discovered
* Files successfully read
* Files skipped
* Total rows read
* Valid rows
* Invalid rows
* Rejection rate
* Missing transaction IDs
* Missing account IDs
* Invalid transaction types
* Invalid amounts
* Invalid transaction dates
* Invalid currencies
* Duplicate transaction IDs

The original summary is also retained:

```text
output/summary.csv
```

It contains the total, valid, and invalid record counts.

## Output Files

The pipeline generates:

* `output/valid_transactions.csv` - valid transactions
* `output/invalid_transactions.csv` - invalid transactions with their error reasons
* `output/summary.csv` - basic total, valid, and invalid record counts
* `output/dq_summary.csv` - detailed data-quality metrics
* `logs/pipeline.log` - operational execution events

## Testing Strategy

Automated tests are run using pytest.

Run the complete test suite:

```powershell
py -m pytest -v
```

### Unit Tests

`tests/test_validation.py` tests individual validation functions in isolation.

The unit tests cover:

* Positive, negative, and non-numeric amounts
* Correct and incorrect date formats
* Impossible dates
* Allowed and invalid transaction types
* Allowed and invalid currencies

### Integration Tests

`tests/test_pipeline.py` runs the complete pipeline and checks its generated outputs.

The integration tests cover:

* Skipping a file with a missing required column
* Preserving multiple validation errors for one transaction
* Producing the expected output from the original branch files

### Regression Test

The original three branch files are used as a regression test.

The expected result remains:

```text
Total records: 24
Valid records: 10
Invalid records: 14
```

This protects the Week 2 business behavior while allowing the pipeline to evolve.

## Handling File-Level Problems

The pipeline deliberately handles realistic run conditions.

Examples include:

* No matching CSV files
* Empty files
* Missing required columns
* Malformed or unreadable files
* A bad file alongside valid files
* All candidate files being rejected
* Missing output directory

File-level events are recorded in:

```text
logs/pipeline.log
```

Warnings and errors do not prevent valid files from being processed when recovery is possible.

## Limitations and Future Improvements

* The pipeline currently processes CSV files only. Support for additional input formats such as Excel or Parquet could be added later.
* Validation rules are currently configured in Python code. A future version could make some business rules configurable without changing the source code.
* The pipeline currently writes CSV output files locally. A production version could store outputs in a database or cloud storage system.
* More automated tests could be added for logging behavior and individual file-handling scenarios.

## Engineering Reflection

The hardest Week 2 weakness to harden was handling failures at the file level without allowing one problematic file to affect the processing of other valid files. In the original pipeline, the main focus was on validating transaction rows and producing the correct valid and invalid outputs. Week 3 required thinking more about what could happen before row validation even starts, such as an unreadable CSV, malformed CSV content, a file with missing columns, an empty file, or a directory containing no usable files.

I changed the pipeline so that file reading, schema checking, validation, output generation, and DQ metric generation are handled as separate responsibilities. Files that cannot be safely processed are skipped with a warning or error, while other valid files can continue through the pipeline. I also added Python's built-in logging module so important execution events are recorded in `logs/pipeline.log` instead of relying only on terminal output.

Another important improvement was automated testing. The Week 3 test suite now includes unit tests for individual validation rules, integration tests that execute the pipeline and inspect its outputs, and a regression test using the original three branch files.

The evidence that gives me more confidence now is not just the final output counts. The pipeline produces both operational evidence through `pipeline.log` and data-quality evidence through `dq_summary.csv`. The complete pytest suite also passes, including the regression result of 24 total records, 10 valid records, and 14 invalid records. Together, these checks provide stronger confidence that the pipeline still produces the expected business result while handling realistic failure conditions more safely.


### Sample Error Scenario Log

The following example shows a successful pipeline run where a malformed CSV file is encountered. The malformed file is logged as an error and skipped, while the remaining valid files continue to be processed.

```text
2026-09-16 12:25:12,007 - INFO - Pipeline started
2026-09-16 12:25:12,008 - INFO - Reading file: input\BR001_20260906_TRANSACTION.csv
2026-09-16 12:25:12,010 - INFO - Successfully read file: input\BR001_20260906_TRANSACTION.csv
2026-09-16 12:25:12,011 - INFO - Reading file: input\BR002_20260906_TRANSACTION.csv
2026-09-16 12:25:12,011 - INFO - Successfully read file: input\BR002_20260906_TRANSACTION.csv
2026-09-16 12:25:12,012 - INFO - Reading file: input\BR003_20260906_TRANSACTION.csv
2026-09-16 12:25:12,013 - INFO - Successfully read file: input\BR003_20260906_TRANSACTION.csv
2026-09-16 12:25:12,013 - INFO - Reading file: input\T11_MALFORMED.csv
2026-09-16 12:25:12,013 - ERROR - Could not read file input\T11_MALFORMED.csv: Error tokenizing data. C error: EOF inside string starting at row 2. Skipping this file.
2026-09-16 12:25:12,036 - INFO - Pipeline completed successfully.
```

The malformed file causes a `ParserError`, which is logged at the `ERROR` level and skipped without stopping the entire pipeline.



### Great Expectations Comparison

Great Expectations (GX) is a data-quality framework that provides a structured way to define and validate expectations about datasets. An expectation is a rule describing what the data should satisfy, such as a column containing no missing values, a numeric column having values greater than zero, or a column containing only a defined set of values.

In the current project, these checks are implemented directly using Pandas in `validation.py`. For example, the pipeline checks that transaction amounts are numeric and greater than zero, transaction types are either `CREDIT` or `DEBIT`, currency is `USD`, dates follow the required format, and transaction IDs are not duplicated. The project also has custom DQ metrics in `dq_metrics.py`, logging in `pipeline.log`, and pytest tests for the validation and pipeline behavior.

Great Expectations could add several capabilities on top of this approach:

* **Structured expectations:** Data-quality rules could be defined in a standardized framework rather than implementing each check manually.
* **Reusable validation rules:** Expectations can be reused across different datasets or pipelines, reducing the need to write similar validation logic repeatedly.
* **Validation results:** GX provides structured results showing which expectations passed or failed, making validation outcomes easier to inspect.
* **Data-quality documentation:** GX can generate human-readable documentation describing the expectations and their validation results.
* **More standardized reporting:** Instead of maintaining all validation reporting logic manually, GX provides tools for organizing and presenting data-quality results.
* **Scalability:** As the number of datasets, columns, and validation rules grows, a dedicated data-quality framework can provide more structure for managing those checks.

However, Great Expectations would also introduce an additional framework and dependency. For this relatively small pipeline, the existing Pandas validation, custom DQ metrics, logging, and pytest tests are sufficient and easier to keep lightweight. Therefore, Great Expectations was researched as a possible future improvement rather than implemented in the current project.
