"""MAGI (Modified Adjusted Gross Income) calculator."""

from decimal import Decimal
from pathlib import Path

from ..models.user_inputs import UserInputs
from .income_aggregator import IncomeAggregator
from .tax_rules import TaxRules
from .tax_calculator import TaxCalculator, TaxResult
from .roth_converter import RothConverter, RothConversionSuggestion


class MAGIResult:
    """Container for MAGI calculation results."""

    def __init__(
        self,
        total_income: Decimal,
        agi: Decimal,
        magi: Decimal,
        income_breakdown: dict,
        deductions_breakdown: dict,
        filing_status: str,
        tax_year: int,
        tax_result: TaxResult = None,
        roth_suggestion: RothConversionSuggestion = None,
    ):
        self.total_income = total_income
        self.agi = agi
        self.magi = magi
        self.income_breakdown = income_breakdown
        self.deductions_breakdown = deductions_breakdown
        self.filing_status = filing_status
        self.tax_year = tax_year
        self.tax_result = tax_result
        self.roth_suggestion = roth_suggestion

    def to_dict(self) -> dict:
        """Convert result to dictionary."""
        result = {
            "total_income": float(self.total_income),
            "agi": float(self.agi),
            "magi": float(self.magi),
            "income_breakdown": {
                k: {k2: float(v2) for k2, v2 in v.items()}
                for k, v in self.income_breakdown.items()
            },
            "deductions_breakdown": {
                k: float(v) for k, v in self.deductions_breakdown.items()
            },
            "filing_status": self.filing_status,
            "tax_year": self.tax_year,
        }
        if self.tax_result:
            result["tax_result"] = self.tax_result.to_dict()
        if self.roth_suggestion:
            result["roth_suggestion"] = self.roth_suggestion.to_dict()
        return result


class MAGICalculator:
    """Calculate Modified Adjusted Gross Income (MAGI)."""

    def __init__(self, gains_file: Path, transactions_file: Path):
        """
        Initialize MAGI calculator.

        Args:
            gains_file: Path to realized gains CSV
            transactions_file: Path to transactions CSV
        """
        self.aggregator = IncomeAggregator(gains_file, transactions_file)

    def calculate(self, user_inputs: UserInputs) -> MAGIResult:
        """
        Calculate MAGI based on investment data and user inputs.

        MAGI Calculation:
        1. Start with Total Income (all sources)
        2. Subtract adjustments to income (student loan interest, IRA contributions, etc.)
        3. This gives you AGI (Adjusted Gross Income)
        4. Add back certain deductions (tax-exempt interest, IRA deductions, etc.)
        5. This gives you MAGI (Modified Adjusted Gross Income)

        Args:
            user_inputs: User-provided inputs

        Returns:
            MAGIResult object with all calculations
        """
        # Load investment income
        investment_income = self.aggregator.load_investment_income()
        additional_income = self.aggregator.get_additional_income(user_inputs)
        deductions = self.aggregator.get_deductions(user_inputs)

        # Calculate total income
        total_income = investment_income.total_investment_income + additional_income.total

        # Calculate AGI (Total Income - Adjustments)
        adjustments = deductions.total_adjustments
        agi = total_income - adjustments

        # Calculate MAGI (AGI + certain add-backs)
        # For MAGI, we add back:
        # - Tax-exempt interest
        # - Student loan interest deduction
        # - IRA deductions
        # - Other deductions that were subtracted for AGI
        magi_addbacks = (
            additional_income.tax_exempt_interest
            + deductions.student_loan_interest
            + deductions.ira_contributions
        )

        magi = agi + magi_addbacks

        # Get detailed breakdown
        income_breakdown = self.aggregator.get_income_breakdown(user_inputs)

        deductions_breakdown = {
            "student_loan_interest": deductions.student_loan_interest,
            "ira_contributions": deductions.ira_contributions,
            "hsa_contributions": deductions.hsa_contributions,
            "self_employment_tax": deductions.self_employment_tax,
            "other_adjustments": deductions.other_adjustments,
            "total_adjustments": deductions.total_adjustments,
            "standard_deduction": deductions.standard_deduction,
            "itemized_deductions": deductions.itemized_deductions,
        }

        # Calculate taxes
        tax_result = TaxCalculator.calculate_taxes(
            short_term_gains=investment_income.short_term_capital_gains,
            long_term_gains=investment_income.long_term_capital_gains,
            dividend_income=investment_income.dividend_income,
            interest_income=investment_income.interest_income,
            additional_income=additional_income.total,
            filing_status=user_inputs.filing_status,
        )

        # Analyze Roth conversion opportunity
        roth_suggestion = None
        if user_inputs.target_magi:
            roth_suggestion = RothConverter.analyze_roth_opportunity(
                current_magi=magi,
                target_magi=user_inputs.target_magi,
                short_term_gains=investment_income.short_term_capital_gains,
                long_term_gains=investment_income.long_term_capital_gains,
                dividend_income=investment_income.dividend_income,
                interest_income=investment_income.interest_income,
                additional_income=additional_income.total,
                filing_status=user_inputs.filing_status,
                current_tax_result=tax_result,
            )

        return MAGIResult(
            total_income=total_income,
            agi=agi,
            magi=magi,
            income_breakdown=income_breakdown,
            deductions_breakdown=deductions_breakdown,
            filing_status=user_inputs.filing_status.value,
            tax_year=user_inputs.tax_year,
            tax_result=tax_result,
            roth_suggestion=roth_suggestion,
        )

    def get_irmaa_info(self, magi: Decimal, filing_status) -> dict:
        """
        Get IRMAA tier information for the calculated MAGI.

        Args:
            magi: Calculated MAGI
            filing_status: Filing status enum

        Returns:
            Dictionary with IRMAA information
        """
        tier = TaxRules.get_irmaa_tier(magi, filing_status)
        return {
            "tier": tier,
            "magi": float(magi),
        }

    def get_detailed_transactions(self):
        """Get detailed transaction data for reporting."""
        investment_income = self.aggregator.load_investment_income()

        # Helper function to convert gain to dict
        def gain_to_dict(g):
            return {
                "symbol": g.symbol,
                "name": g.name,
                "closed_date": g.closed_date.isoformat() if g.closed_date else None,
                "opened_date": g.opened_date.isoformat() if g.opened_date else None,
                "quantity": int(g.quantity),
                "proceeds": float(g.proceeds),
                "cost_basis": float(g.cost_basis),
                "gain_loss": float(g.gain_loss),
                "term": g.term,
                "wash_sale": g.wash_sale,
                "holding_period_days": g.holding_period_days,
            }

        # Filter short-term option trades
        short_term_option_trades = [
            gain_to_dict(g)
            for g in investment_income.realized_gains
            if g.is_short_term and g.is_option
        ]

        return {
            "realized_gains": [
                gain_to_dict(g) for g in investment_income.realized_gains
            ],
            "short_term_option_trades": short_term_option_trades,
            "income_transactions": [
                {
                    "date": t.date.isoformat() if t.date else None,
                    "action": t.action,
                    "symbol": t.symbol,
                    "description": t.description,
                    "amount": float(t.amount),
                }
                for t in investment_income.transactions
            ],
        }
