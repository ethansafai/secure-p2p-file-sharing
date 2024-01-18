import argparse
import base64
import digsig
import os
import requests
import secrets
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('-hostname', required=True)
parser.add_argument('-username', required=True)
parser.add_argument('-password', required=True)
parser.add_argument('-file_directory', required=True)
parser.add_argument('-certificate', required=True)
parser.add_argument('-private_key', required=True)
parser.add_argument('-index_server_name', required=True)
parser.add_argument('-peer_server_port', required=True)
args = parser.parse_args()

# set up SSL verification (trust the peer and indexing server certificates)
base_url = f'https://{args.index_server_name}'
session = requests.Session()
session.verify = os.path.join('..', 'certificates')

def generate_nonce(length: int=16) -> str:
  """Generate a cryptographically secure nonce."""
  return secrets.token_hex(length)

def authenticate(username: str, password: str):
  """Sends peer credentials to indexing server to retrieve JWT"""
  creds = {'username': username, 'password': password}
  response = session.post(f'{base_url}/auth', json=creds)
  if not response.ok:
    raise Exception(response.json())

def sync():
  """Send domain name, port number of peer server, and list of files to
  indexing server (as well as the associated keyword)"""
  keywords = os.listdir(args.file_directory)
  peer_files = []
  for keyword in keywords:
    keyword_files = os.listdir(os.path.join(args.file_directory, keyword))
    for keyword_file in keyword_files:
      peer_files.append({'filename': keyword_file, 'keyword': keyword})

  data = {'domain_name': args.hostname, 
          'port_number': args.peer_server_port, 
          'files': peer_files}
  response = session.post(f'{base_url}/sync', json=data)
  if not response.ok:
    raise Exception(response.json())

def search_files(keyword: str):
  """Search for and download all files associated with the specified keyword"""
  # get a list of peers having files associated with the keyword
  response = session.get(f'{base_url}/files/{keyword}')
  if not response.ok:
    raise Exception(response.json())
  peers = response.json()
  print(peers)

  # contact each peer for their files
  for peer in peers:
    # retrieve a list of files associated with the keyword stored by the peer
    domain_name, port_number = peer['domain_name'], peer['port_number']
    response = session.get(
      f'https://localhost:{port_number}/files/{keyword}'
    )
    if not response.ok:
      raise Exception(response.json())
    file_names = response.json()
    print(f'Files from {domain_name}: {file_names}\n')

    # download each file
    for file_name in file_names:
      get_file(domain_name, port_number, keyword, file_name)
    print()

def save_file(keyword: str, file_name: str, data: str):
  """Save the file to the peer's file system (the file will go in a directory
  named after the file's keyword)"""
  directory_path = os.path.join(args.file_directory, keyword)
  # make a directory for the keyword if one does not already exist
  if not os.path.exists(directory_path):
    os.mkdir(directory_path)
  # write the file to the system
  file_path = os.path.join(directory_path, file_name)
  with open(file_path, 'w') as new_file:
    new_file.write(data)

def get_file(domain_name: str, port_number: str, keyword: str, file_name: str):
  """Retrieve the specified file from the peer and save it to the local
  filesystem if the digital signature is successfully verified"""
  # generate nonce
  generated_nonce = generate_nonce()
  post_data = {'nonce': generated_nonce}
  # retrieve the file data and digital signature from the peer
  response = session.post(
    f'https://localhost:{port_number}/files/{keyword}/{file_name}',
    json=post_data
  )
  if not response.ok:
    raise Exception(response.json())

  data = response.json() 
  file_data = data['file_data']
  
  # ensure the received nonce matches the one that was sent
  received_nonce = data['nonce']
  if generated_nonce != received_nonce:
    print('- Nonces do not match, skipping...')
    return

  # retrieve and decode the digital signature
  digital_signature = data['digital_signature']
  base64_decoded_signature = base64.b64decode(digital_signature)

  print(f'File data for file {file_name}:')
  print(file_data)
  print('- Nonces match')

  peer_certificate_path = os.path.join('..', 'certificates',
                                       f'{domain_name}-server.crt')
  # verify the digital signature
  if digsig.signature_is_valid(peer_certificate_path, file_data,
                               base64_decoded_signature):
    print('- Signature ok')
    # save the file to this peer's directory
    save_file(keyword, file_name, file_data)
  else:
    # the digital signature is invalid, do not save the file
    print('- Signature invalid, skipping...')

def main():
  """Display the user menu and allow the user to search for and download files
  from other peers"""
  # start peer server
  certificate_path = os.path.join('..', 'certificates', args.certificate)
  private_key_path = os.path.join('..', 'keys', args.private_key)
  peer_server_command = f'python peer-server.py {args.peer_server_port} '\
                        f'{args.file_directory} {certificate_path} '\
                        f'{private_key_path}'
  process = subprocess.Popen(peer_server_command, stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, stdin=subprocess.PIPE, 
                            shell=False)
  # authenticate with the indexing server
  print('Authenticating...')
  authenticate(args.username, args.password)
  print('Success')
  print('Sending list of files to server...')
  sync()
  print('Success')

  # generate the user menu
  menu_items = ['Update index server', 'Search for file',
                'Exit and shut down peer server']
  menu = ''
  for i in range(len(menu_items)):
    menu += f'{i + 1}. {menu_items[i]}\n'

  while True:
    print('\n' + menu, end='')
    choice = int(input('Enter a choice: '))
    if choice < 1 or choice > 3:
      print('Invalid choice, please try again\n')
      continue
    
    if choice == 1:
      # update the indexing server
      print('Sending list of files to server...')
      sync()
      print('Success')
    elif choice == 2:
      # search for a keyword
      keyword = input('Keyword to search for: ')
      search_files(keyword) 
    else:
      # exit and shut down the peer server
      print('Goodbye')
      break

  # stop the peer server
  process.kill()

if __name__ == "__main__":
  main()
