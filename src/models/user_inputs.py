"""User input models."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class FilingStatus(Enum):
    """Tax filing status options."""

    SINGLE = "Single"
    MARRIED_FILING_JOINTLY = "Married Filing Jointly"
    MARRIED_FILING_SEPARATELY = "Married Filing Separately"
    HEAD_OF_HOUSEHOLD = "Head of Household"
    QUALIFYING_WIDOW = "Qualifying Widow(er)"


@dataclass
class TaxYear:
    """Tax year information and standard deduction amounts."""

    year: int
    standard_deductions: dict[FilingStatus, Decimal]

    @staticmethod
    def for_2025() -> "TaxYear":
        """Get 2025 tax year information."""
        return TaxYear(
            year=2025,
            standard_deductions={
                FilingStatus.SINGLE: Decimal("15000"),
                FilingStatus.MARRIED_FILING_JOINTLY: Decimal("30000"),
                FilingStatus.MARRIED_FILING_SEPARATELY: Decimal("15000"),
                FilingStatus.HEAD_OF_HOUSEHOLD: Decimal("22500"),
                FilingStatus.QUALIFYING_WIDOW: Decimal("30000"),
            },
        )


@dataclass
class UserInputs:
    """User-provided inputs for MAGI calculation."""

    filing_status: FilingStatus
    tax_year: int
    target_magi: Decimal = None  # Optional target MAGI for tax optimization

    # Additional income
    wages: Decimal = Decimal(0)
    business_income: Decimal = Decimal(0)
    rental_income: Decimal = Decimal(0)
    retirement_income: Decimal = Decimal(0)
    social_security: Decimal = Decimal(0)
    other_income: Decimal = Decimal(0)
    tax_exempt_interest: Decimal = Decimal(0)

    # Deductions and adjustments
    use_standard_deduction: bool = True
    itemized_deductions: Decimal = Decimal(0)
    student_loan_interest: Decimal = Decimal(0)
    ira_contributions: Decimal = Decimal(0)
    hsa_contributions: Decimal = Decimal(0)
    self_employment_tax: Decimal = Decimal(0)
    other_adjustments: Decimal = Decimal(0)

    # Tax withholding and payments
    federal_withholding: Decimal = Decimal(0)  # Federal tax withheld (W-2, estimated payments)
    prior_year_tax: Decimal = None  # Optional: Prior year's total tax for safe harbor calculation

    def get_standard_deduction(self) -> Decimal:
        """Get standard deduction amount for filing status."""
        tax_year = TaxYear.for_2025()
        return tax_year.standard_deductions.get(self.filing_status, Decimal(0))
