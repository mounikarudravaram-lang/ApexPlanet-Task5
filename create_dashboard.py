
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "dashboards"

OUTPUT_DIR.mkdir(exist_ok=True)

# Find original cleaned dataset
excluded_files = [
    "monthly_sales.csv",
    "category_sales.csv",
    "kpi_summary.csv",
    "automation_cleaned_data.csv"
]

csv_files = [
    f for f in DATA_DIR.glob("*.csv")
    if f.name not in excluded_files
]

if not csv_files:
    raise FileNotFoundError(
        "Cleaned dataset not found in data/processed!"
    )

# Load dataset
df = pd.read_csv(csv_files[0])

# Clean data
df.columns = df.columns.str.strip()

for col in ["Sales", "Profit", "Quantity"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Check required columns
if "Sales" not in df.columns or "Profit" not in df.columns:
    raise ValueError("Sales and Profit columns are required!")

# Convert order date
if "Order Date" in df.columns:
    df["Order Date"] = pd.to_datetime(
        df["Order Date"], errors="coerce"
    )

# Calculate KPIs
total_sales = df["Sales"].sum()
total_profit = df["Profit"].sum()

total_orders = (
    df["Order ID"].nunique()
    if "Order ID" in df.columns else len(df)
)

total_customers = (
    df["Customer ID"].nunique()
    if "Customer ID" in df.columns else 0
)

# Create dashboard
fig, axes = plt.subplots(2, 2, figsize=(14, 9))

fig.suptitle(
    "E-COMMERCE SALES DASHBOARD",
    fontsize=20,
    fontweight="bold"
)

# Display KPI values
fig.text(
    0.5, 0.91,
    f"Total Sales: {total_sales:,.2f}    |    "
    f"Total Profit: {total_profit:,.2f}    |    "
    f"Total Orders: {total_orders:,}    |    "
    f"Customers: {total_customers:,}",
    ha="center",
    fontsize=12
)

# 1. Monthly Sales
if "Order Date" in df.columns:
    monthly = df.dropna(subset=["Order Date"]).copy()
    monthly["Month"] = monthly["Order Date"].dt.to_period("M")

    monthly_sales = monthly.groupby("Month")["Sales"].sum()

    axes[0, 0].plot(
        monthly_sales.index.astype(str),
        monthly_sales.values,
        marker="o"
    )
    axes[0, 0].set_title("Monthly Sales Trend")
    axes[0, 0].set_xlabel("Month")
    axes[0, 0].set_ylabel("Sales")
    axes[0, 0].tick_params(axis="x", rotation=45)
else:
    axes[0, 0].text(0.5, 0.5, "Order Date unavailable",
                    ha="center")

# 2. Category-wise Sales
if "Category" in df.columns:
    category_sales = (
        df.groupby("Category")["Sales"].sum().sort_values()
    )

    axes[0, 1].bar(
        category_sales.index,
        category_sales.values
    )
    axes[0, 1].set_title("Category-wise Sales")
    axes[0, 1].set_xlabel("Category")
    axes[0, 1].set_ylabel("Sales")
else:
    axes[0, 1].text(0.5, 0.5, "Category unavailable",
                    ha="center")

# 3. Region-wise Sales
if "Region" in df.columns:
    region_sales = (
        df.groupby("Region")["Sales"].sum().sort_values()
    )

    axes[1, 0].bar(
        region_sales.index,
        region_sales.values
    )
    axes[1, 0].set_title("Region-wise Sales")
    axes[1, 0].set_xlabel("Region")
    axes[1, 0].set_ylabel("Sales")
else:
    axes[1, 0].text(0.5, 0.5, "Region unavailable",
                    ha="center")

# 4. Category-wise Profit
if "Category" in df.columns:
    category_profit = (
        df.groupby("Category")["Profit"].sum()
    )

    axes[1, 1].bar(
        category_profit.index,
        category_profit.values
    )
    axes[1, 1].set_title("Category-wise Profit")
    axes[1, 1].set_xlabel("Category")
    axes[1, 1].set_ylabel("Profit")
else:
    axes[1, 1].text(0.5, 0.5, "Category unavailable",
                    ha="center")

# Improve layout
for ax in axes.flat:
    ax.grid(axis="y", alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.87])

# Save dashboard
dashboard_path = OUTPUT_DIR / "dashboard.png"

plt.savefig(
    dashboard_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("Dashboard created successfully!")
print("Saved at:", dashboard_path)
