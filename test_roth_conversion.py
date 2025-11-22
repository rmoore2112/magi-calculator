"""Test script for Roth conversion feature."""

from decimal import Decimal
from pathlib import Path
from src.models.user_inputs import UserInputs, FilingStatus
from src.calculators.magi_calculator import MAGICalculator

DATA_DIR = Path("data")

def main():
    """Test the Roth conversion feature."""
    print("=" * 70)
    print("Testing Roth Conversion Feature")
    print("=" * 70)

    # Find CSV files
    gains_files = list(DATA_DIR.glob("*GainLoss*.csv"))
    transaction_files = list(DATA_DIR.glob("*Transactions*.csv"))

    if not gains_files or not transaction_files:
        print("ERROR: CSV files not found")
        return False

    gains_file = sorted(gains_files, reverse=True)[0]
    transaction_file = sorted(transaction_files, reverse=True)[0]

    calculator = MAGICalculator(gains_file, transaction_file)

    # Test Case 1: No target MAGI (should not show suggestion)
    print("\n" + "=" * 70)
    print("Test Case 1: No Target MAGI")
    print("=" * 70)

    user_inputs = UserInputs(
        filing_status=FilingStatus.SINGLE,
        tax_year=2025,
        target_magi=None,
    )

    result = calculator.calculate(user_inputs)

    print(f"  Current MAGI: ${result.magi:,.2f}")
    print(f"  Target MAGI: None")
    print(f"  Roth Suggestion: {'Yes' if result.roth_suggestion else 'No'}")

    if result.roth_suggestion:
        print("  ✗ FAIL: Should not show suggestion without target MAGI")
        return False
    else:
        print("  ✓ PASS: Correctly hidden without target MAGI")

    # Test Case 2: Target MAGI below current (should not show suggestion)
    print("\n" + "=" * 70)
    print("Test Case 2: Target MAGI Below Current")
    print("=" * 70)

    user_inputs = UserInputs(
        filing_status=FilingStatus.SINGLE,
        tax_year=2025,
        target_magi=Decimal("20000"),  # Below current
    )

    result = calculator.calculate(user_inputs)

    print(f"  Current MAGI: ${result.magi:,.2f}")
    print(f"  Target MAGI: $20,000.00")
    print(f"  Roth Suggestion: {'Yes' if result.roth_suggestion else 'No'}")

    if result.roth_suggestion:
        print("  ✗ FAIL: Should not show suggestion when target < current")
        return False
    else:
        print("  ✓ PASS: Correctly hidden when target < current")

    # Test Case 3: Target MAGI above current (should show suggestion)
    print("\n" + "=" * 70)
    print("Test Case 3: Target MAGI Above Current")
    print("=" * 70)

    user_inputs = UserInputs(
        filing_status=FilingStatus.SINGLE,
        tax_year=2025,
        target_magi=Decimal("50000"),  # Above current
    )

    result = calculator.calculate(user_inputs)

    print(f"  Current MAGI: ${result.magi:,.2f}")
    print(f"  Target MAGI: $50,000.00")
    print(f"  Roth Suggestion: {'Yes' if result.roth_suggestion else 'No'}")

    if not result.roth_suggestion:
        print("  ✗ FAIL: Should show suggestion when target > current")
        return False

    print(f"\n  Roth Conversion Details:")
    print(f"    Suggested conversion: ${result.roth_suggestion.suggested_conversion:,.2f}")
    print(f"    Tax on conversion: ${result.roth_suggestion.conversion_tax:,.2f}")
    print(f"    Marginal rate: {result.roth_suggestion.marginal_rate:.2f}%")
    print(f"    Current total tax: ${result.roth_suggestion.current_total_tax:,.2f}")
    print(f"    New total tax: ${result.roth_suggestion.new_total_tax:,.2f}")

    # Verify the conversion amount is correct
    expected_conversion = Decimal("50000") - result.magi
    actual_conversion = result.roth_suggestion.suggested_conversion

    if abs(expected_conversion - actual_conversion) < Decimal("0.01"):
        print(f"  ✓ PASS: Conversion amount correct (${actual_conversion:,.2f})")
    else:
        print(f"  ✗ FAIL: Expected ${expected_conversion:,.2f}, got ${actual_conversion:,.2f}")
        return False

    # Test Case 4: MFJ with wages and target MAGI
    print("\n" + "=" * 70)
    print("Test Case 4: Married Filing Jointly with Wages")
    print("=" * 70)

    user_inputs = UserInputs(
        filing_status=FilingStatus.MARRIED_FILING_JOINTLY,
        tax_year=2025,
        wages=Decimal("75000"),
        target_magi=Decimal("120000"),
    )

    result = calculator.calculate(user_inputs)

    print(f"  Current MAGI: ${result.magi:,.2f}")
    print(f"  Target MAGI: $120,000.00")
    print(f"  Roth Suggestion: {'Yes' if result.roth_suggestion else 'No'}")

    if result.roth_suggestion:
        print(f"\n  Roth Conversion Details:")
        print(f"    Suggested conversion: ${result.roth_suggestion.suggested_conversion:,.2f}")
        print(f"    Tax on conversion: ${result.roth_suggestion.conversion_tax:,.2f}")
        print(f"    Marginal rate: {result.roth_suggestion.marginal_rate:.2f}%")
        print(f"  ✓ PASS: Suggestion shown correctly")
    else:
        print(f"  ✗ FAIL: Should show suggestion")
        return False

    print("\n" + "=" * 70)
    print("ALL ROTH CONVERSION TESTS PASSED!")
    print("=" * 70)
    print("\nThe Roth conversion feature is working correctly.")
    print("You can now run the web application to see it in action:")
    print("  ./run.sh")

    return True

if __name__ == "__main__":
    main()
