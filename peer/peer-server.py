import base64
import digsig
from flask import Flask, jsonify, request
import json
import os
import sys

port_number = int(sys.argv[1])
file_directory = sys.argv[2]
certificate_path = sys.argv[3]
private_key_path = sys.argv[4]

app = Flask(__name__)

@app.route('/files/<keyword>')
def get_file_names(keyword):
  """Send a list of files this peer has associated with the keyword to the
  requesting peer"""
  directory_path = os.path.join(file_directory, keyword)
  if not os.path.exists(directory_path):
    return jsonify({'message': f'No files found with keyword {keyword}'}), 404
  file_names = os.listdir(directory_path)
  return jsonify(file_names)

@app.route('/files/<keyword>/<file_name>', methods=['POST'])
def get_file(keyword, file_name):
  """Send the file specified by the keyword and file name to the requesting peer
  along with the digital signature"""
  # check if the file exists
  file_path = os.path.join(file_directory, keyword, file_name)
  if not os.path.exists(file_path):
    return jsonify({'message': f'File {file_name} not found'}), 404
  with open(file_path) as file_to_send:
    file_data = file_to_send.read()
  digital_signature = digsig.generate_signature(private_key_path, file_data)
  # base64 encode the signature as we cannot send raw bytes over JSON
  base64_encoded_signature = base64.b64encode(digital_signature).decode()
  body = json.loads(request.data)
  # retrieve the provided nonce and echo it back to the peer
  nonce = body['nonce']
  return jsonify({'file_data': file_data,
                  'digital_signature': base64_encoded_signature,
                  'nonce': nonce})

if __name__ == "__main__":
  app.run(ssl_context=(certificate_path, private_key_path),
          port=port_number,
          host='0.0.0.0',
          debug=True)
