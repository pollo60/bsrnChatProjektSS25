
import socket
import threading
import toml
import ipaddress
import sys
import json

BUFFER_SIZE = 1024
COMM_FILE = "discovery_output.json"

class DiscoveryService:
    def __init__(self, config_path):
        self.clients = {}
        self.running = True
        self.config = toml.load(config_path)
        data = self.config.get("login_daten", self.config)
        self.whoisport = int(data.get("whoisport", 1111))
        self.my_handle = data.get("name", "Unbekannt")
        self.my_port = int(data.get("port", 5000))
        self.lock = threading.Lock()
        self.local_ip, self.broadcast_ip = self.get_local_ip_and_broadcast()

    def start(self):
        threading.Thread(target=self.listen_on_port, args=("WHOIS-Port", self.whoisport), daemon=True).start()
        threading.Thread(target=self.listen_on_port, args=("Eigen-Port", self.my_port), daemon=True).start()

    def listen_on_port(self, port_name, port_value):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(('', int(port_value)))
            except OSError as e:
                print(f"[FEHLER] Port {port_value} konnte nicht gebunden werden: {e}")
                return

            while self.running:
                try:
                    data, addr = sock.recvfrom(BUFFER_SIZE)
                    message = data.decode().strip()
                    is_own_msg = addr[0] == self.local_ip and any(
                        message == expected for expected in [
                            f"JOIN {self.my_handle} {self.my_port}",
                            f"Netzwerk beigetreten als {self.my_handle} {self.my_port}"
                        ]
                    )
                    if not is_own_msg:
                        print(f"[Discovery] Nachricht auf {port_name} von {addr}: {message}")
                    self.handle_message(message, addr, sock)
                except Exception as e:
                    print(f"[FEHLER] Fehler beim Lauschen auf {port_name}: {e}")

    def handle_message(self, message, addr, sock):
        parts = message.split()
        if not parts:
            return
        command = parts[0].upper()
        if command == "JOIN" and len(parts) == 3:
            handle, port = parts[1], int(parts[2])
            with self.lock:
                self.clients[handle] = (addr[0], port)
            self.save_clients()
        elif command == "LEAVE" and len(parts) == 2:
            handle = parts[1]
            with self.lock:
                self.clients.pop(handle, None)
            self.save_clients()

    def save_clients(self):
        try:
            with open(COMM_FILE, "w") as f:
                json.dump(self.clients, f)
        except Exception as e:
            print(f"[FEHLER] Konnte Clients nicht speichern: {e}")

    def get_local_ip_and_broadcast(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
            net = ipaddress.ip_network(ip + '/24', strict=False)
            return ip, str(net.broadcast_address)
        except:
            return "127.0.0.1", "255.255.255.255"

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.toml"
    discovery = DiscoveryService(config_path)
    discovery.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        discovery.running = False
