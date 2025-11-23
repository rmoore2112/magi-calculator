"""Roth conversion calculator and optimizer."""

from decimal import Decimal
from dataclasses import dataclass
from typing import Optional

from ..models.user_inputs import FilingStatus
from .tax_calculator import TaxCalculator


@dataclass
class RothConversionSuggestion:
    """Container for Roth conversion opportunity analysis."""

    has_opportunity: bool
    current_magi: Decimal
    target_magi: Decimal
    suggested_conversion: Decimal  # Amount to convert
    conversion_tax: Decimal  # Tax owed on the conversion
    current_total_tax: Decimal  # Tax without conversion
    new_total_tax: Decimal  # Tax with conversion
    marginal_rate: Decimal  # Effective rate on the conversion

    # Breakdown for display
    current_federal_tax: Decimal
    new_federal_tax: Decimal
    current_state_tax: Decimal
    new_state_tax: Decimal

    def to_dict(self) -> dict:
        """Convert to dictionary for template rendering."""
        return {
            "has_opportunity": self.has_opportunity,
            "current_magi": float(self.current_magi),
            "target_magi": float(self.target_magi),
            "suggested_conversion": float(self.suggested_conversion),
            "conversion_tax": float(self.conversion_tax),
            "current_total_tax": float(self.current_total_tax),
            "new_total_tax": float(self.new_total_tax),
            "marginal_rate": float(self.marginal_rate),
            "current_federal_tax": float(self.current_federal_tax),
            "new_federal_tax": float(self.new_federal_tax),
            "current_state_tax": float(self.current_state_tax),
            "new_state_tax": float(self.new_state_tax),
        }


class RothConverter:
    """Calculate Roth conversion opportunities and tax impact."""

    @classmethod
    def analyze_roth_opportunity(
        cls,
        current_magi: Decimal,
        target_magi: Optional[Decimal],
        short_term_gains: Decimal,
        long_term_gains: Decimal,
        dividend_income: Decimal,
        interest_income: Decimal,
        additional_income: Decimal,
        filing_status: FilingStatus,
        current_tax_result,
        deduction: Decimal = None,
    ) -> Optional[RothConversionSuggestion]:
        """
        Analyze whether there's a Roth conversion opportunity.

        Args:
            current_magi: Current calculated MAGI
            target_magi: User's target MAGI (optional)
            short_term_gains: Short-term capital gains
            long_term_gains: Long-term capital gains
            dividend_income: Dividend income
            interest_income: Interest income
            additional_income: Other ordinary income
            filing_status: Tax filing status
            current_tax_result: Current TaxResult object
            deduction: Total deduction amount (standard or itemized)

        Returns:
            RothConversionSuggestion if opportunity exists, None otherwise
        """
        # Check if we have a target and it's above current MAGI
        if not target_magi or target_magi <= current_magi:
            return None

        # Calculate the simple gap
        suggested_conversion = target_magi - current_magi

        # Roth conversion is treated as ordinary income
        # Recalculate taxes with the conversion added to ordinary income
        new_short_term_gains = short_term_gains
        new_interest = interest_income
        new_additional = additional_income + suggested_conversion  # Add conversion here

        new_tax_result = TaxCalculator.calculate_taxes(
            short_term_gains=new_short_term_gains,
            long_term_gains=long_term_gains,
            dividend_income=dividend_income,
            interest_income=new_interest,
            additional_income=new_additional,
            filing_status=filing_status,
            deduction=deduction,
            # Note: withholding/prior_year_tax not needed for Roth conversion comparison
        )

        # Calculate the tax impact of the conversion
        conversion_tax = new_tax_result.total_tax - current_tax_result.total_tax

        # Calculate marginal rate on the conversion
        if suggested_conversion > 0:
            marginal_rate = (conversion_tax / suggested_conversion) * 100
        else:
            marginal_rate = Decimal(0)

        return RothConversionSuggestion(
            has_opportunity=True,
            current_magi=current_magi,
            target_magi=target_magi,
            suggested_conversion=suggested_conversion,
            conversion_tax=conversion_tax,
            current_total_tax=current_tax_result.total_tax,
            new_total_tax=new_tax_result.total_tax,
            marginal_rate=marginal_rate,
            current_federal_tax=current_tax_result.total_federal_tax,
            new_federal_tax=new_tax_result.total_federal_tax,
            current_state_tax=current_tax_result.state_tax,
            new_state_tax=new_tax_result.state_tax,
        )

    @classmethod
    def get_no_opportunity_result(cls) -> Optional[RothConversionSuggestion]:
        """Return None when there's no opportunity."""
        return None
