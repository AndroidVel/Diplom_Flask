from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

engine = create_engine('sqlite:///db.sqlite3', echo=True)
metadata = MetaData()

SessionLocal = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
