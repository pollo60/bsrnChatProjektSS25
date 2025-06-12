import socket
import toml
import hashlib
import time

class NetworkMessage:
    sequence_counter = 0  # Klassenweite Nachrichtenzählung

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


def send_slcp_broadcast(command, handle, content="", port=42069, broadcast_ip="255.255.255.255"):
    """Sendet eine SLCP-Broadcast-Nachricht."""
    try:
        msg = NetworkMessage(command, handle, content=content)
        data = msg.bytestream()

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(data, (broadcast_ip, port))
            sock.settimeout(5.0)

        print(f"[Network] Broadcast gesendet: {command} von {handle}")
        return True
    except Exception as e:
        print(f"[Network] Broadcast-Fehler: {e}")
        return False


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
        # Fallback: andere Sektionen durchsuchen
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
