import socket       # UDP-Kommunikation im lokalen Netzwerk
import threading    # Parallele Threads zum Lauschen auf Ports
import toml          # Konfiguration im TOML-Format einlesen
import ipaddress     # Broadcast-Adresse basierend auf IP berechnen

BUFFER_SIZE = 1024  # Maximale Größe für empfangene UDP-Nachrichten

class DiscoveryService:
    def __init__(self, config_path="config.toml"):
        self.clients = {}       # Bekannte Clients {handle: (ip, port)}
        self.running = True     # Wird genutzt, um das Lauschen zu stoppen
        self.config = toml.load(config_path)

        # Konfigurationswerte lesen
        self.whoisport = self.config.get("login_daten", {}).get("whoisport")
        self.my_handle = self.config.get("handle", "").strip()
        self.my_port = self.config.get("port", 5000)

        self.lock = threading.Lock()
        self.local_ip, self.broadcast_ip = self.get_local_ip_and_broadcast()

    def start(self):
        """Startet parallele Threads zum Lauschen auf WHOIS- und eigenen Port."""
        threading.Thread(target=self.listen_on_port, args=("WHOIS-Port", self.whoisport), daemon=True).start()
        threading.Thread(target=self.listen_on_port, args=("Eigen-Port", self.my_port), daemon=True).start()

    def listen_on_port(self, port_name, port_value):
        """Lauscht auf UDP-Nachrichten auf einem bestimmten Port."""
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
                        print(f"\n📥 Neue Nachricht auf {port_name} von {addr}: {message}")

                    self.handle_message(message, addr, sock)
                except Exception as e:
                    print(f"[FEHLER] Fehler beim Lauschen auf {port_name}: {e}")

    def handle_message(self, message, addr, sock):
        """Verarbeitet eingehende Nachrichten (JOIN, WHO, LEAVE, KNOWUSERS)."""
        parts = message.split()
        if not parts:
            return

        command = parts[0].upper()

        if command == "JOIN" and len(parts) == 3:
            handle, port = parts[1], int(parts[2])
            with self.lock:
                self.clients[handle] = (addr[0], port)
            if addr[0] == self.local_ip and handle == self.my_handle:
                print(f"Du ({handle}) bist erfolgreich dem Chat beigetreten!")
            else:
                print(f"{handle} ist jetzt online unter {addr[0]}:{port}")

        elif command == "WHO" and len(parts) == 2:
            sender_handle = parts[1]
            print(f"WHO-Anfrage empfangen von {sender_handle} ({addr[0]})")
            response = f"JOIN {self.my_handle} {self.my_port}"
            sock.sendto(response.encode(), (addr[0], self.whoisport))
            print(f"JOIN-Antwort gesendet an {sender_handle}: {response}")

        elif command == "LEAVE" and len(parts) == 2:
            handle = parts[1]
            with self.lock:
                self.clients.pop(handle, None)
            if addr[0] == self.local_ip and handle == self.my_handle:
                print(f"Du ({handle}) hast den Chat verlassen.")
            else:
                print(f"{handle} hat den Chat verlassen.")

        elif command == "KNOWUSERS":
            user_entries = message[len("KNOWUSERS "):].split(", ")
            newly_added = []
            with self.lock:
                for entry in user_entries:
                    try:
                        handle, ip, port = entry.strip().split()
                        port = int(port)
                        if handle != self.my_handle and handle not in self.clients:
                            self.clients[handle] = (ip, port)
                            newly_added.append((handle, ip, port))
                    except ValueError:
                        continue
            if newly_added:
                print("Entdeckte Nutzer:")
                for h, ip, port in newly_added:
                    print(f"- {h} ({ip}:{port})")
            else:
                print("Keine neuen Nutzer entdeckt oder alle bereits bekannt.")

    def send_known_users(self, target_addr, sock):
        """Sendet eine Liste aller bekannten Nutzer als KNOWUSERS-Nachricht."""
        with self.lock:
            userlist = ", ".join([f"{h} {ip} {p}" for h, (ip, p) in self.clients.items()]) or "Niemand online"
        response = f"KNOWUSERS {userlist}\n"
        sock.sendto(response.encode(), target_addr)
        print(f"Gesendet an {target_addr}: {response.strip()}")

    def stop(self):
        """Stoppt die Listener."""
        self.running = False
        print("Discovery-Service wurde gestoppt.")

    def get_local_ip_and_broadcast(self):
        """Ermittelt lokale IP und zugehörige Broadcast-Adresse."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
            net = ipaddress.ip_network(ip + '/24', strict=False)
            return ip, str(net.broadcast_address)
        except:
            return "127.0.0.1", "255.255.255.255"
