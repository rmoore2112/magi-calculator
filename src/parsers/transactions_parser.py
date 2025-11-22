"""Parser for transaction history CSV file."""

import pandas as pd
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import List

from ..models.transaction import Transaction


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime object."""
    if pd.isna(date_str) or not date_str:
        return None
    return pd.to_datetime(date_str).date()


def parse_decimal(value) -> Decimal:
    """Parse value to Decimal, handling various formats."""
    if pd.isna(value) or value == "" or value is None:
        return None

    # Remove currency symbols, commas, and parentheses for negative numbers
    if isinstance(value, str):
        value = value.replace("$", "").replace(",", "").strip()
        # Handle parentheses for negative numbers
        if value.startswith("(") and value.endswith(")"):
            value = "-" + value[1:-1]

    try:
        return Decimal(str(value))
    except:
        return None


def parse_transactions_csv(file_path: Path) -> List[Transaction]:
    """
    Parse the transaction history CSV file.

    Args:
        file_path: Path to the CSV file

    Returns:
        List of Transaction objects
    """
    df = pd.read_csv(file_path)

    transactions = []

    for _, row in df.iterrows():
        transaction = Transaction(
            date=parse_date(row.get("Date")),
            action=str(row.get("Action", "")).strip(),
            symbol=str(row.get("Symbol", "")).strip() if not pd.isna(row.get("Symbol")) else None,
            description=str(row.get("Description", "")).strip(),
            quantity=parse_decimal(row.get("Quantity")),
            price=parse_decimal(row.get("Price")),
            fees_comm=parse_decimal(row.get("Fees & Comm")) or Decimal(0),
            amount=parse_decimal(row.get("Amount")) or Decimal(0),
        )
        transactions.append(transaction)

    return transactions


def get_transactions_summary(transactions: List[Transaction]) -> dict:
    """
    Generate summary statistics for transactions.

    Args:
        transactions: List of Transaction objects

    Returns:
        Dictionary with summary statistics
    """
    dividends = [t for t in transactions if t.is_dividend]
    interest_txns = [t for t in transactions if t.is_interest]
    trades = [t for t in transactions if t.is_trade]

    dividend_income = sum(t.amount for t in dividends)
    interest_income = sum(t.amount for t in interest_txns)
    total_fees = sum(t.fees_comm for t in trades if t.fees_comm)

    return {
        "total_transactions": len(transactions),
        "num_dividends": len(dividends),
        "num_interest": len(interest_txns),
        "num_trades": len(trades),
        "dividend_income": dividend_income,
        "interest_income": interest_income,
        "total_fees": total_fees,
        "total_income_from_transactions": dividend_income + interest_income,
    }


def filter_income_transactions(transactions: List[Transaction]) -> List[Transaction]:
    """
    Filter transactions to only include income-generating transactions.

    Args:
        transactions: List of Transaction objects

    Returns:
        List of Transaction objects that are dividends or interest
    """
    return [t for t in transactions if t.is_dividend or t.is_interest]
