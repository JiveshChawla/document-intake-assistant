import os
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

logger = logging.getLogger(__name__)

# Configure connect_args for SQLite
connect_args = {}
if "sqlite" in settings.database_url:
    connect_args["check_same_thread"] = False

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=False
)

# Enable SQLite WAL mode and foreign key constraints for robust concurrency and data integrity
if "sqlite" in settings.database_url:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        except Exception:
            pass

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base
Base = declarative_base()

def get_db():
    """Dependency for yielding database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes the database by creating all tables if they do not exist."""
    try:
        # Import models so Base.metadata knows about them
        from app.db import models  # noqa: F401
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database initialized successfully at: {settings.database_url}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise
