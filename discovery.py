import socket
import threading
import toml
import os

# === Konfiguration laden ===

def load_config():
    config_path = "config.toml"
    if not os.path.exists(config_path):
        raise FileNotFoundError("Konfigurationsdatei config.toml fehlt.")
    with open(config_path, "r") as f:
        return toml.load(f)

config = load_config()
WHOIS_PORT = config["network"]["whoisport"]
ENCODING = "utf-8"
BUFFER_SIZE = 1024
DISCOVERED_USERS = {}  # handle -> (ip, port)

# === UDP-Socket vorbereiten ===

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(("", WHOIS_PORT))  # Auf alle Interfaces lauschen

# === Hilfsfunktionen ===

def handle_join(addr, parts):
    """JOIN <Handle> <Port>"""
    if len(parts) != 3:
        return
    handle = parts[1]
    port = int(parts[2])
    DISCOVERED_USERS[handle] = (addr[0], port)
    print(f"[JOIN] {handle} @ {addr[0]}:{port}")

def handle_leave(parts):
    """LEAVE <Handle>"""
    if len(parts) != 2:
        return
    handle = parts[1]
    if handle in DISCOVERED_USERS:
        del DISCOVERED_USERS[handle]
        print(f"[LEAVE] {handle} entfernt")

def handle_who(addr):
    """Antwort auf WHO mit KNOWNUSERS"""
    if not DISCOVERED_USERS:
        return
    response_parts = []
    for handle, (ip, port) in DISCOVERED_USERS.items():
        response_parts.append(f"{handle} {ip} {port}")
    response = "KNOWNUSERS " + ", ".join(response_parts) + "\n"
    sock.sendto(response.encode(ENCODING), addr)
    print(f"[WHO] Antwort gesendet an {addr}: {response.strip()}")

# === Haupt-Listener-Loop ===

def discovery_listener():
    print(f"Discovery-Dienst läuft auf Port {WHOIS_PORT}")
    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            message = data.decode(ENCODING).strip()
            print(f"[Empfangen] {message} von {addr}")

            if message.startswith("JOIN"):
                handle_join(addr, message.split())
            elif message.startswith("LEAVE"):
                handle_leave(message.split())
            elif message == "WHO":
                handle_who(addr)

        except Exception as e:
            print(f"[Fehler] {e}")

# === Startpunkt ===

if __name__ == "__main__":
    listener_thread = threading.Thread(target=discovery_listener, daemon=True)
    listener_thread.start()
    listener_thread.join()
