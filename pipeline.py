import glob
import pandas as pd
import sys

# glob will be used here to find all CSV files in the directory. 
# pandas is used to read and manipulate the CSV files.
# sys is used to read command line arguments.




# 1. Extract
# sys.argv is a list in Python, which contains the command-line arguments passed to the script.
# glob.glob is used to find all the pathnames matching a specified pattern according to the rules used by the Unix shell.
# files will contain a list of all pathnames matching the pattern "input/*.csv" or "test/{test_id}*.csv" if a test_id is provided as a command-line argument.
if len(sys.argv) > 1:
    test_id = sys.argv[1]
    files = glob.glob(f"test/{test_id}*.csv")
else:
    files = glob.glob("input/*.csv")


# required_columns is a set of column names that are expected to be present in each CSV file.
# set is a built-in Python data type that stores unordered collections of unique elements.
required_columns = {
    "transaction_id",
    "account_id",
    "transaction_date",
    "transaction_type",
    "amount",
    "currency"
}

dataframes = []

# read_csv is used to read a CSV file into a DataFrame.
for file in files:
    df = pd.read_csv(file)

    missing_columns = required_columns - set(df.columns)

    # file is skipped if it is missing any of the required columns, and a warning message is printed to the console.
    # file is pathname of the CSV file being processed.
    if missing_columns:
        print(
            f"Warning: {file} is missing required columns: "
            f"{missing_columns}. Skipping this file."
        )
        continue


    # Check if the DataFrame is empty
    if df.empty:
        print(f"Warning: {file} contains no transactions.")

    dataframes.append(df)



# not dataframes checks if the list of DataFrames is empty. If it is, a warning message is printed to the console, and an empty DataFrame with the required columns is created. 
# empty dataframe is created beacause there are no valid input files to process. This ensures that the rest of the code can still run without errors, even if there are no valid input files.
# pd.DataFrame is used to create a new DataFrame. The columns parameter is set to the list of required columns, which ensures that the empty DataFrame has the correct structure.
# If there are valid DataFrames, they are concatenated into a single DataFrame called daily_data.
# ignore_index=True is used to reset the index of the concatenated DataFrame, so that it has a continuous index starting from 0.
if not dataframes:
    print("Warning: No valid input files to process.")
    daily_data = pd.DataFrame(columns=list(required_columns))
else:
    daily_data = pd.concat(dataframes, ignore_index=True)



# Create an error column for every record
daily_data["error_reason"] = ""


# 2. Transform
# Transaction ID must not be missing
# isna() is a pandas function that returns a boolean Series indicating whether each element in the Series is missing (NaN) or not.
# mask is a boolean Series that is True for rows where the transaction_id is missing (NaN). 
# Series is a one-dimensional array-like object in pandas that can hold any data type.
# if mask is false, the error_reason column for that row will not be updated. If mask is true, the error_reason column for that row will be updated to include the message "transaction_id is missing; ".
# daily_data.loc[mask, "error_reason"] is used to select the rows in daily_data where mask is True and the error_reason column. The += operator is used to append the error message to the existing value in the error_reason column for those rows.
mask = daily_data["transaction_id"].isna()
daily_data.loc[mask, "error_reason"] += "transaction_id is missing; "


# Account ID must not be missing

mask = daily_data["account_id"].isna()
daily_data.loc[mask, "error_reason"] += "account_id is missing; "


# Transaction type must be CREDIT or DEBIT
# ~ is a bitwise NOT operator in Python. In this context, it is used to invert the boolean values in the Series returned by daily_data["transaction_type"].isin(["CREDIT", "DEBIT"]).
mask = ~daily_data["transaction_type"].isin(["CREDIT", "DEBIT"])
daily_data.loc[mask, "error_reason"] += "invalid transaction_type; "


# Amount must be present, numeric and greater than 0
# pd.to_numeric is a pandas function that converts a Series to a numeric type. 
# pd.numeric is used to ensure that the "amount" column is treated as a numeric type, which allows for proper validation and calculations.
# The errors="coerce" parameter is used to convert any non-numeric values to NaN (Not a Number). This allows us to easily identify and handle invalid amounts in the next step.
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
# astype(str) is used to convert the "transaction_date" column to a string type. This is necessary because the regular expression used to validate the date format expects a string input.
date_as_string = daily_data["transaction_date"].astype(str)

# valid_date_format is a boolean Series that is True for rows where the "transaction_date" matches the regular expression pattern for the YYYY-MM-DD format. 
# The pattern r"^\d{4}-\d{2}-\d{2}$" checks for four digits (year), followed by a hyphen, two digits (month), another hyphen, and two digits (day).
valid_date_format = date_as_string.str.match(
    r"^\d{4}-\d{2}-\d{2}$"
)


# datetime parsing is performed to ensure that the "transaction_date" values are valid dates. This step is necessary because a string may match the YYYY-MM-DD format but still not represent a valid date (e.g., "2023-02-30").
# parsed_dates is a Series that contains the parsed datetime values for the "transaction_date" column.
# pd.to_datetime is used to convert the "transaction_date" strings to datetime objects. The format="%Y-%m-%d" parameter specifies the expected date format, and errors="coerce" ensures that any invalid date strings are converted to NaT (Not a Time), which is pandas' representation of missing datetime values.
parsed_dates = pd.to_datetime(
    daily_data["transaction_date"],
    format="%Y-%m-%d",
    errors="coerce"
)

mask = (~valid_date_format) | parsed_dates.isna()

daily_data.loc[mask, "error_reason"] += "invalid transaction_date; "




# Transaction ID must be unique across all branch files
# duplicate_ids is a boolean Series that is True for rows where the "transaction_id" is not missing (notna()) and is duplicated (duplicated(keep=False)). 
# The keep=False parameter ensures that all occurrences of the duplicate transaction IDs are marked as duplicates, not just the first or last occurrence.
duplicate_ids = (
    daily_data["transaction_id"].notna()
    & daily_data["transaction_id"].duplicated(keep=False)
)


daily_data.loc[duplicate_ids, "error_reason"] += (
    "duplicate transaction_id; "
)



# 3. Separate valid / invalid
# valid_transactions is a DataFrame that contains only the rows from daily_data where the "error_reason" column is an empty string (i.e., no errors were found).
# copy() is used to create an independent copy of the filtered DataFrame.
valid_transactions = daily_data[
    daily_data["error_reason"] == ""
].copy()

invalid_transactions = daily_data[
    daily_data["error_reason"] != ""
].copy()

# drop the "error_reason" column from the valid_transactions DataFrame, as it is no longer needed for valid records. This step helps to clean up the DataFrame before saving it to a CSV file.
valid_transactions = valid_transactions.drop(columns=["error_reason"])


# 4. Load
# to_csv is a pandas function that writes a DataFrame to a CSV file. The index=False parameter is used to prevent pandas from writing row indices to the CSV file, which is often unnecessary for data storage and analysis.
valid_transactions.to_csv(
    "output/valid_transactions.csv",
    index=False
)

invalid_transactions.to_csv(
    "output/invalid_transactions.csv",
    index=False
)



# 5. Summary
# summary is a DataFrame that contains the counts of total input records, valid records, and invalid records.
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

