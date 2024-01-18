from __future__ import annotations
import jwt
import os
import time

JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = 60 * 60
JWT_SECRET = os.environ.get('JWT_SECRET', 'secret')

def create_token(username: str) -> str:
  """Generate a JWT for the user with their username stored inside"""
  return jwt.encode({
                      'username': username,
                      'iat': int(time.time()) # note the time when JWT was made
                    },
                    JWT_SECRET,
                    JWT_ALGORITHM)

def verify_token(token: str) -> tuple(bool, str):
  """Returns True and the username stored in the token if the token is valid,
  otherwise, returns False and an empty string"""
  try:
    # decode the token
    decoded = jwt.decode(token, JWT_SECRET, [JWT_ALGORITHM])
    # ensure the token is not expired
    if int(time.time()) - decoded['iat'] >= JWT_EXPIRATION:
      return False, ''
    return True, decoded['username']
  except:
    return False, ''
