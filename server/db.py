from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# create a connection to the sqlite database
engine = create_engine('sqlite:///index.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class User(Base):
  """A model to represent a user in the database"""
  __tablename__ = 'users'
  username = Column(String, primary_key=True)
  hashed_password = Column(String)
  domain_name = Column(String)
  port_number = Column(String)

class File(Base):
  """A model to represent a file in the database associated with a user and 
  file keyword"""
  __tablename__ = 'files'
  id = Column(Integer, primary_key=True)
  username = Column(String)
  filename = Column(String)
  keyword = Column(String)

# generate the sqlite tables based on the above schema
Base.metadata.create_all(bind=engine)
