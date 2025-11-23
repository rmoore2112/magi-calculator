"""Federal and state tax calculator."""

from decimal import Decimal
from dataclasses import dataclass
from typing import Tuple, Optional

from ..models.user_inputs import FilingStatus


@dataclass
class QuarterlyPaymentInfo:
    """Information about quarterly estimated tax payment requirements."""

    required: bool
    estimated_payment: Decimal  # Suggested quarterly payment amount
    total_underpayment: Decimal  # Amount that will be owed at tax time
    reason: str  # Explanation of why payments are required
    safe_harbor_amount: Decimal  # Minimum to pay to avoid penalty

    def to_dict(self) -> dict:
        """Convert to dictionary for template rendering."""
        return {
            "required": self.required,
            "estimated_payment": float(self.estimated_payment),
            "total_underpayment": float(self.total_underpayment),
            "reason": self.reason,
            "safe_harbor_amount": float(self.safe_harbor_amount),
        }


@dataclass
class TaxResult:
    """Container for tax calculation results."""

    # Income breakdown
    ordinary_income: Decimal  # Short-term gains + interest
    preferential_income: Decimal  # Long-term gains + qualified dividends
    total_income: Decimal
    standard_deduction: Decimal
    taxable_income: Decimal

    # Federal tax
    federal_ordinary_tax: Decimal
    federal_preferential_tax: Decimal
    total_federal_tax: Decimal

    # State tax
    state_taxable_income: Decimal
    state_tax: Decimal

    # Total
    total_tax: Decimal
    after_tax_income: Decimal

    # Rates
    effective_tax_rate: Decimal  # Total tax / total income
    federal_marginal_rate: Decimal  # Highest bracket reached

    # Quarterly payments
    quarterly_payment_info: Optional[QuarterlyPaymentInfo] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for template rendering."""
        result = {
            "ordinary_income": float(self.ordinary_income),
            "preferential_income": float(self.preferential_income),
            "total_income": float(self.total_income),
            "standard_deduction": float(self.standard_deduction),
            "taxable_income": float(self.taxable_income),
            "federal_ordinary_tax": float(self.federal_ordinary_tax),
            "federal_preferential_tax": float(self.federal_preferential_tax),
            "total_federal_tax": float(self.total_federal_tax),
            "state_taxable_income": float(self.state_taxable_income),
            "state_tax": float(self.state_tax),
            "total_tax": float(self.total_tax),
            "after_tax_income": float(self.after_tax_income),
            "effective_tax_rate": float(self.effective_tax_rate),
            "federal_marginal_rate": float(self.federal_marginal_rate),
        }
        if self.quarterly_payment_info:
            result["quarterly_payment_info"] = self.quarterly_payment_info.to_dict()
        return result


class TaxCalculator:
    """Calculate federal and North Carolina state taxes."""

    # 2025 Federal Tax Brackets (ordinary income)
    FEDERAL_BRACKETS = {
        FilingStatus.SINGLE: [
            (Decimal("11925"), Decimal("0.10")),
            (Decimal("48475"), Decimal("0.12")),
            (Decimal("103350"), Decimal("0.22")),
            (Decimal("197300"), Decimal("0.24")),
            (Decimal("250525"), Decimal("0.32")),
            (Decimal("626350"), Decimal("0.35")),
            (Decimal("999999999"), Decimal("0.37")),
        ],
        FilingStatus.MARRIED_FILING_JOINTLY: [
            (Decimal("23850"), Decimal("0.10")),
            (Decimal("96950"), Decimal("0.12")),
            (Decimal("206700"), Decimal("0.22")),
            (Decimal("394600"), Decimal("0.24")),
            (Decimal("501050"), Decimal("0.32")),
            (Decimal("751600"), Decimal("0.35")),
            (Decimal("999999999"), Decimal("0.37")),
        ],
        FilingStatus.MARRIED_FILING_SEPARATELY: [
            (Decimal("11925"), Decimal("0.10")),
            (Decimal("48475"), Decimal("0.12")),
            (Decimal("103350"), Decimal("0.22")),
            (Decimal("197300"), Decimal("0.24")),
            (Decimal("250525"), Decimal("0.32")),
            (Decimal("375800"), Decimal("0.35")),
            (Decimal("999999999"), Decimal("0.37")),
        ],
        FilingStatus.HEAD_OF_HOUSEHOLD: [
            (Decimal("17000"), Decimal("0.10")),
            (Decimal("64850"), Decimal("0.12")),
            (Decimal("103350"), Decimal("0.22")),
            (Decimal("197300"), Decimal("0.24")),
            (Decimal("250500"), Decimal("0.32")),
            (Decimal("626350"), Decimal("0.35")),
            (Decimal("999999999"), Decimal("0.37")),
        ],
        FilingStatus.QUALIFYING_WIDOW: [
            (Decimal("23850"), Decimal("0.10")),
            (Decimal("96950"), Decimal("0.12")),
            (Decimal("206700"), Decimal("0.22")),
            (Decimal("394600"), Decimal("0.24")),
            (Decimal("501050"), Decimal("0.32")),
            (Decimal("751600"), Decimal("0.35")),
            (Decimal("999999999"), Decimal("0.37")),
        ],
    }

    # 2025 Long-Term Capital Gains & Qualified Dividend Thresholds
    LTCG_BRACKETS = {
        FilingStatus.SINGLE: [
            (Decimal("48350"), Decimal("0.00")),
            (Decimal("533400"), Decimal("0.15")),
            (Decimal("999999999"), Decimal("0.20")),
        ],
        FilingStatus.MARRIED_FILING_JOINTLY: [
            (Decimal("96700"), Decimal("0.00")),
            (Decimal("600050"), Decimal("0.15")),
            (Decimal("999999999"), Decimal("0.20")),
        ],
        FilingStatus.MARRIED_FILING_SEPARATELY: [
            (Decimal("48350"), Decimal("0.00")),
            (Decimal("300025"), Decimal("0.15")),
            (Decimal("999999999"), Decimal("0.20")),
        ],
        FilingStatus.HEAD_OF_HOUSEHOLD: [
            (Decimal("64750"), Decimal("0.00")),
            (Decimal("566700"), Decimal("0.15")),
            (Decimal("999999999"), Decimal("0.20")),
        ],
        FilingStatus.QUALIFYING_WIDOW: [
            (Decimal("96700"), Decimal("0.00")),
            (Decimal("600050"), Decimal("0.15")),
            (Decimal("999999999"), Decimal("0.20")),
        ],
    }

    # 2025 Standard Deductions
    STANDARD_DEDUCTIONS = {
        FilingStatus.SINGLE: Decimal("15000"),
        FilingStatus.MARRIED_FILING_JOINTLY: Decimal("30000"),
        FilingStatus.MARRIED_FILING_SEPARATELY: Decimal("15000"),
        FilingStatus.HEAD_OF_HOUSEHOLD: Decimal("22500"),
        FilingStatus.QUALIFYING_WIDOW: Decimal("30000"),
    }

    # North Carolina Tax (2025)
    NC_TAX_RATE = Decimal("0.0475")  # 4.75% flat rate
    NC_STANDARD_DEDUCTIONS = {
        FilingStatus.SINGLE: Decimal("12750"),
        FilingStatus.MARRIED_FILING_JOINTLY: Decimal("25500"),
        FilingStatus.MARRIED_FILING_SEPARATELY: Decimal("12750"),
        FilingStatus.HEAD_OF_HOUSEHOLD: Decimal("19125"),
        FilingStatus.QUALIFYING_WIDOW: Decimal("25500"),
    }

    @classmethod
    def calculate_federal_ordinary_tax(
        cls, taxable_ordinary_income: Decimal, filing_status: FilingStatus
    ) -> Tuple[Decimal, Decimal]:
        """
        Calculate federal tax on ordinary income using progressive brackets.

        Returns:
            Tuple of (tax_amount, marginal_rate)
        """
        if taxable_ordinary_income <= 0:
            return Decimal("0"), Decimal("0")

        brackets = cls.FEDERAL_BRACKETS.get(filing_status, cls.FEDERAL_BRACKETS[FilingStatus.SINGLE])
        tax = Decimal("0")
        previous_threshold = Decimal("0")
        marginal_rate = Decimal("0")

        for threshold, rate in brackets:
            if taxable_ordinary_income <= previous_threshold:
                break

            taxable_in_bracket = min(taxable_ordinary_income, threshold) - previous_threshold
            tax += taxable_in_bracket * rate
            marginal_rate = rate

            if taxable_ordinary_income <= threshold:
                break

            previous_threshold = threshold

        return tax, marginal_rate

    @classmethod
    def calculate_federal_ltcg_tax(
        cls,
        preferential_income: Decimal,
        ordinary_income: Decimal,
        filing_status: FilingStatus,
    ) -> Decimal:
        """
        Calculate federal tax on long-term capital gains and qualified dividends.

        Uses "stacking" method: ordinary income fills lower brackets first,
        then preferential income is stacked on top.
        """
        if preferential_income <= 0:
            return Decimal("0")

        brackets = cls.LTCG_BRACKETS.get(filing_status, cls.LTCG_BRACKETS[FilingStatus.SINGLE])
        tax = Decimal("0")

        # Start stacking from where ordinary income left off
        income_position = ordinary_income
        remaining_ltcg = preferential_income
        previous_threshold = Decimal("0")

        for threshold, rate in brackets:
            if remaining_ltcg <= 0:
                break

            # How much of this bracket is already filled by ordinary income?
            bracket_start = max(income_position, previous_threshold)
            bracket_end = threshold

            if bracket_start >= bracket_end:
                previous_threshold = threshold
                continue

            # Amount of preferential income in this bracket
            amount_in_bracket = min(remaining_ltcg, bracket_end - bracket_start)
            tax += amount_in_bracket * rate
            remaining_ltcg -= amount_in_bracket
            income_position += amount_in_bracket
            previous_threshold = threshold

        return tax

    @classmethod
    def calculate_nc_state_tax(
        cls, total_income: Decimal, filing_status: FilingStatus
    ) -> Tuple[Decimal, Decimal]:
        """
        Calculate North Carolina state tax (flat 4.75% rate).

        Returns:
            Tuple of (taxable_income, tax_amount)
        """
        nc_standard_deduction = cls.NC_STANDARD_DEDUCTIONS.get(
            filing_status, cls.NC_STANDARD_DEDUCTIONS[FilingStatus.SINGLE]
        )

        taxable_income = max(Decimal("0"), total_income - nc_standard_deduction)
        tax = taxable_income * cls.NC_TAX_RATE

        return taxable_income, tax

    @classmethod
    def calculate_quarterly_payment_requirement(
        cls,
        total_federal_tax: Decimal,
        federal_withholding: Decimal,
        prior_year_tax: Optional[Decimal],
        filing_status: FilingStatus,
    ) -> QuarterlyPaymentInfo:
        """
        Determine if quarterly estimated tax payments are required.

        IRS rules require quarterly payments if:
        1. You'll owe at least $1,000 in tax when you file, AND
        2. Your withholding will be less than the smaller of:
           - 90% of current year tax
           - 100% of prior year tax (110% if prior year AGI > $150K/$75K)

        Args:
            total_federal_tax: Current year's total federal tax liability
            federal_withholding: Federal tax already withheld/paid
            prior_year_tax: Prior year's total tax (optional, for safe harbor)
            filing_status: Tax filing status

        Returns:
            QuarterlyPaymentInfo with payment requirements
        """
        # Calculate expected underpayment
        underpayment = total_federal_tax - federal_withholding

        # Check if underpayment exceeds $1,000 threshold
        if underpayment < Decimal("1000"):
            return QuarterlyPaymentInfo(
                required=False,
                estimated_payment=Decimal("0"),
                total_underpayment=underpayment,
                reason="Estimated underpayment is less than $1,000",
                safe_harbor_amount=Decimal("0"),
            )

        # Calculate safe harbor amount (minimum to pay to avoid penalty)
        # Generally 90% of current year tax or 100% of prior year tax
        current_year_safe_harbor = total_federal_tax * Decimal("0.90")

        # Use 100% of prior year tax if provided (110% if high income, but we'll use 100% for simplicity)
        if prior_year_tax:
            prior_year_safe_harbor = prior_year_tax
            safe_harbor_amount = min(current_year_safe_harbor, prior_year_safe_harbor)
            if federal_withholding >= prior_year_safe_harbor:
                reason = f"Withholding meets prior year safe harbor ({float(prior_year_safe_harbor):,.0f})"
            else:
                reason = f"Underpayment exceeds $1,000 and withholding is less than safe harbor amount"
        else:
            safe_harbor_amount = current_year_safe_harbor
            if federal_withholding >= current_year_safe_harbor:
                reason = f"Withholding meets 90% of current year tax ({float(current_year_safe_harbor):,.0f})"
            else:
                reason = f"Underpayment exceeds $1,000 and withholding is less than 90% of current year tax"

        # Determine if quarterly payments are required
        payments_required = federal_withholding < safe_harbor_amount

        # Calculate suggested quarterly payment
        # Remaining amount needed divided by remaining quarters (assume we're planning ahead for 4 quarters)
        remaining_needed = max(Decimal("0"), safe_harbor_amount - federal_withholding)
        suggested_quarterly = remaining_needed / Decimal("4")

        return QuarterlyPaymentInfo(
            required=payments_required,
            estimated_payment=suggested_quarterly,
            total_underpayment=underpayment,
            reason=reason,
            safe_harbor_amount=safe_harbor_amount,
        )

    @classmethod
    def calculate_taxes(
        cls,
        short_term_gains: Decimal,
        long_term_gains: Decimal,
        dividend_income: Decimal,
        interest_income: Decimal,
        additional_income: Decimal,
        filing_status: FilingStatus,
        deduction: Decimal = None,
        federal_withholding: Decimal = Decimal("0"),
        prior_year_tax: Optional[Decimal] = None,
    ) -> TaxResult:
        """
        Calculate complete federal and state tax liability.

        Args:
            short_term_gains: Short-term capital gains
            long_term_gains: Long-term capital gains
            dividend_income: Dividend income (treated as qualified)
            interest_income: Interest income
            additional_income: Other income (wages, business, etc.)
            filing_status: Tax filing status
            deduction: Total deduction amount (standard or itemized). If None, uses standard deduction.
            federal_withholding: Federal tax withheld or already paid
            prior_year_tax: Prior year's total tax (for safe harbor calculation)

        Returns:
            TaxResult with complete tax breakdown
        """
        # Categorize income
        ordinary_income = short_term_gains + interest_income + additional_income
        preferential_income = long_term_gains + dividend_income
        total_income = ordinary_income + preferential_income

        # Get deduction amount (use provided deduction or default to standard)
        if deduction is None:
            deduction_amount = cls.STANDARD_DEDUCTIONS.get(
                filing_status, cls.STANDARD_DEDUCTIONS[FilingStatus.SINGLE]
            )
        else:
            deduction_amount = deduction

        # Calculate taxable income
        total_taxable = max(Decimal("0"), total_income - deduction_amount)

        # Determine how much is ordinary vs preferential after deduction
        if total_taxable == 0:
            taxable_ordinary = Decimal("0")
            taxable_preferential = Decimal("0")
        else:
            # Deduction reduces ordinary income first, then preferential
            taxable_ordinary = max(Decimal("0"), ordinary_income - deduction_amount)
            if ordinary_income > deduction_amount:
                taxable_preferential = preferential_income
            else:
                # Deduction partially or fully absorbed ordinary income
                remaining_deduction = deduction_amount - ordinary_income
                taxable_preferential = max(Decimal("0"), preferential_income - remaining_deduction)

        # Calculate federal taxes
        federal_ordinary_tax, marginal_rate = cls.calculate_federal_ordinary_tax(
            taxable_ordinary, filing_status
        )
        federal_preferential_tax = cls.calculate_federal_ltcg_tax(
            taxable_preferential, taxable_ordinary, filing_status
        )
        total_federal_tax = federal_ordinary_tax + federal_preferential_tax

        # Calculate North Carolina state tax
        nc_taxable_income, state_tax = cls.calculate_nc_state_tax(total_income, filing_status)

        # Calculate totals
        total_tax = total_federal_tax + state_tax
        after_tax_income = total_income - total_tax
        effective_rate = (
            (total_tax / total_income * 100) if total_income > 0 else Decimal("0")
        )

        # Calculate quarterly payment requirement
        quarterly_payment_info = cls.calculate_quarterly_payment_requirement(
            total_federal_tax=total_federal_tax,
            federal_withholding=federal_withholding,
            prior_year_tax=prior_year_tax,
            filing_status=filing_status,
        )

        return TaxResult(
            ordinary_income=ordinary_income,
            preferential_income=preferential_income,
            total_income=total_income,
            standard_deduction=deduction_amount,
            taxable_income=total_taxable,
            federal_ordinary_tax=federal_ordinary_tax,
            federal_preferential_tax=federal_preferential_tax,
            total_federal_tax=total_federal_tax,
            state_taxable_income=nc_taxable_income,
            state_tax=state_tax,
            total_tax=total_tax,
            after_tax_income=after_tax_income,
            effective_tax_rate=effective_rate,
            federal_marginal_rate=marginal_rate * 100,  # Convert to percentage
            quarterly_payment_info=quarterly_payment_info,
        )
