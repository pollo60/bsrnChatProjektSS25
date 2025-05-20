import socket
import threading
import toml

DISCOVERY_PORT = 4000
BUFFER_SIZE = 1024

class DiscoveryService:
    def __init__(self, config_path="config.toml"):
        self.clients = {}  # Speichert bekannte Clients: {handle: (ip, port)}
        self.running = True
        self.config = toml.load(config_path)
        self.whoisport = self.config['whoisport']
        self.lock = threading.Lock()

    def start(self):
        
        #Startet den Discovery-Dienst und wartet auf Broadcasts.
        
        thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        thread.start()

    def listen_for_messages(self):
        
        # Wartet auf WHO-, JOIN- und LEAVE-Nachrichten per UDP-Broadcast.
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', self.whoisport))

            print(f"[Discovery] Listening on UDP port {self.whoisport} for broadcast messages...")

            while self.running:
                try:
                    data, addr = sock.recvfrom(BUFFER_SIZE)
                    message = data.decode().strip()
                    print(f"[Discovery] Received: {message} from {addr}")
                    self.handle_message(message, addr, sock)
                except Exception as e:
                    print(f"[Discovery] Error: {e}")

    def handle_message(self, message, addr, sock):
        
        #Verarbeitet empfangene Nachrichten entsprechend dem SLCP-Protokoll.
        
        parts = message.split()
        if not parts:
            return

        command = parts[0].upper()

        if command == "JOIN" and len(parts) == 3:
            handle, port = parts[1], int(parts[2])
            with self.lock:
                self.clients[handle] = (addr[0], port)
            print(f"[Discovery] JOIN von {handle} ({addr[0]}:{port})")

        elif command == "LEAVE" and len(parts) == 2:
            handle = parts[1]
            with self.lock:
                self.clients.pop(handle, None)
            print(f"[Discovery] LEAVE von {handle}")

        elif command == "WHO":
            self.send_known_users(addr, sock)

    def send_known_users(self, target_addr, sock):
        
        #Sendet eine KNOWUSERS-Nachricht an den anfragenden Client.
        
        with self.lock:
            userlist = ", ".join([
                f"{handle} {ip} {port}"
                for handle, (ip, port) in self.clients.items()
            ])
        response = f"KNOWUSERS {userlist}\n"
        sock.sendto(response.encode(), target_addr)
        print(f"[Discovery] Antwort an {target_addr}: {response.strip()}")

    def stop(self):
        self.running = False
