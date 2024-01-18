import authtoken
import files
from flask import Flask, jsonify, make_response, request
import json
import pwdhasher
import os
import users

app = Flask(__name__)

@app.route('/users', methods=['POST'])
def register():
  """Register a new user"""
  try:
    body = json.loads(request.data)
    username, password = body['username'], body['password']
    
    if users.find_user(username) is not None:
      return jsonify({'message': 'User already exists'}), 400
    
    # hash and salt the user's password and save their username and hashed
    # password to the database
    hashed_password = pwdhasher.hash_password(password).decode()
    users.add_user(username, hashed_password)
    return jsonify({'message': 'User created'}), 201
  except:
    error_msg = 'Provide a username and password in JSON format'
    return jsonify({'message': error_msg}), 400

@app.route('/auth', methods=['POST'])
def authenticate():
  """Check user's credentials and issue auth token if valid"""
  try:
    body = json.loads(request.data)
    username, password = body['username'], body['password']

    user = users.find_user(username)
    if user is None or not pwdhasher.passwords_match(password, 
                                                     user.hashed_password):
      return jsonify({'message': 'Invalid credentials'}), 404
    
    # the users credentials are valid, so issue a JWT to the peer for
    # authorization (stored as a cookie)
    token = authtoken.create_token(username)
    response = make_response(jsonify({'message': 'Success'}), 200)
    response.set_cookie('token', token)
    return response
  except:
    error_msg = 'Provide a username and password in JSON format'
    return jsonify({'message': error_msg}), 400

@app.route('/sync', methods=['POST'])
def sync():
  """Receive user's domain name, port number, and list of files"""
  try:
    # ensure the user has been authenticated
    authenticated, username = authtoken.verify_token(
      request.cookies.get('token')
    )
    if not authenticated:
      return jsonify({'message': 'Unauthorized'}), 401

    body = json.loads(request.data)
    domain_name, port_number, user_files = body['domain_name'],\
                                           body['port_number'],\
                                           body['files']
    # update the index database with the provided information
    users.update_user(username, domain_name, port_number)
    files.delete_user_files(username)
    for user_file in user_files:
      files.add_file(username, user_file['filename'], user_file['keyword'])
    return jsonify({'message': 'Records updated successfully'}), 200
  except:
    error_msg = 'Provide domain name, port number, and list of files in JSON '\
                'format'
    return jsonify({'message': error_msg}), 400

@app.route('/files/<keyword>')
def search_files(keyword):
  """Return a list of peers having files associated with the keyword to the
  requesting peer"""
  if not user_authenticated():
    return jsonify({'message': 'Unauthorized'}), 401
  peers = files.search_files(keyword)
  return jsonify(peers)

def user_authenticated() -> bool:
  """Returns True if the user's JWT is valid"""
  valid, _ = authtoken.verify_token(request.cookies.get('token'))
  return valid

if __name__ == "__main__":
  app.run(ssl_context=(os.path.join('..', 'certificates', 'index-server.crt'),
                       os.path.join('..', 'keys', 'index-server.key')),
          port=443,
          host='0.0.0.0',
          debug=True)
