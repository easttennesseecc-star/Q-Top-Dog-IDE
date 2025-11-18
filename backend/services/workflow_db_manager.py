"""
Database initialization for workflow orchestration

Handles database setup, migrations, and initialization for the orchestration system.
"""

import os
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from backend.models.workflow import Base, BuildWorkflow, WorkflowHandoff, WorkflowEvent

logger = logging.getLogger(__name__)


class WorkflowDatabaseManager:
    """Manages workflow database setup and initialization"""
    
    def __init__(self, database_url: str):
        """
        Initialize database manager
        
        Args:
            database_url: SQLAlchemy database connection URL
        """
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def init_database(self) -> bool:
        """
        Initialize database schema and create all tables.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing workflow database...")
            
            # Create all tables defined in Base metadata
            Base.metadata.create_all(self.engine)
            
            logger.info("Workflow database tables created successfully")
            logger.info("   - build_workflows table created")
            logger.info("   - workflow_handoffs table created")
            logger.info("   - workflow_events table created")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize workflow database: {str(e)}")
            return False
    
    def run_migrations(self) -> bool:
        """
        Run SQL migration scripts for workflow tables.
        
        Returns:
            True if migrations successful, False otherwise
        """
        try:
            logger.info("Running workflow database migrations...")
            
            # Get migrations directory
            migrations_dir = os.path.join(
                os.path.dirname(__file__),
                "..",
                "migrations"
            )
            
            migration_file = os.path.join(migrations_dir, "001_create_workflow_tables.sql")
            
            if not os.path.exists(migration_file):
                logger.warning(f"Migration file not found at {migration_file}")
                logger.info("Using SQLAlchemy ORM to create tables instead...")
                return self.init_database()
            
            # Read and execute migration
            with open(migration_file, 'r') as f:
                migration_sql = f.read()
            
            with self.engine.connect() as connection:
                # Split into individual statements and execute
                statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
                
                for statement in statements:
                    if statement and not statement.strip().startswith('--'):
                        try:
                            connection.execute(text(statement))
                        except Exception as e:
                            # Many statements might fail if tables already exist - that's ok
                            logger.debug(f"Migration statement result: {str(e)}")
                
                connection.commit()
            
            logger.info("Database migrations completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to run migrations: {str(e)}")
            # Fall back to ORM initialization
            logger.info("Falling back to SQLAlchemy ORM table creation...")
            return self.init_database()
    
    def verify_schema(self) -> bool:
        """
        Verify that all required tables exist.
        
        Returns:
            True if all tables exist, False otherwise
        """
        try:
            with self.engine.connect() as connection:
                # Get list of tables
                db_inspector = inspect(self.engine)
                existing_tables = db_inspector.get_table_names()
                
                required_tables = {
                    'build_workflows',
                    'workflow_handoffs',
                    'workflow_events'
                }
                
                missing_tables = required_tables - set(existing_tables)
                
                if missing_tables:
                    logger.error(f"Missing tables: {', '.join(missing_tables)}")
                    return False
                
                logger.info("All required workflow tables verified:")
                for table in required_tables:
                    columns = [c['name'] for c in db_inspector.get_columns(table)]
                    logger.info(f"   - {table} ({len(columns)} columns)")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to verify schema: {str(e)}")
            return False
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            SQLAlchemy Session
        """
        return self.SessionLocal()
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()


# Convenience functions for database setup

def init_workflow_database(manager: WorkflowDatabaseManager) -> bool:
    """
    Initialize workflow database using a provided manager instance.
    
    Args:
        manager: An instance of WorkflowDatabaseManager.
        
    Returns:
        True if successful, False otherwise
    """
    # First, try to create tables directly with the ORM. This is the most reliable method.
    if not manager.init_database():
        # If that fails, fall back to trying migrations.
        if not manager.run_migrations():
            logger.error("Both ORM initialization and migrations failed.")
            return False

    # After attempting creation, verify the schema. This is the source of truth.
    return manager.verify_schema()


def get_workflow_db_session(database_url: str) -> Session:
    """
    Get a database session for workflow operations.
    
    Args:
        database_url: SQLAlchemy database connection URL
        
    Returns:
        SQLAlchemy Session
    """
    manager = WorkflowDatabaseManager(database_url)
    return manager.get_session()
