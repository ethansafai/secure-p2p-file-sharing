from __future__ import annotations
from db import File, User, session

def add_file(username: str, filename: str, keyword: str) -> None:
  """Add a record for a peer file to the index database"""
  # ensure there are no duplicate entries
  user_file = session.query(File).filter(File.username == username, 
                                         File.filename == filename, 
                                         File.keyword == keyword).first()
  if user_file is not None:
    print('*** Attempt at creating duplicate file, skipping... ****')
    print(f'Attempt: [{username} {filename} {keyword}]')
    return
  
  session.add(File(username=username, filename=filename, keyword=keyword))
  session.commit()

def get_user_files(username: str) -> list[File]:
  """Retrieve a list of files associated with the specified user"""
  user_files = session.query(File).filter(File.username == username).all()
  return user_files

def delete_user_files(username: str) -> None:
  """Delete all files associated with the specified user"""
  session.query(File).filter(File.username == username).delete()
  session.commit()

def search_files(keyword: str) -> list[dict]:
  """Search for users having files associated with the specified keyword"""
  related_files = session.query(File).filter(File.keyword == keyword).all()
  if len(related_files) == 0:
    return []
  # retrieve the usernames of the peers having the relevant files
  usernames = set([related_file.username for related_file in related_files])
  peers = []
  # get the domain name and port numbers of those peers and return them
  for username in usernames:
    user = session.query(User).filter(User.username == username).first()
    peers.append({'domain_name': user.domain_name,
                  'port_number': user.port_number})
  return peers
