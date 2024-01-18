from __future__ import annotations
from db import session, User

def add_user(username: str, hashed_password: str) -> None:
  """Add a user to the index database"""
  session.add(User(username=username, hashed_password=hashed_password))
  session.commit()

def find_user(username: str) -> User | None:
  """Search for a user in the index database"""
  user = session.query(User).filter(User.username == username).first()
  return user

def update_user(username: str, domain_name: str, port_number: str) -> None:
  """Update a users domain name and port number in the index database"""
  user = session.query(User).filter(User.username == username).first()
  if user is None:
    raise Exception('User not found')
  user.domain_name = domain_name
  user.port_number = port_number
  session.commit()
