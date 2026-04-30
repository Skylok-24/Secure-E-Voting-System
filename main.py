import time
import subprocess
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

server_process = None


def start_server():
    global server_process

    env = os.environ.copy()
    env['PYTHONPATH'] = PROJECT_ROOT

    server_process = subprocess.Popen(
        [sys.executable, "-m", "server.voting_server"],
        cwd=PROJECT_ROOT,
        env=env
    )


def run_client():
    env = os.environ.copy()
    env['PYTHONPATH'] = PROJECT_ROOT

    subprocess.run(
        [sys.executable, "-m", "client.gui_client"],
        cwd=PROJECT_ROOT,
        env=env
    )


if __name__ == "__main__":
    sys.path.insert(0, PROJECT_ROOT)

    start_server()

    time.sleep(1)

    try:
        run_client()

    finally:
        if server_process:
            server_process.terminate()
            server_process.wait()