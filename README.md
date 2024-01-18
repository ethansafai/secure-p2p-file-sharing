# Secure Peer-to-peer File Sharing 🔒

## Overview

This project aims to deliver a secure peer-to-peer file sharing application written in Python (using Python 3.11.5 specifically) that provides data confidentiality, integrity, and authenticity. An indexing server keeps track of the files stored by each peer and the associated keyword. When a peer wants to search for a file, it sends the keyword to the server which will return the name and port number of the peer who has the file. The peer will then use the name and port number to connect to the other peer and download the file. Both the indexing server and the peer server make use of Flask REST APIs over HTTPS for confidentiality. Public key certificates and digital signatures of files are also used to ensure authenticity and integrity, respectively.

Example application flow:

![application flow diagram](https://github.com/ethansafai/cpsc352-final-project/blob/main/application-flow.png)

### A quick note about the peer file structure
Each peer has a base file directory which they use to store and download files. The base file directory contains subdirectories which represent different keywords, and within those subfolders are the files associated with that keyword. This makes searching through files and maintaining the mapping between keywords and file names much easier.
```
peer-files/
├─ keyword1/
│  ├─ file1.txt
│  ├─ file2.txt
├─ keyword2/
│  ├─ file3.txt
│  ├─ file4.txt
```

## Indexing Server REST API endpoints

- POST /user - register a peer with a username and password

Example request:
```
{"username": "myusername", "password": "mypassword"}
```

- POST /auth - provide username and password to receive a JWT for authentication

Example request:
```
{"username": "myusername", "password": "mypassword"}
```
- POST /sync - send (from peer) domain name, port number, and list of files and their associated keywords

Example request:
```
{
    "domain_name": "peer1",
    "port_number": "7001",
    "files": [
        {"filename": "horses.txt", "keyword": "horse"}
    ]
}
```
- GET /files/&lt;keyword&gt; - retrieve a list of peers having files assocaited with the specified keyword

Example response:
```
[
    {"domain_name": "peer1", "port_number": "7001"},
    {"domain_name": "peer2", "port_number": "7002"}
]
```

## Peer Server REST API endpoints

- GET /files/&lt;keyword&gt; - send a list of files this peer has associated with the keyword to the requesting peer

Example response:
```
["horse_rock.txt", "horses_are_cool.txt"]
```
- POST /files/&lt;keyword&gt;/&lt;file_name&gt; - sends the file specified by the keyword and file name to the requesting peer, along with the digital signature for the requesting peer to verify (the requesting peer must send a nonce in the request body for the sending peer to echo back)

Example response:
```
{
    "file_data": "I love horses!",
    "digital_signature": "6B+4...",
    "nonce": "c53e..."
}
```

## Running the code

### 1. Installing dependencies:

`pip install -r requirements.txt`

### 2. Starting the server:

```
cd server
python server
```

### 3. Starting the peers:

<em>**Note:** change into the 'peer' directory before running these commands, and open up a new terminal for each one. (port numbers and credentials can be changed based on requirements, below is merely an example)</em>

2. Start Peer 1:
   `python peer-client.py -hostname peer1 -index_server_name localhost -peer_server_port 7001 -username peer1 -password password -file_directory peer1-files -certificate peer1-server.crt -private_key peer1-server.key`
3. Start Peer 2:
   `python peer-client.py -hostname peer2 -index_server_name localhost -peer_server_port 7002 -username peer2 -password password -file_directory peer2-files -certificate peer2-server.crt -private_key peer2-server.key`
4. Start Peer 3:
   `python peer-client.py -hostname peer3 -index_server_name localhost -peer_server_port 7003 -username peer3 -password password -file_directory peer3-files -certificate peer3-server.crt -private_key peer3-server.key`

Example output from running the peer program:

```
PS C:\Users\ethan\OneDrive - Cal State Fullerton\cs352\FinalProject\peer> python peer-client.py -hostname peer2 -index_server_name localhost -peer_server_port 7002 -username peer2 -password password -file_directory peer2-files -certificate peer2-server.crt -private_key peer2-server.key
Authenticating...
Success
Sending list of files to server...
Success

1. Update index server
2. Search for file
3. Exit and shut down peer server
Enter a choice: 2
Keyword to search for: koala
[{'domain_name': 'peer1', 'port_number': '7001'}]
Files from peer1: ['koalas_rock.txt', 'love_koalas.txt']

File data for file koalas_rock.txt:
Koalas rock!
- Nonces match
- Signature ok
File data for file love_koalas.txt:
I love koalas what about you?
- Nonces match
- Signature ok


1. Update index server
2. Search for file
3. Exit and shut down peer server
Enter a choice: 3
Goodbye
```
