import tkinter as tk
import socket
import json

from crypto.rsa_utils import encrypt, generate_keys
from crypto.crypto_utils import sign

HOST = '127.0.0.1'
PORT = 5001


# 🔐 الحصول على مفتاح السيرفر
def get_server_public_key():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    client.send(json.dumps({"request": "get_public_key"}).encode())
    response = json.loads(client.recv(4096).decode())
    client.close()
    return tuple(response["public_key"])


server_public = get_server_public_key()
client_public, client_private = generate_keys()


# 🧑‍💻 إرسال التصويت
def send_vote():
    voter_id = entry_id.get()
    vote = vote_var.get()

    if not voter_id or not vote:
        status_label.config(text="⚠️ Enter ID and choose candidate", fg="#ff4d4d")
        return

    try:
        encrypted_vote = encrypt(vote, server_public)
        signature = sign(encrypted_vote, client_private)

        packet = {
            "voter_id": voter_id,
            "vote": encrypted_vote,
            "signature": signature,
            "public_key": client_public
        }

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        client.send(json.dumps(packet).encode())

        response = client.recv(1024).decode()
        status_label.config(text=response, fg="#4CAF50")

        client.close()

        entry_id.delete(0, tk.END)
        vote_var.set("")

    except Exception as e:
        status_label.config(text=str(e), fg="red")


# 📊 عرض النتائج داخل الواجهة
def get_results():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))

        client.send(json.dumps({"action": "results"}).encode())
        response = client.recv(4096).decode()
        results = json.loads(response)

        results_box.delete("1.0", tk.END)

        for r in results:
            results_box.insert(tk.END, f"Candidate {r[0]} → {r[1]} votes\n")

        client.close()

    except Exception as e:
        status_label.config(text=str(e), fg="red")


# 🎨 تصميم الواجهة
root = tk.Tk()
root.title("Secure E-Voting")
root.geometry("500x500")
root.configure(bg="#121212")

# ===== Title =====
title = tk.Label(root, text="🗳 Secure E-Voting System",
                 font=("Segoe UI", 18, "bold"),
                 bg="#121212", fg="white")
title.pack(pady=15)

# ===== Card Frame =====
card = tk.Frame(root, bg="#1e1e1e", bd=0, relief="ridge")
card.pack(pady=10, padx=20, fill="x")

# ===== Voter ID =====
tk.Label(card, text="Voter ID",
         bg="#1e1e1e", fg="#bbbbbb").pack(pady=5)

entry_id = tk.Entry(card, font=("Segoe UI", 12),
                    bg="#2a2a2a", fg="white",
                    insertbackground="white",
                    relief="flat")
entry_id.pack(pady=5, ipadx=5, ipady=5)

# ===== Vote Options =====
vote_var = tk.StringVar()

tk.Label(card, text="Select Candidate",
         bg="#1e1e1e", fg="#bbbbbb").pack(pady=10)

options_frame = tk.Frame(card, bg="#1e1e1e")
options_frame.pack()

def create_radio(text, value):
    return tk.Radiobutton(
        options_frame,
        text=text,
        variable=vote_var,
        value=value,
        bg="#1e1e1e",
        fg="white",
        selectcolor="#333",
        activebackground="#1e1e1e"
    )

create_radio("Candidate A", "A").pack(anchor="w")
create_radio("Candidate B", "B").pack(anchor="w")
create_radio("Candidate C", "C").pack(anchor="w")

# ===== Buttons =====
btn_frame = tk.Frame(card, bg="#1e1e1e")
btn_frame.pack(pady=15)

vote_btn = tk.Button(
    btn_frame,
    text="Submit Vote",
    command=send_vote,
    bg="#4CAF50",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    width=15
)
vote_btn.grid(row=0, column=0, padx=5)

results_btn = tk.Button(
    btn_frame,
    text="Show Results",
    command=get_results,
    bg="#2196F3",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    width=15
)
results_btn.grid(row=0, column=1, padx=5)

# ===== Status =====
status_label = tk.Label(root, text="Ready",
                        bg="#121212", fg="#bbbbbb",
                        font=("Segoe UI", 10))
status_label.pack(pady=5)

# ===== Results Box =====
results_box = tk.Text(
    root,
    height=10,
    bg="#1e1e1e",
    fg="white",
    font=("Consolas", 11),
    relief="flat"
)
results_box.pack(padx=20, pady=10, fill="both", expand=True)

root.mainloop()