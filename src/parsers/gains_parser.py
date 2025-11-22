"""Parser for realized gains/losses CSV file."""

import pandas as pd
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import List

from ..models.transaction import RealizedGain


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


def parse_quantity(value) -> int:
    """Parse quantity value, handling commas."""
    if pd.isna(value) or value == "" or value is None:
        return 0

    if isinstance(value, str):
        value = value.replace(",", "").strip()

    try:
        return int(value)
    except:
        return 0


def parse_gains_csv(file_path: Path) -> List[RealizedGain]:
    """
    Parse the realized gains/losses CSV file.

    Args:
        file_path: Path to the CSV file

    Returns:
        List of RealizedGain objects
    """
    # Skip the first row (title row) and use the second row as headers
    df = pd.read_csv(file_path, skiprows=1)

    gains = []

    for _, row in df.iterrows():
        # Parse wash sale flag
        wash_sale = str(row.get("Wash Sale?", "")).strip().lower() == "yes"

        gain = RealizedGain(
            symbol=str(row.get("Symbol", "")).strip(),
            name=str(row.get("Name", "")).strip(),
            closed_date=parse_date(row.get("Closed Date")),
            opened_date=parse_date(row.get("Opened Date")),
            quantity=parse_quantity(row.get("Quantity")),
            proceeds_per_share=parse_decimal(row.get("Proceeds Per Share")) or Decimal(0),
            cost_per_share=parse_decimal(row.get("Cost Per Share")) or Decimal(0),
            proceeds=parse_decimal(row.get("Proceeds")) or Decimal(0),
            cost_basis=parse_decimal(row.get("Cost Basis (CB)")) or Decimal(0),
            gain_loss=parse_decimal(row.get("Gain/Loss ($)")) or Decimal(0),
            gain_loss_pct=parse_decimal(row.get("Gain/Loss (%)")),
            long_term_gain_loss=parse_decimal(row.get("Long Term Gain/Loss")),
            short_term_gain_loss=parse_decimal(row.get("Short Term Gain/Loss")),
            term=str(row.get("Term", "")).strip(),
            wash_sale=wash_sale,
            disallowed_loss=parse_decimal(row.get("Disallowed Loss")),
        )
        gains.append(gain)

    return gains


def get_gains_summary(gains: List[RealizedGain]) -> dict:
    """
    Generate summary statistics for realized gains.

    Args:
        gains: List of RealizedGain objects

    Returns:
        Dictionary with summary statistics
    """
    total_st_gains = sum(
        g.short_term_gain_loss for g in gains
        if g.short_term_gain_loss is not None
    )
    total_lt_gains = sum(
        g.long_term_gain_loss for g in gains
        if g.long_term_gain_loss is not None
    )

    return {
        "total_transactions": len(gains),
        "short_term_gains": total_st_gains,
        "long_term_gains": total_lt_gains,
        "total_gains": total_st_gains + total_lt_gains,
        "num_short_term": sum(1 for g in gains if g.is_short_term),
        "num_long_term": sum(1 for g in gains if g.is_long_term),
        "num_wash_sales": sum(1 for g in gains if g.wash_sale),
    }
