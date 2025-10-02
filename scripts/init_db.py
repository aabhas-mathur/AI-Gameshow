#!/usr/bin/env python3
"""
Initialize the database with tables
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db
from app.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Initialize database tables"""
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()