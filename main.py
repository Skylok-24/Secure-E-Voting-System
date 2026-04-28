import threading
import time
import subprocess


def run_server():
    subprocess.run(["python", "server/voting_server.py"])


def run_client():
    time.sleep(1)
    subprocess.run(["python", "client/gui_client.py"])


if __name__ == "__main__":

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()


    run_client()