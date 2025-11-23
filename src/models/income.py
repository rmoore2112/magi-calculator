"""Income aggregation models."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List

from .transaction import RealizedGain, Transaction


@dataclass
class InvestmentIncome:
    """Aggregated investment income from CSV files."""

    realized_gains: List[RealizedGain] = field(default_factory=list)
    transactions: List[Transaction] = field(default_factory=list)

    @property
    def short_term_capital_gains(self) -> Decimal:
        """Calculate total short-term capital gains."""
        return sum(
            (g.short_term_gain_loss or Decimal(0))
            for g in self.realized_gains
            if g.is_short_term
        )

    @property
    def short_term_options_gains(self) -> Decimal:
        """Calculate short-term capital gains from options only."""
        return sum(
            (g.short_term_gain_loss or Decimal(0))
            for g in self.realized_gains
            if g.is_short_term and g.is_option
        )

    @property
    def short_term_non_options_gains(self) -> Decimal:
        """Calculate short-term capital gains from non-option trades."""
        return sum(
            (g.short_term_gain_loss or Decimal(0))
            for g in self.realized_gains
            if g.is_short_term and not g.is_option
        )

    @property
    def long_term_capital_gains(self) -> Decimal:
        """Calculate total long-term capital gains."""
        return sum(
            (g.long_term_gain_loss or Decimal(0))
            for g in self.realized_gains
            if g.is_long_term
        )

    @property
    def total_capital_gains(self) -> Decimal:
        """Calculate total capital gains (ST + LT)."""
        return self.short_term_capital_gains + self.long_term_capital_gains

    @property
    def dividend_income(self) -> Decimal:
        """Calculate total dividend income."""
        return sum(t.amount for t in self.transactions if t.is_dividend)

    @property
    def interest_income(self) -> Decimal:
        """Calculate total interest income."""
        return sum(t.amount for t in self.transactions if t.is_interest)

    @property
    def total_investment_income(self) -> Decimal:
        """Calculate total investment income."""
        return self.total_capital_gains + self.dividend_income + self.interest_income


@dataclass
class AdditionalIncome:
    """Additional income sources beyond investment income."""

    wages: Decimal = Decimal(0)
    business_income: Decimal = Decimal(0)
    rental_income: Decimal = Decimal(0)
    retirement_income: Decimal = Decimal(0)
    social_security: Decimal = Decimal(0)
    other_income: Decimal = Decimal(0)
    tax_exempt_interest: Decimal = Decimal(0)

    @property
    def total(self) -> Decimal:
        """Calculate total additional income."""
        return (
            self.wages
            + self.business_income
            + self.rental_income
            + self.retirement_income
            + self.social_security
            + self.other_income
        )


@dataclass
class Deductions:
    """Deductions and adjustments to income."""

    standard_deduction: Decimal = Decimal(0)
    itemized_deductions: Decimal = Decimal(0)
    student_loan_interest: Decimal = Decimal(0)
    ira_contributions: Decimal = Decimal(0)
    hsa_contributions: Decimal = Decimal(0)
    self_employment_tax: Decimal = Decimal(0)
    other_adjustments: Decimal = Decimal(0)

    @property
    def total_deductions(self) -> Decimal:
        """Calculate total deductions (standard or itemized, whichever is higher)."""
        return max(self.standard_deduction, self.itemized_deductions)

    @property
    def total_adjustments(self) -> Decimal:
        """Calculate total adjustments to income."""
        return (
            self.student_loan_interest
            + self.ira_contributions
            + self.hsa_contributions
            + self.self_employment_tax
            + self.other_adjustments
        )
