import socket       # Für Netzwerkkommunikation (UDP-Sockets)
import threading    # Für paralleles Lauschen ohne die Hauptlogik zu blockieren
import toml         # Zum Einlesen der Konfigurationsdatei (config.toml)

# Konstanten zur Netzwerkkonfiguration
DISCOVERY_PORT = 4000         # Standardport für Broadcasts (wird in der config.toml überschrieben)
BUFFER_SIZE = 1024            # Maximale Größe der empfangenen UDP-Nachricht

class DiscoveryService:
    """
    Der DiscoveryService lauscht im lokalen Netzwerk auf SLCP-Nachrichten (JOIN, LEAVE, WHO)
    und verwaltet eine Liste aktiver Clients.
    """

    def __init__(self, config_path="config.toml"):
        # Dictionary zur Speicherung der bekannten Clients:
        # Format: {handle: (ip, port)}
        self.clients = {}

        # Steuert, ob der Dienst weiterlaufen soll
        self.running = True

        # Konfigurationswerte aus der TOML-Datei laden
        self.config = toml.load(config_path)

        # Der Port, auf dem der Dienst UDP-Broadcasts empfängt
        self.whoisport = self.config['whoisport']

        # Lock für Thread-Sicherheit (verhindert gleichzeitige Zugriffe auf self.clients)
        self.lock = threading.Lock()

    def start(self):
        """
        Startet den Discovery-Dienst in einem Hintergrund-Thread.
        Dieser lauscht auf Broadcast-Nachrichten im Netzwerk.
        """
        thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        thread.start()

    def listen_for_messages(self):
        """
        Diese Funktion lauscht dauerhaft auf eingehende Nachrichten per UDP.
        Erwartet werden JOIN, LEAVE und WHO Nachrichten.
        """
        # UDP-Socket erstellen
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # Erlaubt das mehrfache Binden auf denselben Port (für parallele Prozesse)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Binde Socket an alle verfügbaren Schnittstellen (0.0.0.0) und den konfigurierten Port
            sock.bind(('', self.whoisport))

            print(f"[Discovery] Listening on UDP port {self.whoisport} for broadcast messages...")

            # Endlosschleife – Dienst bleibt aktiv solange self.running == True
            while self.running:
                try:
                    # Warte auf eingehende UDP-Nachricht
                    data, addr = sock.recvfrom(BUFFER_SIZE)

                    # Dekodiere empfangene Bytes in einen String
                    message = data.decode().strip()

                    print(f"[Discovery] Received: {message} from {addr}")

                    # Verarbeite die Nachricht weiter
                    self.handle_message(message, addr, sock)
                except Exception as e:
                    # Fehler beim Empfang werden ausgegeben
                    print(f"[Discovery] Error: {e}")

    def handle_message(self, message, addr, sock):
        """
        Diese Methode analysiert die Nachricht und führt entsprechende Aktionen aus:
        - JOIN: Nutzer wird zur Liste hinzugefügt
        - LEAVE: Nutzer wird entfernt
        - WHO: Liste aller bekannten Nutzer wird zurückgeschickt
        """
        # Teile Nachricht anhand von Leerzeichen
        parts = message.split()
        if not parts:
            return  # Leere Nachricht – ignorieren

        command = parts[0].upper()  # Extrahiere den Befehl (JOIN, LEAVE, WHO)

        # JOIN <Handle> <Port> → neuen Nutzer zur Liste hinzufügen
        if command == "JOIN" and len(parts) == 3:
            handle, port = parts[1], int(parts[2])
            with self.lock:
                self.clients[handle] = (addr[0], port)  # IP aus Absenderadresse verwenden
            print(f"[Discovery] JOIN von {handle} ({addr[0]}:{port})")

        # LEAVE <Handle> → Nutzer aus Liste entfernen
        elif command == "LEAVE" and len(parts) == 2:
            handle = parts[1]
            with self.lock:
                self.clients.pop(handle, None)  # handle entfernen (falls vorhanden)
            print(f"[Discovery] LEAVE von {handle}")

        # WHO → Anfrage nach bekannten Nutzern beantworten
        elif command == "WHO":
            self.send_known_users(addr, sock)

    def send_known_users(self, target_addr, sock):
        """
        Baut eine KNOWUSERS-Nachricht zusammen und sendet sie zurück
        an die Adresse, von der die WHO-Anfrage kam.
        Format: KNOWUSERS <Handle1> <IP1> <Port1>, <Handle2> <IP2> <Port2>, ...
        """
        with self.lock:
            # Erstelle eine Liste aller bekannten Nutzer
            userlist = ", ".join([
                f"{handle} {ip} {port}"
                for handle, (ip, port) in self.clients.items()
            ])

        # Zusammensetzen der Antwortnachricht
        response = f"KNOWUSERS {userlist}\n"

        # Antwort per UDP zurück an den Fragenden senden
        sock.sendto(response.encode(), target_addr)

        print(f"[Discovery] Antwort an {target_addr}: {response.strip()}")

    def stop(self):
        """
        Beendet den Dienst (wird meist beim Programmende aufgerufen).
        """
        self.running = False
