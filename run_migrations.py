#!/usr/bin/env python3
"""
Workflow Database Migration Runner

Runs database migrations for Q Assistant Orchestration workflow system.
Usage: python run_migrations.py [--database-url "postgres://..."]
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.workflow_db_manager import WorkflowDatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_migrations(database_url: str) -> bool:
    """
    Run database migrations for workflow orchestration.
    
    Args:
        database_url: SQLAlchemy database connection URL
        
    Returns:
        True if migrations successful
    """
    logger.info("=" * 60)
    logger.info("🚀 Q Assistant Orchestration Database Migration")
    logger.info("=" * 60)
    
    try:
        logger.info(f"\n📦 Connecting to database: {database_url.split('/')[-1]}")
        
        # Create database manager
        manager = WorkflowDatabaseManager(database_url)
        
        # Run migrations
        logger.info("\n🔄 Running migrations...")
        if manager.run_migrations():
            logger.info("✅ Migrations completed successfully")
        else:
            logger.error("❌ Migrations failed")
            return False
        
        # Verify schema
        logger.info("\n🔍 Verifying schema...")
        if manager.verify_schema():
            logger.info("✅ Schema verification passed")
        else:
            logger.error("❌ Schema verification failed")
            return False
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ All migrations completed successfully!")
        logger.info("=" * 60)
        logger.info("\n📊 Workflow orchestration database is ready for use")
        logger.info("   - build_workflows table created")
        logger.info("   - workflow_handoffs table created")
        logger.info("   - workflow_events table created")
        logger.info("\n🎯 Next steps:")
        logger.info("   1. Start backend: python -m backend.main")
        logger.info("   2. Create workflow: POST /api/workflows/{project_id}/start")
        logger.info("   3. Advance workflow: POST /api/workflows/{workflow_id}/advance")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Migration failed: {str(e)}")
        logger.error("\n📋 Troubleshooting:")
        logger.error("   - Check database connection string")
        logger.error("   - Verify database server is running")
        logger.error("   - Check database credentials")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run database migrations for Q Assistant Orchestration"
    )
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", "sqlite:///./topdog_ide.db"),
        help="Database connection URL (default: SQLite topdog_ide.db)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run migrations
    success = run_migrations(args.database_url)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
