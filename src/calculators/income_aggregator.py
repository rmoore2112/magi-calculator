"""Income aggregation from multiple sources."""

from decimal import Decimal
from pathlib import Path
from typing import List

from ..models.income import InvestmentIncome, AdditionalIncome, Deductions
from ..models.transaction import RealizedGain, Transaction
from ..models.user_inputs import UserInputs
from ..parsers.gains_parser import parse_gains_csv
from ..parsers.transactions_parser import parse_transactions_csv, filter_income_transactions


class IncomeAggregator:
    """Aggregates income from CSV files and user inputs."""

    def __init__(self, gains_file: Path, transactions_file: Path):
        """
        Initialize the income aggregator.

        Args:
            gains_file: Path to realized gains CSV
            transactions_file: Path to transactions CSV
        """
        self.gains_file = gains_file
        self.transactions_file = transactions_file
        self._investment_income = None

    def load_investment_income(self) -> InvestmentIncome:
        """
        Load and parse investment income from CSV files.

        Returns:
            InvestmentIncome object with all investment data
        """
        if self._investment_income is None:
            gains = parse_gains_csv(self.gains_file)
            all_transactions = parse_transactions_csv(self.transactions_file)
            income_transactions = filter_income_transactions(all_transactions)

            self._investment_income = InvestmentIncome(
                realized_gains=gains,
                transactions=income_transactions,
            )

        return self._investment_income

    def get_additional_income(self, user_inputs: UserInputs) -> AdditionalIncome:
        """
        Create AdditionalIncome object from user inputs.

        Args:
            user_inputs: User-provided income information

        Returns:
            AdditionalIncome object
        """
        return AdditionalIncome(
            wages=user_inputs.wages,
            business_income=user_inputs.business_income,
            rental_income=user_inputs.rental_income,
            retirement_income=user_inputs.retirement_income,
            social_security=user_inputs.social_security,
            other_income=user_inputs.other_income,
            tax_exempt_interest=user_inputs.tax_exempt_interest,
        )

    def get_deductions(self, user_inputs: UserInputs) -> Deductions:
        """
        Create Deductions object from user inputs.

        Args:
            user_inputs: User-provided deduction information

        Returns:
            Deductions object
        """
        standard_deduction = Decimal(0)
        itemized_deductions = Decimal(0)

        if user_inputs.use_standard_deduction:
            standard_deduction = user_inputs.get_standard_deduction()
        else:
            itemized_deductions = user_inputs.itemized_deductions

        return Deductions(
            standard_deduction=standard_deduction,
            itemized_deductions=itemized_deductions,
            student_loan_interest=user_inputs.student_loan_interest,
            ira_contributions=user_inputs.ira_contributions,
            hsa_contributions=user_inputs.hsa_contributions,
            self_employment_tax=user_inputs.self_employment_tax,
            other_adjustments=user_inputs.other_adjustments,
        )

    def get_income_breakdown(self, user_inputs: UserInputs) -> dict:
        """
        Get detailed breakdown of all income sources.

        Args:
            user_inputs: User-provided inputs

        Returns:
            Dictionary with income breakdown
        """
        investment_income = self.load_investment_income()
        additional_income = self.get_additional_income(user_inputs)

        return {
            "investment_income": {
                "short_term_capital_gains": investment_income.short_term_capital_gains,
                "short_term_options_gains": investment_income.short_term_options_gains,
                "short_term_non_options_gains": investment_income.short_term_non_options_gains,
                "long_term_capital_gains": investment_income.long_term_capital_gains,
                "total_capital_gains": investment_income.total_capital_gains,
                "dividend_income": investment_income.dividend_income,
                "interest_income": investment_income.interest_income,
                "total": investment_income.total_investment_income,
            },
            "additional_income": {
                "wages": additional_income.wages,
                "business_income": additional_income.business_income,
                "rental_income": additional_income.rental_income,
                "retirement_income": additional_income.retirement_income,
                "social_security": additional_income.social_security,
                "other_income": additional_income.other_income,
                "total": additional_income.total,
            },
            "tax_exempt_interest": additional_income.tax_exempt_interest,
        }
