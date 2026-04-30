import socket
import json

from crypto.rsa_utils import generate_keys, decrypt
from crypto.crypto_utils import verify
from .database import init_db, has_voted, save_vote, get_results

HOST = '127.0.0.1'
PORT = 5001

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()

print("Server is running...")

# 🔐 مفاتيح السيرفر
server_public, server_private = generate_keys()

# 🗄️ قاعدة البيانات
init_db()

while True:
    client, addr = server.accept()
    print(f"Connected from {addr}")

    data = client.recv(4096).decode()
    if not data:
        client.close()
        continue

    packet = json.loads(data)

    # 🔥 1. إرسال المفتاح العام
    if packet.get("request") == "get_public_key":
        client.send(json.dumps({"public_key": server_public}).encode())
        client.close()
        continue

    # 🔥 2. عرض النتائج
    if packet.get("action") == "results":
        results = get_results()
        client.send(json.dumps(results).encode())
        client.close()
        continue

    # 🔥 3. التصويت
    try:
        voter_id = packet["voter_id"]
        voter_id = "".join(voter_id.lower().split())
        encrypted_vote = packet["vote"]
        signature = packet["signature"]
        client_public = tuple(packet["public_key"])

        # ❌ منع التكرار
        if has_voted(voter_id):
            client.send("Already voted!".encode())
            client.close()
            continue

        # 🔐 التحقق من التوقيع
        if not verify(encrypted_vote, signature, client_public):
            client.send("Invalid signature!".encode())
            client.close()
            continue

        # 🔓 فك التشفير
        vote = decrypt(encrypted_vote, server_private)

        # 💾 حفظ
        save_vote(voter_id, vote)

        client.send("Vote accepted!".encode())

    except Exception as e:
        client.send(f"Error: {str(e)}".encode())

    client.close()