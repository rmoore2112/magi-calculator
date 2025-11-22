"""Transaction data models."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class RealizedGain:
    """Represents a realized capital gain or loss from a closed position."""

    symbol: str
    name: str
    closed_date: date
    opened_date: date
    quantity: int
    proceeds_per_share: Decimal
    cost_per_share: Decimal
    proceeds: Decimal
    cost_basis: Decimal
    gain_loss: Decimal
    gain_loss_pct: Optional[Decimal]
    long_term_gain_loss: Optional[Decimal]
    short_term_gain_loss: Optional[Decimal]
    term: str  # "Long Term" or "Short Term"
    wash_sale: bool
    disallowed_loss: Optional[Decimal]

    @property
    def is_long_term(self) -> bool:
        """Check if this is a long-term gain/loss."""
        return self.term == "Long Term"

    @property
    def is_short_term(self) -> bool:
        """Check if this is a short-term gain/loss."""
        return self.term == "Short Term"

    @property
    def holding_period_days(self) -> int:
        """Calculate holding period in days."""
        return (self.closed_date - self.opened_date).days


@dataclass
class Transaction:
    """Represents a transaction from the transaction history."""

    date: date
    action: str
    symbol: Optional[str]
    description: str
    quantity: Optional[Decimal]
    price: Optional[Decimal]
    fees_comm: Decimal
    amount: Decimal

    @property
    def is_dividend(self) -> bool:
        """Check if this is a dividend transaction."""
        return self.action == "Cash Dividend"

    @property
    def is_interest(self) -> bool:
        """Check if this is an interest transaction."""
        return self.action in ("Bond Interest", "Credit Interest")

    @property
    def is_trade(self) -> bool:
        """Check if this is a trade transaction."""
        return self.action in (
            "Buy",
            "Sell",
            "Buy to Open",
            "Sell to Open",
            "Buy to Close",
            "Sell to Close",
        )
