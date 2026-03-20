from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

DATABASE_URL = URL.create(
    "postgresql+psycopg2",
    username="postgres",
    password="Nagagokul2403@",
    host="127.0.0.1",
    port=5432,
    database="AIRI",
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

#this is a dependency that will be used to get a database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

