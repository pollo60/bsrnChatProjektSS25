# discovery_daemon_queue.py
import socket
import toml
import time
import json
import os

BUFFER_SIZE = 1024
COMM_FILE = "discovery_output.json"

def run_discovery(config_path, output_queue):
    with open(config_path, 'r', encoding="utf-8") as f:
        config = toml.load(f)

    login = config['login_daten']
    whoisport = int(login['whoisport'])
    my_handle = login['name']
    my_port = int(login['port'])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", whoisport))

    print(f"[DISCOVERY] Lausche auf Port {whoisport}...")

    clients = {}

    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            msg = data.decode().strip()
            print(f"[DISCOVERY] Von {addr}: {msg}")
            parts = msg.split()
            if not parts:
                continue

            cmd = parts[0].upper()
            if cmd == "JOIN" and len(parts) == 3:
                h, p = parts[1], int(parts[2])
                clients[h] = (addr[0], p)
                save_clients(clients)
                output_queue.put(f"{h} ist beigetreten ({addr[0]}:{p})")

            elif cmd == "LEAVE" and len(parts) == 2:
                h = parts[1]
                clients.pop(h, None)
                save_clients(clients)
                output_queue.put(f"{h} hat das Netzwerk verlassen.")

            elif cmd == "WHO":
                response = f"JOIN {my_handle} {my_port}"
                sock.sendto(response.encode(), addr)

        except Exception as e:
            output_queue.put(f"[DISCOVERY] Fehler: {e}")

def save_clients(clients):
    try:
        with open(COMM_FILE, 'w') as f:
            json.dump(clients, f)
    except Exception as e:
        print("[DISCOVERY] Fehler beim Speichern:", e)
