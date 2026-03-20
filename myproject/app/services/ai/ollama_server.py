import subprocess
import socket
import time
import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "127.0.0.1")
OLLAMA_PORT = int(os.getenv("OLLAMA_PORT", "11434"))

_ollama_process = None


def is_port_open(host=OLLAMA_HOST, port=OLLAMA_PORT):
    """Check if Ollama server is already running."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            return True
        except ConnectionRefusedError:
            return False


def ensure_ollama_running():
    """
    Start Ollama server if it is not already running.
    Safe to call multiple times.
    """
    global _ollama_process

    if is_port_open():
        return

    print("Starting Ollama server...")

    _ollama_process = subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Wait until server becomes available
    for _ in range(15):
        if is_port_open():
            print("Ollama server ready")
            return
        time.sleep(1)

    raise RuntimeError("Failed to start Ollama server.")