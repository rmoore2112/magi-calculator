# MAGI Calculator

A Python web application for calculating Modified Adjusted Gross Income (MAGI) based on investment transaction data and additional income sources.

## Overview

The MAGI Calculator processes brokerage transaction data (realized gains/losses and transaction history) and combines it with user-provided income and deduction information to estimate your Modified Adjusted Gross Income (MAGI). MAGI is used to determine eligibility for various tax benefits, healthcare subsidies, and Medicare IRMAA surcharges.

## Features

- **Investment Data Processing**: Automatically parses and analyzes:
  - Realized capital gains and losses (short-term and long-term)
  - Dividend income
  - Interest income
  - Wash sale tracking

- **Comprehensive Income Calculation**: Supports multiple income sources:
  - Wages (W-2 income)
  - Business income (self-employment)
  - Rental income
  - Retirement income
  - Social Security benefits
  - Tax-exempt interest

- **Deductions & Adjustments**:
  - Standard or itemized deductions
  - Student loan interest
  - Traditional IRA contributions
  - HSA contributions
  - Self-employment tax

- **Multiple Filing Statuses**:
  - Single
  - Married Filing Jointly
  - Married Filing Separately
  - Head of Household
  - Qualifying Widow(er)

- **Interactive HTML Reports**:
  - Summary metrics (Total Income, AGI, MAGI)
  - Income breakdown by category
  - Capital gains analysis with charts
  - IRMAA tier determination
  - Detailed transaction tables
  - Interactive visualizations using Plotly

## Installation

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

1. Clone or navigate to the repository:
   ```bash
   cd magi-calculator
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

3. Place your CSV files in the `data/` directory:
   - Realized gains/losses CSV (e.g., `Brokerage_GainLoss_Realized_Details_*.csv`)
   - Transaction history CSV (e.g., `Brokerage_*_Transactions_*.csv`)

## Usage

### Running the Application

**Quick Start** (recommended):

```bash
./run.sh
```

The `run.sh` script will automatically:
- Check for and install uv if needed
- Verify data files exist
- Sync dependencies
- Start the web server

**Manual Start**:

```bash
uv run python -m src.main
```

The application will start on `http://127.0.0.1:5001`

Open your web browser and navigate to the URL to access the calculator.

**Note**: Port 5001 is used to avoid conflicts with macOS AirPlay Receiver (which uses port 5000).

### Input Form

1. **Tax Filing Information**: Select your filing status and tax year
2. **Additional Income**: Enter income from sources beyond your investment accounts
3. **Deductions & Adjustments**: Specify deductions and adjustments to income
4. Click **Calculate MAGI** to generate your report

### Understanding the Report

The report includes:

- **Key Metrics**: Total Income, AGI, and MAGI displayed prominently
- **Income Breakdown**: Pie chart and detailed tables showing income sources
- **Capital Gains Analysis**: Bar chart comparing short-term vs long-term gains
- **Deductions**: Summary of all adjustments to income
- **Transaction Details**: Complete tables of realized gains and income transactions
- **IRMAA Tier**: Medicare premium surcharge tier based on your MAGI

## Project Structure

```
magi-calculator/
├── pyproject.toml          # Project configuration and dependencies
├── README.md               # This file
├── .gitignore             # Git ignore patterns
├── data/                  # CSV data files (not tracked in git)
│   ├── *GainLoss*.csv
│   └── *Transactions*.csv
├── src/
│   ├── __init__.py
│   ├── main.py            # Application entry point
│   ├── parsers/           # CSV parsing modules
│   │   ├── gains_parser.py
│   │   └── transactions_parser.py
│   ├── calculators/       # MAGI calculation logic
│   │   ├── income_aggregator.py
│   │   ├── magi_calculator.py
│   │   └── tax_rules.py
│   ├── models/            # Data models
│   │   ├── transaction.py
│   │   ├── income.py
│   │   └── user_inputs.py
│   └── web/               # Flask web application
│       ├── routes.py
│       ├── templates/     # HTML templates
│       │   ├── base.html
│       │   ├── index.html
│       │   ├── report.html
│       │   └── error.html
│       └── static/        # CSS and JS
│           └── style.css
└── tests/                 # Unit tests
```

## CSV File Format

### Realized Gains CSV

Expected columns:
- Symbol, Name
- Opened Date, Closed Date
- Quantity, Proceeds Per Share, Cost Per Share
- Proceeds, Cost Basis (CB)
- Gain/Loss ($), Gain/Loss (%)
- Long Term Gain/Loss, Short Term Gain/Loss
- Term
- Wash Sale?, Disallowed Loss

### Transactions CSV

Expected columns:
- Date
- Action (e.g., "Cash Dividend", "Bond Interest", "Buy", "Sell")
- Symbol, Description
- Quantity, Price
- Fees & Comm
- Amount

## Tax Year Defaults

The calculator includes 2025 standard deduction amounts:
- Single: $15,000
- Married Filing Jointly: $30,000
- Married Filing Separately: $15,000
- Head of Household: $22,500
- Qualifying Widow(er): $30,000

IRMAA thresholds are approximate 2025 values and may need adjustment.

## Important Notes

- This calculator provides **estimates only** and should not be considered professional tax advice
- MAGI calculations can vary depending on specific circumstances
- Always consult with a qualified tax professional for tax planning and filing
- The application stores no data permanently; all calculations are session-based
- CSV files in the `data/` directory are excluded from git to protect sensitive information

## Development

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black src/
```

### Linting

```bash
uv run ruff check src/
```

## Dependencies

- **Flask**: Web framework
- **pandas**: CSV parsing and data manipulation
- **plotly**: Interactive visualizations
- **python-dateutil**: Date parsing utilities

## License

This project is for personal use. Modify as needed for your requirements.

## Disclaimer

This software is provided "as is" without warranty of any kind. The calculations are estimates and should not be used for actual tax filing without verification by a qualified tax professional. The authors are not responsible for any financial decisions made based on this tool's output.
