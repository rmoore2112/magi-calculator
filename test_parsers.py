"""Test script to validate the parsers work correctly."""

from pathlib import Path
from src.parsers.gains_parser import parse_gains_csv, get_gains_summary
from src.parsers.transactions_parser import parse_transactions_csv, get_transactions_summary

DATA_DIR = Path("data")

def main():
    """Test the parsers with actual data."""
    print("=" * 70)
    print("Testing MAGI Calculator Parsers")
    print("=" * 70)

    # Find CSV files
    gains_files = list(DATA_DIR.glob("*GainLoss*.csv"))
    transaction_files = list(DATA_DIR.glob("*Transactions*.csv"))

    if not gains_files or not transaction_files:
        print("ERROR: CSV files not found")
        return False

    gains_file = sorted(gains_files, reverse=True)[0]
    transaction_file = sorted(transaction_files, reverse=True)[0]

    print(f"\nParsing: {gains_file.name}")
    print("-" * 70)

    try:
        gains = parse_gains_csv(gains_file)
        print(f"Successfully parsed {len(gains)} realized gain/loss entries")

        summary = get_gains_summary(gains)
        print(f"\nGains Summary:")
        print(f"  Total transactions: {summary['total_transactions']}")
        print(f"  Short-term gains: ${summary['short_term_gains']:,.2f}")
        print(f"  Long-term gains: ${summary['long_term_gains']:,.2f}")
        print(f"  Total gains/losses: ${summary['total_gains']:,.2f}")
        print(f"  Wash sales: {summary['num_wash_sales']}")

        if gains:
            print(f"\nSample transaction:")
            g = gains[0]
            print(f"  Symbol: {g.symbol}")
            print(f"  Name: {g.name}")
            print(f"  Term: {g.term}")
            print(f"  Gain/Loss: ${g.gain_loss:,.2f}")
            print(f"  Opened: {g.opened_date}")
            print(f"  Closed: {g.closed_date}")

    except Exception as e:
        print(f"ERROR parsing gains file: {e}")
        import traceback
        traceback.print_exc()
        return False

    print(f"\n\nParsing: {transaction_file.name}")
    print("-" * 70)

    try:
        transactions = parse_transactions_csv(transaction_file)
        print(f"Successfully parsed {len(transactions)} transactions")

        summary = get_transactions_summary(transactions)
        print(f"\nTransactions Summary:")
        print(f"  Total transactions: {summary['total_transactions']}")
        print(f"  Dividend income: ${summary['dividend_income']:,.2f}")
        print(f"  Interest income: ${summary['interest_income']:,.2f}")
        print(f"  Total income: ${summary['total_income_from_transactions']:,.2f}")
        print(f"  Total fees: ${summary['total_fees']:,.2f}")

        if transactions:
            # Find a dividend transaction
            dividend_txn = next((t for t in transactions if t.is_dividend), None)
            if dividend_txn:
                print(f"\nSample dividend transaction:")
                print(f"  Date: {dividend_txn.date}")
                print(f"  Action: {dividend_txn.action}")
                print(f"  Symbol: {dividend_txn.symbol}")
                print(f"  Amount: ${dividend_txn.amount:,.2f}")

    except Exception as e:
        print(f"ERROR parsing transactions file: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70)
    print("\nThe parsers are working correctly.")
    print("You can now run the web application:")
    print("  uv run python src/main.py")

    return True

if __name__ == "__main__":
    main()
