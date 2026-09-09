import glob
import pandas as pd
import sys


# 1. Extract
if len(sys.argv) > 1:
    test_id = sys.argv[1]
    files = glob.glob(f"test/{test_id}*.csv")
else:
    files = glob.glob("input/*.csv")

required_columns = {
    "transaction_id",
    "account_id",
    "transaction_date",
    "transaction_type",
    "amount",
    "currency"
}

dataframes = []

for file in files:
    df = pd.read_csv(file)

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        print(
            f"Warning: {file} is missing required columns: "
            f"{missing_columns}. Skipping this file."
        )
        continue

    if df.empty:
        print(f"Warning: {file} contains no transactions.")

    dataframes.append(df)

if not dataframes:
    print("Warning: No valid input files to process.")
    daily_data = pd.DataFrame(columns=list(required_columns))
else:
    daily_data = pd.concat(dataframes, ignore_index=True)

# Create an error column for every record
daily_data["error_reason"] = ""


# Transaction ID must not be missing
mask = daily_data["transaction_id"].isna()
daily_data.loc[mask, "error_reason"] += "transaction_id is missing; "


# Account ID must not be missing
mask = daily_data["account_id"].isna()
daily_data.loc[mask, "error_reason"] += "account_id is missing; "


# Transaction type must be CREDIT or DEBIT
mask = ~daily_data["transaction_type"].isin(["CREDIT", "DEBIT"])
daily_data.loc[mask, "error_reason"] += "invalid transaction_type; "


# Amount must be present, numeric and greater than 0
daily_data["amount"] = pd.to_numeric(
    daily_data["amount"],
    errors="coerce"
)

mask = daily_data["amount"].isna()
daily_data.loc[mask, "error_reason"] += "amount is missing or not numeric; "

mask = daily_data["amount"].notna() & (daily_data["amount"] <= 0)
daily_data.loc[mask, "error_reason"] += "amount must be greater than 0; "


# Currency must be USD
mask = daily_data["currency"] != "USD"
daily_data.loc[mask, "error_reason"] += "currency must be USD; "


# Transaction date must be a real date in YYYY-MM-DD format
date_as_string = daily_data["transaction_date"].astype(str)

valid_date_format = date_as_string.str.match(
    r"^\d{4}-\d{2}-\d{2}$"
)

parsed_dates = pd.to_datetime(
    daily_data["transaction_date"],
    format="%Y-%m-%d",
    errors="coerce"
)

mask = (~valid_date_format) | parsed_dates.isna()

daily_data.loc[mask, "error_reason"] += "invalid transaction_date; "


# Transaction ID must be unique across all branch files
duplicate_ids = (
    daily_data["transaction_id"].notna()
    & daily_data["transaction_id"].duplicated(keep=False)
)

daily_data.loc[duplicate_ids, "error_reason"] += (
    "duplicate transaction_id; "
)



# 3. Separate valid / invalid
valid_transactions = daily_data[
    daily_data["error_reason"] == ""
].copy()

invalid_transactions = daily_data[
    daily_data["error_reason"] != ""
].copy()

valid_transactions = valid_transactions.drop(columns=["error_reason"])


# 4. Load
valid_transactions.to_csv(
    "output/valid_transactions.csv",
    index=False
)

invalid_transactions.to_csv(
    "output/invalid_transactions.csv",
    index=False
)



# 5. Summary

summary = pd.DataFrame({
    "metric": [
        "total input records",
        "valid records",
        "invalid records"
    ],
    "count": [
        len(daily_data),
        len(valid_transactions),
        len(invalid_transactions)
    ]
})

summary.to_csv(
    "output/summary.csv",
    index=False
)


print("Pipeline completed successfully.")
print(f"Total records: {len(daily_data)}")
print(f"Valid records: {len(valid_transactions)}")
print(f"Invalid records: {len(invalid_transactions)}")

