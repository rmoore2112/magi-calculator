"""Tax rules and thresholds for different filing statuses."""

from decimal import Decimal
from ..models.user_inputs import FilingStatus


class TaxRules:
    """Tax rules and calculations for 2025 tax year."""

    # 2025 Standard Deductions
    STANDARD_DEDUCTIONS = {
        FilingStatus.SINGLE: Decimal("15000"),
        FilingStatus.MARRIED_FILING_JOINTLY: Decimal("30000"),
        FilingStatus.MARRIED_FILING_SEPARATELY: Decimal("15000"),
        FilingStatus.HEAD_OF_HOUSEHOLD: Decimal("22500"),
        FilingStatus.QUALIFYING_WIDOW: Decimal("30000"),
    }

    # IRMAA (Medicare Part B/D premium surcharge) thresholds for MAGI
    # These are approximate 2025 values
    IRMAA_THRESHOLDS = {
        FilingStatus.SINGLE: [
            (Decimal("106000"), "Standard premium"),
            (Decimal("133000"), "Tier 1"),
            (Decimal("167000"), "Tier 2"),
            (Decimal("200000"), "Tier 3"),
            (Decimal("500000"), "Tier 4"),
            (Decimal("999999999"), "Tier 5"),
        ],
        FilingStatus.MARRIED_FILING_JOINTLY: [
            (Decimal("212000"), "Standard premium"),
            (Decimal("266000"), "Tier 1"),
            (Decimal("334000"), "Tier 2"),
            (Decimal("400000"), "Tier 3"),
            (Decimal("750000"), "Tier 4"),
            (Decimal("999999999"), "Tier 5"),
        ],
        FilingStatus.MARRIED_FILING_SEPARATELY: [
            (Decimal("106000"), "Standard premium"),
            (Decimal("133000"), "Tier 1"),
            (Decimal("167000"), "Tier 2"),
            (Decimal("200000"), "Tier 3"),
            (Decimal("500000"), "Tier 4"),
            (Decimal("999999999"), "Tier 5"),
        ],
    }

    # ACA Premium Tax Credit phaseout thresholds (based on Federal Poverty Level)
    # These are simplified thresholds
    ACA_SUBSIDY_THRESHOLDS = {
        "single_household": Decimal("60000"),  # Approximate 400% FPL for 1 person
        "family_of_4": Decimal("120000"),  # Approximate 400% FPL for family of 4
    }

    @classmethod
    def get_standard_deduction(cls, filing_status: FilingStatus) -> Decimal:
        """Get standard deduction for filing status."""
        return cls.STANDARD_DEDUCTIONS.get(filing_status, Decimal(0))

    @classmethod
    def get_irmaa_tier(cls, magi: Decimal, filing_status: FilingStatus) -> str:
        """
        Determine IRMAA tier based on MAGI.

        Args:
            magi: Modified Adjusted Gross Income
            filing_status: Tax filing status

        Returns:
            IRMAA tier description
        """
        # Default to single thresholds for statuses not explicitly listed
        if filing_status not in cls.IRMAA_THRESHOLDS:
            thresholds = cls.IRMAA_THRESHOLDS[FilingStatus.SINGLE]
        else:
            thresholds = cls.IRMAA_THRESHOLDS[filing_status]

        for threshold, tier in thresholds:
            if magi <= threshold:
                return tier

        return "Tier 5"

    @classmethod
    def is_aca_subsidy_eligible(cls, magi: Decimal, household_size: int = 1) -> bool:
        """
        Check if eligible for ACA premium tax credit.

        Args:
            magi: Modified Adjusted Gross Income
            household_size: Number of people in household

        Returns:
            True if likely eligible for subsidies
        """
        # Very simplified check
        if household_size == 1:
            return magi < cls.ACA_SUBSIDY_THRESHOLDS["single_household"]
        else:
            # Rough estimate for larger households
            threshold = cls.ACA_SUBSIDY_THRESHOLDS["family_of_4"] * Decimal(household_size) / 4
            return magi < threshold
