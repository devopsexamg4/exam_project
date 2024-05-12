# database stuff
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

host = os.getenv("DB_HOST", "pservice")
port = os.getenv("DB_PORT", "5432")
dbname = os.getenv("DB_NAME", "test")
user = os.getenv("DB_USER", "postgres")
password = os.getenv("DB_PASSWORD", "12345")

SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}" # expects these values as environt variables

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()