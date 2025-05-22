import socket
import threading
import toml

BUFFER_SIZE = 1024

class DiscoveryService:
    def __init__(self, config_path="config.toml"):
        self.clients = {}  # {handle: (ip, port)}
        self.running = True
        self.config = toml.load(config_path)
        self.whoisport = self.config['whoisport']
        self.my_handle = self.config.get("handle", "").strip()
        self.my_port = self.config.get("port", 5000)
        self.lock = threading.Lock()
        self.local_ip = self.get_local_ip()

    def start(self):
        thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        thread.start()

    def listen_for_messages(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', self.whoisport))
            print(f"Discovery-Service läuft. Warte auf Nachrichten auf Port {self.whoisport}...")

            while self.running:
                try:
                    data, addr = sock.recvfrom(BUFFER_SIZE)
                    message = data.decode().strip()
                    print(f"\nNeue Nachricht von {addr}: {message}")
                    self.handle_message(message, addr, sock)

                except ConnectionResetError:
                    print("Verbindung wurde vom Empfänger unerwartet getrennt (ignoriert).")
                except Exception as e:
                    print(f"Fehler beim Empfangen: {e}")

    def handle_message(self, message, addr, sock):
        parts = message.split()
        if not parts:
            return

        command = parts[0].upper()

        if command == "JOIN" and len(parts) == 3:
            handle = parts[1]
            port = int(parts[2])
            with self.lock:
                self.clients[handle] = (addr[0], port)

            if addr[0] == self.local_ip and handle == self.my_handle:
                print(f"✅ Du ({handle}) hast erfolgreich dem Chat beigetreten.")
            else:
                print(f"✅ {handle} ist jetzt online unter {addr[0]}:{port}")

        elif command == "WHO":
            # WHO muss ab jetzt WHO <Name> heißen
            if len(parts) == 2:
                who_sender_handle = parts[1]
                print(f"📡 WHO-Anfrage empfangen von {who_sender_handle} ({addr[0]})")

                # Sende automatische JOIN-Antwort zurück
                join_message = f"JOIN {self.my_handle} {self.my_port}"
                sock.sendto(join_message.encode(), (addr[0], self.whoisport))
                print(f"↩️ JOIN-Antwort an {who_sender_handle} gesendet: {join_message}")
            else:
                print("⚠️ WHO-Nachricht ohne Handle empfangen – wird ignoriert.")

        elif command == "LEAVE" and len(parts) == 2:
            handle = parts[1]
            with self.lock:
                self.clients.pop(handle, None)

            if addr[0] == self.local_ip and handle == self.my_handle:
                print(f"👋 Du ({handle}) hast den Chat verlassen.")
            else:
                print(f"👋 {handle} hat den Chat verlassen.")

        elif command == "KNOWUSERS":
            user_entries = message[len("KNOWUSERS "):].split(", ")
            added = 0
            added_list = []

            with self.lock:
                for entry in user_entries:
                    try:
                        handle, ip, port = entry.strip().split()
                        port = int(port)
                        if handle != self.my_handle and handle not in self.clients:
                            self.clients[handle] = (ip, port)
                            added_list.append((handle, ip, port))
                            added += 1
                    except ValueError:
                        continue

            if added_list:
                print("📃 Entdeckte Nutzer:")
                for h, ip, port in added_list:
                    print(f"- {h} ({ip}:{port})")
            else:
                print("📃 Keine neuen Nutzer entdeckt (oder bereits bekannt).")

        else:
            print(f"❌ Unbekannter Befehl oder ungültige Syntax: {message}")

    def send_known_users(self, target_addr, sock):
        with self.lock:
            if not self.clients:
                userlist = "Niemand online"
            else:
                userlist = ", ".join([
                    f"{handle} {ip} {port}"
                    for handle, (ip, port) in self.clients.items()
                ])

        response = f"KNOWUSERS {userlist}\n"
        sock.sendto(response.encode(), target_addr)
        print(f"Gesendet an {target_addr}: {response.strip()}")

    def stop(self):
        self.running = False
        print("Discovery-Service wurde gestoppt.")

    def get_local_ip(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
