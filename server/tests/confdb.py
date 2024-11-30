from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from getter_variables import URL_DB


engine = create_engine(URL_DB, echo=True)
Session = sessionmaker(bind=engine, autocommit=False, expire_on_commit=False)
session = Session()
