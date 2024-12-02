from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from server.tests.getter_variables import (
    DB_NAME,
    DB_PASSWORD,
    DB_USER,
    DB_HOST,
)


url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
engine = create_engine(url, echo=True)
Session = sessionmaker(bind=engine, autocommit=False, expire_on_commit=False)
session = Session()
