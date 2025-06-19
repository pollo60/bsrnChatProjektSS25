# network_process.py
import socket
import toml
import hashlib
import time
import json
import os
from queue import Queue, Empty

COMM_FILE = "discovery_output.json"

class NetworkMessage:
    sequence_counter = 0

    @classmethod
    def next_sequence(cls):
        cls.sequence_counter += 1
        return cls.sequence_counter

    def __init__(self, command, handle, timestamp=None, content=""):
        self.command = command
        self.handle = handle
        self.timestamp = timestamp if timestamp else time.time()
        self.sequence = self.next_sequence()
        self.content = content
        self.checksum = None

    def bytestream(self):
        data = {
            'command': self.command,
            'handle': self.handle,
            'timestamp': self.timestamp,
            'sequence': self.sequence,
            'content': self.content
        }
        raw = toml.dumps(data)
        self.checksum = hashlib.md5(raw.encode()).hexdigest()[:8]
        data['checksum'] = self.checksum
        return toml.dumps(data).encode('utf-8')

    @classmethod
    def back_to_message(cls, data):
        try:
            parsed = toml.loads(data.decode('utf-8'))
            msg = cls(
                command=parsed['command'],
                handle=parsed['handle'],
                timestamp=parsed['timestamp'],
                content=parsed.get('content', '')
            )
            msg.sequence = parsed.get('sequence', 0)
            msg.checksum = parsed.get('checksum')
            return msg
        except:
            return None

    def validate(self):
        if not self.checksum:
            return False
        data = {
            'command': self.command,
            'handle': self.handle,
            'timestamp': self.timestamp,
            'sequence': self.sequence,
            'content': self.content
        }
        expected = hashlib.md5(toml.dumps(data).encode()).hexdigest()[:8]
        return self.checksum == expected

#Sollte hier der slcp broadcast mittels sockets kommunizieren?
def send_slcp_broadcast(msg_queue: Queue, port=42069, broadcast_ip="255.255.255.255"):
    """Sendet eine SLCP-Broadcast-Nachricht."""
    while True:
        try:
            # Versuche, eine Nachricht aus der Queue zu lesen (mit Timeout, damit der Thread sauber beenden könnte)
            command, handle, content = msg_queue.get(timeout=1)

            if command in {"JOIN", "LEAVE", "WHO"}:
                # Standard-Broadcast
                msg = NetworkMessage(command, handle, content=content)
                data = msg.bytestream()

                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.sendto(data, (broadcast_ip, port))
                    sock.settimeout(5.0)

                print(f"[Network] Broadcast gesendet: {command} von {handle}")
            elif command == "CHAT":
                # Einzel-Nachricht, content ist JSON-kodiert
                payload = json.loads(content)
                empfaenger = payload["empfaenger"]
                nachricht = payload["nachricht"]
                contacts_path = payload["contacts_path"]
                contacts = adressbuch(contacts_path)
                if not contacts:
                    print("[Network] Keine Kontakte gefunden")
                    continue
                target = find_contact(empfaenger, contacts)
                if not target:
                    print(f"[Network] Empfänger '{empfaenger}' nicht gefunden")
                    continue
                msg = NetworkMessage("CHAT", handle, content=nachricht)
                send_to_address(msg, target["ip"], target["port"])
        except Empty:
            # Keine Nachricht in der Queue: einfach warten
            continue
        except Exception as e:
            print(f"[Network] Broadcast-Fehler: {e}")

#Hier kommuniziert SLCP über UDP, aber wir sollen doch eig im Netzwerk über queues kommunizieren
#Er darf über UDP kommuizieren, es geht um die befehle von der Benutzerschnittstelle an den Netzwerkmanager
def slcp_MSG(empfaenger, content, contacts_path, handle):
    """Sendet eine Nachricht an einen Kontakt aus der Kontaktliste."""
    try:
        contacts = adressbuch(contacts_path)
        if not contacts:
            return False
        target = find_contact(empfaenger, contacts)
        if not target:
            print(f"Empfänger '{empfaenger}' nicht gefunden")
            return False
        msg = NetworkMessage("CHAT", handle, content=content)
        return send_to_address(msg, target['ip'], target['port'])
    
    except Exception as e:
        print(f"[Network] Fehler beim Senden: {e}")
        return False


def adressbuch(contacts_path):
    """Lädt die Kontaktliste aus einer TOML-Datei."""
    try:
        with open(contacts_path, 'r') as f:
            data = toml.load(f)
        if "kontakte" in data:
            return data["kontakte"]
        return {
            key: val for key, val in data.items()
            if isinstance(val, dict) and "ziel_name" in val
        }
    except FileNotFoundError:
        print("[WARNUNG] Kontaktdatei nicht gefunden.")
        return None


def find_contact(empfaenger, contacts):
    """Sucht einen Kontakt anhand des Namens."""
    for name, info in contacts.items():
        if name.lower() == empfaenger.strip().lower():
            return {
                'handle': name,
                'ip': info['ziel_ip'].strip(),
                'port': int(str(info['ziel_port']).strip())
            }
    return None

#Kann man diese Funktion mittels Queues lösen -> wg direct messaging
def send_to_address(message, ip, port):
    """Sendet eine Nachricht an eine bestimmte IP und Port."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(5.0)
            sock.sendto(message.bytestream(), (ip, port))
        print(f"[Network] Nachricht an {ip}:{port} gesendet")
        return True
    except Exception as e:
        print(f"[Network] Send-Error: {e}")
        return False


def get_discovered_clients():
    """Liest bekannte Nutzer aus der JSON-Zwischendatei."""
    if not os.path.exists(COMM_FILE):
        return {}
    try:
        with open(COMM_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Network] Fehler beim Lesen von {COMM_FILE}: {e}")
        return {}
