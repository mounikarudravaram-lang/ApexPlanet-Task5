
import pandas as pd
from pathlib import Path

# Project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Dataset folder
DATA_DIR = BASE_DIR / "data" / "processed"

# Find CSV dataset automatically
csv_files = [
    file for file in DATA_DIR.glob("*.csv")
    if file.name not in [
        "monthly_sales.csv",
        "category_sales.csv",
        "kpi_summary.csv",
        "automation_cleaned_data.csv"
    ]
]

if not csv_files:
    raise FileNotFoundError(
        "No input CSV found in data/processed. "
        "Place your cleaned dataset there."
    )

INPUT_FILE = csv_files[0]

print("Dataset found:", INPUT_FILE.name)

# Load dataset
df = pd.read_csv(INPUT_FILE)

print("Dataset loaded successfully!")
print("Original shape:", df.shape)

# Clean column names
df.columns = df.columns.str.strip()

# Remove duplicate rows
df = df.drop_duplicates()

# Convert date columns
for col in ["Order Date", "Ship Date"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# Convert numeric columns
for col in ["Sales", "Profit", "Quantity", "Discount"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Calculate KPIs
kpi_data = {
    "Metric": [
        "Total Sales",
        "Total Profit",
        "Total Quantity",
        "Total Orders",
        "Total Customers"
    ],
    "Value": [
        df["Sales"].sum(),
        df["Profit"].sum(),
        df["Quantity"].sum(),
        df["Order ID"].nunique(),
        df["Customer ID"].nunique()
    ]
}

kpi_df = pd.DataFrame(kpi_data)

# Monthly sales analysis
if "Order Date" in df.columns:
    df["Month"] = df["Order Date"].dt.to_period("M").astype(str)

    monthly_sales = (
        df.groupby("Month")["Sales"]
        .sum()
        .reset_index()
    )

    monthly_sales.to_csv(
        DATA_DIR / "monthly_sales.csv",
        index=False
    )

# Category sales analysis
if "Category" in df.columns:
    category_sales = (
        df.groupby("Category")["Sales"]
        .sum()
        .reset_index()
    )

    category_sales.to_csv(
        DATA_DIR / "category_sales.csv",
        index=False
    )

# Save KPI summary
kpi_df.to_csv(
    DATA_DIR / "kpi_summary.csv",
    index=False
)

# Save cleaned output
df.to_csv(
    DATA_DIR / "automation_cleaned_data.csv",
    index=False
)

print("\nAutomation completed successfully!")

print("\nKPI Summary:")
print(kpi_df)

print("\nOutput files saved in:", DATA_DIR)
