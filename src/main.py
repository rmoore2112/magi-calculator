"""Main entry point for MAGI Calculator web application."""

from flask import Flask
from pathlib import Path


def create_app():
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent / "web" / "templates"),
        static_folder=str(Path(__file__).parent / "web" / "static"),
    )

    # Configuration
    app.config["SECRET_KEY"] = "magi-calculator-secret-key-change-in-production"
    app.config["JSON_SORT_KEYS"] = False

    # Register blueprints
    from .web.routes import main_bp

    app.register_blueprint(main_bp)

    return app


def main():
    """Run the Flask development server."""
    app = create_app()
    port = 5001  # Use 5001 to avoid conflicts with macOS AirPlay Receiver
    print("=" * 70)
    print("MAGI Calculator - Modified Adjusted Gross Income Calculator")
    print("=" * 70)
    print("\nStarting web server...")
    print(f"Open your browser and navigate to: http://127.0.0.1:{port}")
    print("\nPress CTRL+C to stop the server")
    print("=" * 70)
    app.run(debug=True, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
