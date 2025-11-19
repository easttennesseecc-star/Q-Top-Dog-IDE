from __future__ import annotations

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Mirror the app's default DB URL; override via env in deployments/tests
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./topdog_ide.db")

engine = create_engine(
	DATABASE_URL,
	connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
	db: Session = SessionLocal()
	try:
		yield db
	finally:
		db.close()

__all__ = ["engine", "SessionLocal", "get_db"]
