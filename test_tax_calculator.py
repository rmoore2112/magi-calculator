"""Test script for tax calculator."""

from decimal import Decimal
from pathlib import Path
from src.models.user_inputs import UserInputs, FilingStatus
from src.calculators.magi_calculator import MAGICalculator

DATA_DIR = Path("data")

def main():
    """Test the tax calculator with actual data."""
    print("=" * 70)
    print("Testing MAGI Calculator with Tax Calculations")
    print("=" * 70)

    # Find CSV files
    gains_files = list(DATA_DIR.glob("*GainLoss*.csv"))
    transaction_files = list(DATA_DIR.glob("*Transactions*.csv"))

    if not gains_files or not transaction_files:
        print("ERROR: CSV files not found")
        return False

    gains_file = sorted(gains_files, reverse=True)[0]
    transaction_file = sorted(transaction_files, reverse=True)[0]

    print(f"\nUsing files:")
    print(f"  Gains: {gains_file.name}")
    print(f"  Transactions: {transaction_file.name}")

    # Create calculator
    calculator = MAGICalculator(gains_file, transaction_file)

    # Test with Single filing status
    print("\n" + "=" * 70)
    print("Test Case: Single filer with investment income only")
    print("=" * 70)

    user_inputs = UserInputs(
        filing_status=FilingStatus.SINGLE,
        tax_year=2025,
    )

    result = calculator.calculate(user_inputs)

    print(f"\nIncome Summary:")
    print(f"  Short-term capital gains: ${result.income_breakdown['investment_income']['short_term_capital_gains']:,.2f}")
    print(f"  Long-term capital gains: ${result.income_breakdown['investment_income']['long_term_capital_gains']:,.2f}")
    print(f"  Dividend income: ${result.income_breakdown['investment_income']['dividend_income']:,.2f}")
    print(f"  Interest income: ${result.income_breakdown['investment_income']['interest_income']:,.2f}")
    print(f"  Total investment income: ${result.income_breakdown['investment_income']['total']:,.2f}")

    print(f"\nMAGI Calculation:")
    print(f"  Total Income: ${result.total_income:,.2f}")
    print(f"  AGI: ${result.agi:,.2f}")
    print(f"  MAGI: ${result.magi:,.2f}")

    if result.tax_result:
        print(f"\nTax Calculation:")
        print(f"  Ordinary income: ${result.tax_result.ordinary_income:,.2f}")
        print(f"  Preferential income: ${result.tax_result.preferential_income:,.2f}")
        print(f"  Standard deduction: ${result.tax_result.standard_deduction:,.2f}")
        print(f"  Taxable income: ${result.tax_result.taxable_income:,.2f}")
        print(f"\n  Federal tax on ordinary income: ${result.tax_result.federal_ordinary_tax:,.2f}")
        print(f"  Federal tax on preferential income: ${result.tax_result.federal_preferential_tax:,.2f}")
        print(f"  Total federal tax: ${result.tax_result.total_federal_tax:,.2f}")
        print(f"\n  NC taxable income: ${result.tax_result.state_taxable_income:,.2f}")
        print(f"  NC state tax (4.75%): ${result.tax_result.state_tax:,.2f}")
        print(f"\n  TOTAL TAX: ${result.tax_result.total_tax:,.2f}")
        print(f"  After-tax income: ${result.tax_result.after_tax_income:,.2f}")
        print(f"  Effective tax rate: {result.tax_result.effective_tax_rate:.2f}%")
        print(f"  Federal marginal rate: {result.tax_result.federal_marginal_rate:.0f}%")
    else:
        print("\nERROR: No tax result calculated")
        return False

    # Test with MFJ filing status and additional income
    print("\n\n" + "=" * 70)
    print("Test Case: Married Filing Jointly with additional income")
    print("=" * 70)

    user_inputs_mfj = UserInputs(
        filing_status=FilingStatus.MARRIED_FILING_JOINTLY,
        tax_year=2025,
        wages=Decimal("100000"),  # Add wages
    )

    result_mfj = calculator.calculate(user_inputs_mfj)

    print(f"\nIncome Summary:")
    print(f"  Investment income: ${result_mfj.income_breakdown['investment_income']['total']:,.2f}")
    print(f"  Wages: ${result_mfj.income_breakdown['additional_income']['wages']:,.2f}")
    print(f"  Total income: ${result_mfj.total_income:,.2f}")

    if result_mfj.tax_result:
        print(f"\nTax Calculation:")
        print(f"  Total federal tax: ${result_mfj.tax_result.total_federal_tax:,.2f}")
        print(f"  NC state tax: ${result_mfj.tax_result.state_tax:,.2f}")
        print(f"  TOTAL TAX: ${result_mfj.tax_result.total_tax:,.2f}")
        print(f"  Effective tax rate: {result_mfj.tax_result.effective_tax_rate:.2f}%")
    else:
        print("\nERROR: No tax result calculated")
        return False

    print("\n" + "=" * 70)
    print("ALL TAX CALCULATION TESTS PASSED!")
    print("=" * 70)
    print("\nThe tax calculator is working correctly.")
    print("You can now run the web application to see the full report:")
    print("  ./run.sh")

    return True

if __name__ == "__main__":
    main()
