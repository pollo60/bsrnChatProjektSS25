# discovery_daemon.py
import socket
import toml
import threading
import json
import time
import os

BUFFER_SIZE = 1024
COMM_FILE = "discovery_output.json"

def run_discovery(config_path):
    with open(config_path, 'r', encoding="utf-8") as f:
        config = toml.load(f)

    login = config['login_daten']
    whoisport = int(login['whoisport'])
    my_handle = login['name']
    my_port = int(login['port'])

    clients = {}
    lock = threading.Lock()

    def listen():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", whoisport))
        print(f"[DISCOVERY] Lausche auf Port {whoisport}")

        while True:
            try:
                data, addr = sock.recvfrom(BUFFER_SIZE)
                msg = data.decode().strip()
                parts = msg.split()
                if not parts:
                    continue
                cmd = parts[0].upper()
                if cmd == "JOIN" and len(parts) == 3:
                    h, p = parts[1], int(parts[2])
                    with lock:
                        clients[h] = (addr[0], p)
                        save_clients(clients)
                elif cmd == "LEAVE" and len(parts) == 2:
                    h = parts[1]
                    with lock:
                        clients.pop(h, None)
                        save_clients(clients)
                elif cmd == "WHO":
                    response = f"JOIN {my_handle} {my_port}"
                    sock.sendto(response.encode(), addr)
            except Exception as e:
                print("[DISCOVERY] Fehler:", e)

    def save_clients(clients):
        try:
            with open(COMM_FILE, 'w') as f:
                json.dump(clients, f)
        except Exception as e:
            print("[DISCOVERY] Fehler beim Schreiben der Datei:", e)

    thread = threading.Thread(target=listen, daemon=True)
    thread.start()

    while True:
        time.sleep(1)