"""Simple validation script to test CSV file structure."""

from pathlib import Path
import csv

DATA_DIR = Path("data")

def find_csv_files():
    """Find the CSV files in the data directory."""
    gains_files = list(DATA_DIR.glob("*GainLoss*.csv"))
    transaction_files = list(DATA_DIR.glob("*Transactions*.csv"))

    return gains_files, transaction_files

def validate_gains_csv(file_path):
    """Validate the structure of the gains CSV file."""
    print(f"\nValidating: {file_path.name}")
    print("=" * 70)

    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

        print(f"Number of columns: {len(headers)}")
        print(f"Headers: {', '.join(headers[:5])}...")

        rows = list(reader)
        print(f"Number of transactions: {len(rows)}")

        if rows:
            print(f"\nSample row:")
            sample = rows[0]
            for key in ['Symbol', 'Name', 'Closed Date', 'Gain/Loss ($)', 'Term']:
                print(f"  {key}: {sample.get(key, 'N/A')}")

    return True

def validate_transactions_csv(file_path):
    """Validate the structure of the transactions CSV file."""
    print(f"\nValidating: {file_path.name}")
    print("=" * 70)

    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

        print(f"Number of columns: {len(headers)}")
        print(f"Headers: {', '.join(headers)}")

        rows = list(reader)
        print(f"Number of transactions: {len(rows)}")

        # Count transaction types
        actions = {}
        for row in rows:
            action = row.get('Action', 'Unknown')
            actions[action] = actions.get(action, 0) + 1

        print(f"\nTransaction types found:")
        for action, count in sorted(actions.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {action}: {count}")

    return True

def main():
    """Main validation function."""
    print("MAGI Calculator - CSV File Validation")
    print("=" * 70)

    # Check if data directory exists
    if not DATA_DIR.exists():
        print(f"ERROR: Data directory not found: {DATA_DIR}")
        return False

    # Find CSV files
    gains_files, transaction_files = find_csv_files()

    if not gains_files:
        print("ERROR: No gains CSV files found in data directory")
        return False

    if not transaction_files:
        print("ERROR: No transaction CSV files found in data directory")
        return False

    print(f"\nFound {len(gains_files)} gains file(s)")
    print(f"Found {len(transaction_files)} transaction file(s)")

    # Validate the most recent files
    gains_file = sorted(gains_files, reverse=True)[0]
    transaction_file = sorted(transaction_files, reverse=True)[0]

    try:
        validate_gains_csv(gains_file)
        validate_transactions_csv(transaction_file)

        print("\n" + "=" * 70)
        print("VALIDATION SUCCESSFUL!")
        print("=" * 70)
        print("\nYour CSV files are properly formatted.")
        print("You can now run the application with:")
        print("  uv run python src/main.py")
        print("\nOr with standard Python:")
        print("  python3 src/main.py")
        print("\n(Make sure to install dependencies first)")

        return True

    except Exception as e:
        print(f"\nERROR during validation: {e}")
        return False

if __name__ == "__main__":
    main()
