import socket
import json

from crypto.rsa_utils import encrypt, generate_keys
from crypto.crypto_utils import sign

HOST = '127.0.0.1'
PORT = 5001

# 1. Get Server's Public Key
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.send(json.dumps({"request": "get_public_key"}).encode())
server_response = json.loads(client.recv(4096).decode())
server_public = tuple(server_response["public_key"])
client.close()

client_public, client_private = generate_keys()

voter_id = input("Enter your ID: ")
vote = input("Choose (A/B/C): ")

# 2. Encrypt with Server's Public Key
encrypted_vote = encrypt(vote, server_public)
# 3. Sign with Client's Private Key
signature = sign(encrypted_vote, client_private)

packet = {
    "voter_id": voter_id,
    "vote": encrypted_vote,
    "signature": signature,
    "public_key": client_public
}

data = json.dumps(packet)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

client.send(data.encode())

response = client.recv(1024).decode()
print("Server:", response)

client.close()