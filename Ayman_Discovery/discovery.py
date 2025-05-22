import socket       # Für die Netzwerk-Kommunikation via UDP
import threading    # Für paralleles Lauschen ohne das Hauptprogramm zu blockieren
import toml         # Um die Konfigurationsdatei im TOML-Format zu laden

# Allgemeine Einstellungen
DISCOVERY_PORT = 4000         # Default-Port, falls nicht in config.toml überschrieben
BUFFER_SIZE = 1024            # Maximale Größe einer eingehenden Nachricht

class DiscoveryService:
    """
    Der DiscoveryService lauscht im lokalen Netzwerk auf bestimmte Chat-Befehle (JOIN, WHO, LEAVE)
    und verwaltet eine Liste aktiver Nutzer.
    """

    def __init__(self, config_path="config.toml"):
        # Speichert alle aktuell bekannten Nutzer
        self.clients = {}  # Format: {handle: (IP-Adresse, Port)}

        # Kontrollvariable zum Beenden der Hauptschleife
        self.running = True

        # Konfiguration aus Datei laden
        self.config = toml.load(config_path)
        self.whoisport = self.config['whoisport']

        # Verhindert gleichzeitigen Zugriff auf self.clients durch mehrere Threads
        self.lock = threading.Lock()

        # Eigene lokale IP-Adresse ermitteln
        self.local_ip = self.get_local_ip()

    def start(self):
        """
        Startet den Discovery-Dienst in einem separaten Thread.
        """
        thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        thread.start()

    def listen_for_messages(self):
        """
        Wartet dauerhaft auf eingehende UDP-Nachrichten vom Netzwerk (JOIN, WHO, LEAVE).
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', self.whoisport))

            print(f"Discovery-Service läuft. Warte auf Nachrichten auf Port {self.whoisport}...")

            while self.running:
                try:
                    # Empfang einer Nachricht
                    data, addr = sock.recvfrom(BUFFER_SIZE)
                    message = data.decode().strip()
                    print(f"\nNeue Nachricht von {addr}: {message}")
                    self.handle_message(message, addr, sock)
                
                except ConnectionResetError:
                    # Fehlermeldung speziell für die WinError10054: Socket wurde auf EMpfängerseite unerwartet geschlossen
                    print("Verbindung wurde vom Empfänger unerwartet getrennt (ignoriert).")

                except Exception as e:
                    # Anderweitige Fehler
                    print(f"Fehler beim Empfangen: {e}")

    def handle_message(self, message, addr, sock):
        """
        Verarbeitet empfangene Nachrichten: JOIN, WHO oder LEAVE.
        """
        parts = message.split()
        if not parts:
            return  # leere oder fehlerhafte Nachricht ignorieren

        command = parts[0].upper()

        # Nutzer meldet sich im Netzwerk an
        if command == "JOIN" and len(parts) == 3:
            handle = parts[1]
            port = int(parts[2])
            with self.lock:
                self.clients[handle] = (addr[0], port)
            
            if addr[0] == self.local_ip:
                print(f"Du ({handle}) hast erfolgreich dem Chat beigetreten.")
            else:
                print(f"{handle} ist jetzt online unter {addr[0]}:{port}")

        # 📡 Nutzer fragt nach bekannten Teilnehmern im Netzwerk
        elif command == "WHO":
            self.send_known_users(addr, sock)

        #  Nutzer verlässt das Netzwerk
        elif command == "LEAVE" and len(parts) == 2:
            handle = parts[1]
            with self.lock:
                self.clients.pop(handle, None)
            
            if addr[0] == self.local_ip:
                print(f"Du ({handle}) hast den Chat verlassen.")
            else:
                print(f"{handle} hat den Chat verlassen.")

        # Unbekannter Befehl Fehlermeldung
        else:
            print(f"Unbekannter Befehl oder ungültige Syntax: {message}")

    def send_known_users(self, target_addr, sock):
        """
        Antwortet mit einer Liste aller aktuell bekannten Nutzer (KNOWUSERS).
        """
        with self.lock:
            if not self.clients:
                userlist = "Niemand online"
            else:
                userlist = ", ".join([
                    f"{handle} ({ip}:{port})"
                    for handle, (ip, port) in self.clients.items()
                ])

        response = f"KNOWUSERS {userlist}\n"
        sock.sendto(response.encode(), target_addr)

        print(f"Gesendet an {target_addr}: {response.strip()}")

    def stop(self):
        """
        Beendet den Discovery-Dienst.
        """
        self.running = False
        print("Discovery-Service wurde gestoppt.")

    def get_local_ip(self):
        """
        Ermittelt die lokale IP-Adresse des aktuellen Rechners.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
