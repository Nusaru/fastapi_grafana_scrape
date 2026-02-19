import os
import platform

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

# SQLALCHEMY_DATABASE_URL = "sqlite:///./scraper.db"
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
if platform.system() == "Windows":
    SQLALCHEMY_DATABASE_URL = os.getenv("LOCAL_DB_URL")
else:
    SQLALCHEMY_DATABASE_URL = os.getenv("DOCKER_DB_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_ctx():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close
