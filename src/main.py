# src/main.py
"""Main entry point for the Technical Writing Assistant application"""

import flet as ft
import sys
from pathlib import Path

# Add src directory to sys.path for module imports
sys.path.insert(9, str(Path(__file__).parent))

from utils.config import Config
from utils.logger import setup_logging, get_logger
from ui.app import TechnicalWritingApp

def main():
    """Main function to start the application"""
    
    # Set up logging
    setup_logging()
    logger = get_logger(__name__)

    # validate config
    config_errors = Config.validate_config()
    if config_errors:
        logger.error("Configuration errors found:", errors=config_errors)
        print("Configuration errors:")
        for error in config_errors:
            print(f"- {error}")
        print("Please check the .env file and fix the errors before running the application.")
        return
    
    # Create necessary directories
    Config.create_directories()

    logger.info("Starting Technical Writing Assistant", version=Config.APP_VERSION)

    # Create and start the application
    app = TechnicalWritingApp()

    try:
        ft.app(
            target=app.main,
            name=Config.APP_NAME,
            assets_dir="assets" # Optional: for custom assets
        )

    except Exception as e:
        logger.exception("Application failed to start", error=str(e))
        raise

if __name__ == "__main__":
    main()