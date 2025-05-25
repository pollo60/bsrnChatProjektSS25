import socket       # Für die UDP-Kommunikation im lokalen Netzwerk
import threading    # Damit wir mehrere Ports gleichzeitig abhören können (multithreading)
import toml         # Um Konfigurationsdaten aus der Datei config.toml zu lesen

BUFFER_SIZE = 1024  # Max. Größe für empfangene Nachrichten (UDP hat eine Begrenzung)

class DiscoveryService:
    def __init__(self, config_path="config.toml"):
        # Hier speichern wir bekannte Clients: {handle: (ip, port)}
        self.clients = {}

        # Kontrollvariable, um die Listener bei Bedarf zu stoppen
        self.running = True

        # Konfiguration laden (z. B. Handle, Port, whoisport)
        self.config = toml.load(config_path)

        # Port, auf dem Discovery-Broadcasts (JOIN, WHO, LEAVE) empfangen werden
        self.whoisport = self.config['whoisport']

        # Unser eigener Handle (Name des Nutzers)
        self.my_handle = self.config.get("handle", "").strip()

        # Unser persönlicher Kommunikationsport (für direkte Antworten)
        self.my_port = self.config.get("port", 5000)

        # Lock zur Synchronisation – wichtig bei parallelem Zugriff auf self.clients
        self.lock = threading.Lock()

        # Eigene IP-Adresse im Netzwerk ermitteln
        self.local_ip = self.get_local_ip()

    def start(self):
        """
        Startet zwei parallele Threads:
        - einen für den Broadcast-Port (whoisport)
        - einen für den eigenen Kommunikationsport (port)
        """
        threading.Thread(target=self.listen_on_port, args=("WHOIS-Port", self.whoisport), daemon=True).start()
        threading.Thread(target=self.listen_on_port, args=("Eigen-Port", self.my_port), daemon=True).start()

    def listen_on_port(self, port_name, port_value):
        """
        Lauscht auf eingehende Nachrichten auf einem bestimmten Port.
        Wird in einem separaten Thread für jeden Port gestartet.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', port_value))  # Bind an lokale IPs auf dem angegebenen Port
            #print(f"Lausche auf {port_name} (Port {port_value})...") #Das vielleicht nicht printen? Oder gibt das ohne Testzwecke Infos?

            while self.running:
                try:
                    # Warte auf eingehende Nachricht
                    data, addr = sock.recvfrom(BUFFER_SIZE)
                    message = data.decode().strip()
                    # debug nachricht: print(f"DEBUG: Nachricht von {addr[0]}, local_ip={self.local_ip}, message={message}")

                    is_own_join = (
                        message == f"JOIN {self.my_handle} {self.my_port}" and addr[0] == self.local_ip
                    )
                    is_own_custom = (
                        message == f"Netzwerk beigetreten als {self.my_handle} {self.my_port}" and addr[0] == self.local_ip
                    )


                    if not (is_own_join or is_own_custom):
                        print(f"\n📥 Neue Nachricht auf {port_name} von {addr}: {message}")

                    # Nachricht verarbeiten
                    self.handle_message(message, addr, sock)

                except ConnectionResetError:
                    print(f"Verbindung auf {port_name} wurde getrennt.")
                except Exception as e:
                    print(f"Fehler beim Lauschen auf {port_name}: {e}")

    def handle_message(self, message, addr, sock):
        """
        Zentrale Funktion zum Verarbeiten von eingehenden SLCP-Nachrichten.
        Erkennt JOIN, WHO, LEAVE, KNOWUSERS.
        """
        if message.strip() == f"JOIN {self.my_handle} {self.my_port}" or \
           message.strip() == f"Netzwerk beigetreten als {self.my_handle} {self.my_port}":
            return

        parts = message.split()
        if not parts:
                return  # leere Nachricht → ignorieren

        command = parts[0].upper()

        # --- JOIN --- bzw Netzwerk beitreten???
        # Beispiel: JOIN Alice 5000
        if command == "JOIN" and len(parts) == 3: # Nicht abändern, denn dieser Befehl wird benötigt damit SLCP es richtig erkennt
            handle = parts[1]
            port = int(parts[2])

            # In Liste aufnehmen
            with self.lock:
                self.clients[handle] = (addr[0], port)

            # Rückmeldung je nach Absender
            if addr[0] == self.local_ip and handle == self.my_handle:
                print(f"Du ({handle}) bist erfolgreich dem Chat beigetreten!")
            else:
                print(f"{handle} ist jetzt online unter {addr[0]}:{port}")

        # --- WHO ---
        # Beispiel: WHO Alice
        elif command == "WHO":  #Auch hier den Command abändern?
            if len(parts) == 2:
                who_sender_handle = parts[1]
                print(f"WHO-Anfrage empfangen von {who_sender_handle} ({addr[0]})")

                # Sende automatische JOIN-Antwort zurück, damit der WHO-Sender uns sehen kann
                join_message = f"JOIN {self.my_handle} {self.my_port}"
                sock.sendto(join_message.encode(), (addr[0], self.whoisport))
                print(f"JOIN-Antwort an {who_sender_handle} gesendet: {join_message}")
            else:
                print("WHO-Nachricht ohne Handle empfangen – wird ignoriert.")

        # --- LEAVE ---
        # Beispiel: LEAVE Alice
        elif command == "LEAVE" and len(parts) == 2: #Auch hier command leave zu Netwerk verlassen?
            handle = parts[1]
            with self.lock:
                self.clients.pop(handle, None)

            # Rückmeldung je nach Absender
            if addr[0] == self.local_ip and handle == self.my_handle:
                print(f"Du ({handle}) hast den Chat verlassen.")
            else:
                print(f"{handle} hat den Chat verlassen.")

        # --- KNOWUSERS ---
        # Beispiel: KNOWUSERS Alice 192.168.0.5 5000, Bob 192.168.0.7 5001
        elif command == "KNOWUSERS":
            user_entries = message[len("KNOWUSERS "):].split(", ")
            added_list = []

            with self.lock:
                for entry in user_entries:
                    try:
                        handle, ip, port = entry.strip().split()
                        port = int(port)

                        # Nicht sich selbst oder doppelte Nutzer einfügen
                        if handle != self.my_handle and handle not in self.clients:
                            self.clients[handle] = (ip, port)
                            added_list.append((handle, ip, port))
                    except ValueError:
                        continue  # ignorieren, falls fehlerhaft

            if added_list:
                print("Entdeckte Nutzer:")
                for h, ip, port in added_list:
                    print(f"- {h} ({ip}:{port})")
            else:
                print("Keine neuen Nutzer entdeckt (oder bereits bekannt).")


    def send_known_users(self, target_addr, sock):
        """
        Sendet eine KNOWUSERS-Nachricht mit allen bekannten Clients
        an die angegebene Zieladresse.
        """
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
        """
        Beendet die beiden Listener.
        """
        self.running = False
        print("Discovery-Service wurde gestoppt.")

    def get_local_ip(self):
        """
        Ermittelt die lokale IP-Adresse des Rechners,
        indem eine "Fake-Verbindung" zu einer externen IP hergestellt wird.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))  # Verbindung muss nicht tatsächlich erfolgen
                return s.getsockname()[0]
        except:
            return "127.0.0.1"  # Fallback für lokale Tests
