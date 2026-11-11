from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.models import Base

DEFAULT_DATABASE_URL = "sqlite:///data/festa_ifc.db"


def get_database_url() -> str:
    """Return the configured URL, preferring the environment over Streamlit secrets."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    try:
        import streamlit as st

        database_url = st.secrets.get("DATABASE_URL")
    except (ImportError, FileNotFoundError):
        database_url = None

    return str(database_url) if database_url else DEFAULT_DATABASE_URL


def create_database_engine(database_url: str | None = None) -> Engine:
    url = database_url or get_database_url()
    if url.startswith("sqlite:///") and not url.startswith("sqlite:////"):
        database_path = Path(url.removeprefix("sqlite:///"))
        if database_path.parent != Path("."):
            database_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(url, connect_args={"check_same_thread": False} if url.startswith("sqlite") else {})


engine = create_database_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def initialize_database(database_engine: Engine = engine) -> None:
    Base.metadata.create_all(database_engine)


def get_session() -> Session:
    return SessionLocal()
