"""Flask routes for MAGI calculator web application."""

from decimal import Decimal
from pathlib import Path
from flask import Blueprint, render_template, request, jsonify
import json

from ..models.user_inputs import UserInputs, FilingStatus
from ..calculators.magi_calculator import MAGICalculator
from ..parsers.gains_parser import get_gains_summary
from ..parsers.transactions_parser import get_transactions_summary

# Create blueprint
main_bp = Blueprint("main", __name__)

# Get data directory
DATA_DIR = Path(__file__).parent.parent.parent / "data"


def find_csv_files():
    """Find the CSV files in the data directory."""
    gains_files = list(DATA_DIR.glob("*GainLoss*.csv"))
    transaction_files = list(DATA_DIR.glob("*Transactions*.csv"))

    if not gains_files or not transaction_files:
        return None, None

    # Use the most recent files
    gains_file = sorted(gains_files, reverse=True)[0]
    transaction_file = sorted(transaction_files, reverse=True)[0]

    return gains_file, transaction_file


@main_bp.route("/")
def index():
    """Render the input form."""
    gains_file, transaction_file = find_csv_files()

    if not gains_file or not transaction_file:
        return render_template(
            "error.html",
            error="CSV files not found in data directory. Please ensure your gains and transactions CSV files are in the data folder.",
        )

    return render_template(
        "index.html",
        filing_statuses=[status.value for status in FilingStatus],
        gains_file=gains_file.name,
        transaction_file=transaction_file.name,
    )


@main_bp.route("/calculate", methods=["POST"])
def calculate():
    """Calculate MAGI based on form inputs."""
    try:
        # Get form data
        form_data = request.form

        # Parse filing status
        filing_status_str = form_data.get("filing_status")
        filing_status = None
        for status in FilingStatus:
            if status.value == filing_status_str:
                filing_status = status
                break

        if not filing_status:
            return jsonify({"error": "Invalid filing status"}), 400

        # Parse target MAGI (optional)
        target_magi = form_data.get("target_magi")
        target_magi_decimal = Decimal(target_magi) if target_magi and target_magi.strip() else None

        # Parse user inputs
        user_inputs = UserInputs(
            filing_status=filing_status,
            tax_year=int(form_data.get("tax_year", 2025)),
            target_magi=target_magi_decimal,
            wages=Decimal(form_data.get("wages", 0) or 0),
            business_income=Decimal(form_data.get("business_income", 0) or 0),
            rental_income=Decimal(form_data.get("rental_income", 0) or 0),
            retirement_income=Decimal(form_data.get("retirement_income", 0) or 0),
            social_security=Decimal(form_data.get("social_security", 0) or 0),
            other_income=Decimal(form_data.get("other_income", 0) or 0),
            tax_exempt_interest=Decimal(form_data.get("tax_exempt_interest", 0) or 0),
            use_standard_deduction=form_data.get("use_standard_deduction") == "true",
            itemized_deductions=Decimal(form_data.get("itemized_deductions", 0) or 0),
            student_loan_interest=Decimal(form_data.get("student_loan_interest", 0) or 0),
            ira_contributions=Decimal(form_data.get("ira_contributions", 0) or 0),
            hsa_contributions=Decimal(form_data.get("hsa_contributions", 0) or 0),
            self_employment_tax=Decimal(form_data.get("self_employment_tax", 0) or 0),
            other_adjustments=Decimal(form_data.get("other_adjustments", 0) or 0),
        )

        # Find CSV files
        gains_file, transaction_file = find_csv_files()

        if not gains_file or not transaction_file:
            return jsonify({"error": "CSV files not found"}), 500

        # Calculate MAGI
        calculator = MAGICalculator(gains_file, transaction_file)
        result = calculator.calculate(user_inputs)

        # Get IRMAA info
        irmaa_info = calculator.get_irmaa_info(result.magi, filing_status)

        # Get detailed transactions
        detailed_transactions = calculator.get_detailed_transactions()

        # Render report template
        return render_template(
            "report.html",
            result=result,
            irmaa_info=irmaa_info,
            detailed_transactions=detailed_transactions,
            user_inputs=user_inputs,
        )

    except Exception as e:
        return render_template("error.html", error=str(e)), 500


@main_bp.route("/api/data-summary")
def data_summary():
    """Get summary of data files (for displaying on form page)."""
    try:
        gains_file, transaction_file = find_csv_files()

        if not gains_file or not transaction_file:
            return jsonify({"error": "CSV files not found"}), 404

        # Import parsers
        from ..parsers.gains_parser import parse_gains_csv
        from ..parsers.transactions_parser import parse_transactions_csv

        # Parse files
        gains = parse_gains_csv(gains_file)
        transactions = parse_transactions_csv(transaction_file)

        # Get summaries
        gains_summary = get_gains_summary(gains)
        transactions_summary = get_transactions_summary(transactions)

        return jsonify(
            {
                "gains_summary": {
                    k: float(v) if isinstance(v, Decimal) else v
                    for k, v in gains_summary.items()
                },
                "transactions_summary": {
                    k: float(v) if isinstance(v, Decimal) else v
                    for k, v in transactions_summary.items()
                },
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
