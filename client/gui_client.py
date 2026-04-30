import tkinter as tk
from tkinter import ttk
import socket
import json

from crypto.rsa_utils import encrypt, generate_keys
from crypto.crypto_utils import sign

HOST = '127.0.0.1'
PORT = 5001

# ── Palette ──────────────────────────────────────────────
BG          = "#0A0E17"        # near-black navy
SURFACE     = "#111827"        # dark card
SURFACE2    = "#1C2333"        # slightly lighter card
BORDER      = "#2A3448"        # subtle border
ACCENT      = "#3B82F6"        # vivid blue
ACCENT_DIM  = "#1E3A5F"        # muted blue for hover
SUCCESS     = "#10B981"        # emerald green
DANGER      = "#EF4444"        # red
TEXT_HI     = "#F1F5F9"        # near-white
TEXT_MID    = "#94A3B8"        # muted
TEXT_LOW    = "#475569"        # very muted

FONT_TITLE  = ("Georgia", 20, "bold")
FONT_LABEL  = ("Courier New", 9)
FONT_ENTRY  = ("Courier New", 12)
FONT_BTN    = ("Courier New", 10, "bold")
FONT_MONO   = ("Courier New", 11)


# ── Helpers ──────────────────────────────────────────────
def get_server_public_key():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    client.send(json.dumps({"request": "get_public_key"}).encode())
    response = json.loads(client.recv(4096).decode())
    client.close()
    return tuple(response["public_key"])


server_public  = get_server_public_key()
client_public, client_private = generate_keys()


# ── Vote sender ───────────────────────────────────────────
def send_vote():
    voter_id = entry_id.get()
    vote     = vote_var.get()

    if not voter_id or not vote:
        set_status("⚠  Enter voter ID and select a candidate.", DANGER)
        return

    try:
        encrypted_vote = encrypt(vote, server_public)
        signature      = sign(encrypted_vote, client_private)

        packet = {
            "voter_id":   voter_id,
            "vote":       encrypted_vote,
            "signature":  signature,
            "public_key": client_public
        }

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        client.send(json.dumps(packet).encode())

        response = client.recv(1024).decode()
        set_status(response, SUCCESS)

        client.close()
        entry_id.delete(0, tk.END)
        vote_var.set("")

    except Exception as e:
        set_status(str(e), DANGER)


# ── Results fetcher ───────────────────────────────────────
def get_results():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))

        client.send(json.dumps({"action": "results"}).encode())
        response = client.recv(4096).decode()
        results  = json.loads(response)

        results_box.config(state="normal")
        results_box.delete("1.0", tk.END)

        for r in results:
            results_box.insert(tk.END, f"  Candidate {r[0]}   →   {r[1]} votes\n")

        results_box.config(state="disabled")
        client.close()

    except Exception as e:
        set_status(str(e), DANGER)


def set_status(msg, color=TEXT_MID):
    status_label.config(text=msg, fg=color)


# ── Root window ───────────────────────────────────────────
root = tk.Tk()
root.title("Secure E-Voting")
root.geometry("1200x720")
root.resizable(False, False)
root.configure(bg=BG)

# Thin decorative top-bar
topbar = tk.Frame(root, bg=ACCENT, height=3)
topbar.pack(fill="x", side="top")


# ── Header ────────────────────────────────────────────────
header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=30, pady=(22, 0))

tk.Label(
    header,
    text="SECURE E-VOTING",
    font=FONT_TITLE,
    bg=BG, fg=TEXT_HI,
).pack(side="left")

tk.Label(
    header,
    text="🔒",
    font=("Segoe UI Emoji", 18),
    bg=BG, fg=ACCENT,
).pack(side="right", pady=2)

tk.Frame(root, bg=BORDER, height=1).pack(fill="x", padx=30, pady=(10, 0))


# ── Main card ─────────────────────────────────────────────
card = tk.Frame(root, bg=SURFACE, bd=0, highlightthickness=1,
                highlightbackground=BORDER)
card.pack(padx=30, pady=16, fill="x")

inner = tk.Frame(card, bg=SURFACE)
inner.pack(padx=20, pady=18, fill="x")

# --- Voter ID ---
tk.Label(inner, text="VOTER ID", font=FONT_LABEL,
         bg=SURFACE, fg=TEXT_LOW, anchor="w").pack(fill="x", pady=(0, 4))

entry_frame = tk.Frame(inner, bg=BORDER, bd=0,
                       highlightthickness=1, highlightbackground=BORDER)
entry_frame.pack(fill="x")

entry_id = tk.Entry(
    entry_frame,
    font=FONT_ENTRY,
    bg=SURFACE2,
    fg=TEXT_HI,
    insertbackground=ACCENT,
    relief="flat",
    bd=0,
)
entry_id.pack(fill="x", ipady=8, ipadx=10)

# ─ bind focus glow
def on_focus_in(e):
    entry_frame.config(highlightbackground=ACCENT)
def on_focus_out(e):
    entry_frame.config(highlightbackground=BORDER)
entry_id.bind("<FocusIn>",  on_focus_in)
entry_id.bind("<FocusOut>", on_focus_out)

tk.Frame(inner, bg=BG, height=1).pack(fill="x", pady=(14, 6))


# --- Candidates ---
tk.Label(inner, text="SELECT CANDIDATE", font=FONT_LABEL,
         bg=SURFACE, fg=TEXT_LOW, anchor="w").pack(fill="x", pady=(4, 8))

vote_var = tk.StringVar()

CANDIDATES = [
    ("A", "Candidate A"),
    ("B", "Candidate B"),
    ("C", "Candidate C"),
]

radio_frames = []

def make_radio_card(parent, label, value):
    """Styled radio-button card."""
    frame = tk.Frame(parent, bg=SURFACE2, cursor="hand2",
                     highlightthickness=1, highlightbackground=BORDER)
    frame.pack(fill="x", pady=3)

    rb = tk.Radiobutton(
        frame,
        text=f"  {label}",
        variable=vote_var,
        value=value,
        font=FONT_MONO,
        bg=SURFACE2,
        fg=TEXT_MID,
        selectcolor=SURFACE2,
        activebackground=SURFACE2,
        activeforeground=TEXT_HI,
        relief="flat",
        bd=0,
        indicatoron=True,
        anchor="w",
    )
    rb.pack(fill="x", ipady=7, ipadx=10)

    def on_select():
        # Reset all cards
        for f, r in radio_frames:
            f.config(highlightbackground=BORDER)
            r.config(fg=TEXT_MID)
        # Highlight selected
        frame.config(highlightbackground=ACCENT)
        rb.config(fg=TEXT_HI)

    rb.config(command=on_select)
    frame.bind("<Button-1>", lambda e: (vote_var.set(value), on_select()))
    radio_frames.append((frame, rb))


for val, lbl in CANDIDATES:
    make_radio_card(inner, lbl, val)


# ── Buttons ───────────────────────────────────────────────
btn_row = tk.Frame(root, bg=BG)
btn_row.pack(padx=30, pady=4, fill="x")

def make_button(parent, text, command, bg, fg=TEXT_HI, col=0):
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        font=FONT_BTN,
        relief="flat",
        bd=0,
        cursor="hand2",
        activebackground=ACCENT_DIM,
        activeforeground=TEXT_HI,
        padx=18, pady=10,
    )
    btn.grid(row=0, column=col, padx=(0, 8) if col == 0 else (8, 0), sticky="ew")

    # Hover tints
    orig_bg = bg
    btn.bind("<Enter>", lambda e: btn.config(bg=ACCENT_DIM))
    btn.bind("<Leave>", lambda e: btn.config(bg=orig_bg))
    return btn

btn_row.columnconfigure(0, weight=1)
btn_row.columnconfigure(1, weight=1)

make_button(btn_row, "▶  SUBMIT VOTE",   send_vote,   ACCENT,   col=0)
make_button(btn_row, "◉  SHOW RESULTS",  get_results, SURFACE2, col=1)


# ── Status bar ────────────────────────────────────────────
status_label = tk.Label(
    root,
    text="Ready",
    font=FONT_LABEL,
    bg=BG,
    fg=TEXT_LOW,
    anchor="w",
)
status_label.pack(padx=30, pady=(6, 2), fill="x")


# ── Results panel ─────────────────────────────────────────
res_frame = tk.Frame(root, bg=SURFACE, highlightthickness=1,
                     highlightbackground=BORDER)
res_frame.pack(padx=30, pady=(4, 20), fill="both", expand=True)

tk.Label(res_frame, text=" RESULTS", font=FONT_LABEL,
         bg=SURFACE, fg=TEXT_LOW, anchor="w").pack(fill="x", padx=10, pady=(8, 2))

tk.Frame(res_frame, bg=BORDER, height=1).pack(fill="x", padx=10)

results_box = tk.Text(
    res_frame,
    font=FONT_MONO,
    bg=SURFACE,
    fg=TEXT_HI,
    relief="flat",
    bd=0,
    state="disabled",
    selectbackground=ACCENT_DIM,
    cursor="arrow",
    spacing1=4,
    spacing3=4,
)
results_box.pack(padx=10, pady=8, fill="both", expand=True)

# Scrollbar
sb = tk.Scrollbar(res_frame, command=results_box.yview,
                  bg=SURFACE, troughcolor=SURFACE, bd=0, width=6)
results_box.config(yscrollcommand=sb.set)
sb.pack(side="right", fill="y")


root.mainloop()