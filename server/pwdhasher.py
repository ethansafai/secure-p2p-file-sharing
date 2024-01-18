import bcrypt

def hash_password(password: str) -> bytes:
  """Salt and hash the user's password and return the result"""
  salt = bcrypt.gensalt()
  hashed_password = bcrypt.hashpw(password.encode(), salt)
  return hashed_password

def passwords_match(password: str, hashed: str) -> bool:
  """Check the user's password against the provided hash"""
  return bcrypt.checkpw(password.encode(), hashed.encode())
