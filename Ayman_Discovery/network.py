import socket
import toml
import hashlib
import time


class NetworkMessage:

    sequence_counter = 0
    
    @classmethod
    def next_sequence():
        global sequence_counter
        sequence_counter =+ 1
        return sequence_counter

    def _init_(self, command, handle, content=""):
        self.command = command       #STRING: JOIN, LEAVE, WHO ETC
        self.handle = handle         #STRING: Benutzername
        self.timestamp = time.time()  #FLOAT: Zeit (time.time())
        self.sequence = self.next_sequence(),     #INT: Zaehler
        self.content = content       #STRING: Nachricht

  

    def bytestream(self):
        ### checksum berechnen

        data_dict = {
            'command' : self.command,
            'handle' : self.handle,
            'timestamp' : self.timestamp,
            'content' : self.content
        }

        #Checksum
        data_stream = toml.dump(data_dict, sort_keys = True)
        self.checksum = hashlib.md5(data_stream.encode().hexdigest()[:8])

        data_dict['checksum'] = self.checksum

        return toml.dumps(data_dict).encode('utf-8')

    def back_to_message(cls, data):
        try:
            data_dict = toml.loads(data.decode('utf-8'))
            msg = cls(
                    command=data_dict['command'],
            handle=data_dict['handle'],
            timestamp=data_dict['timestamp'],
            sequence=data_dict['sequence'],
            content=data_dict.get('content', '')
        )
            msg.checksum = data_dict.get('checksum')
            return msg
        except:
            return None  # Falsche Daten
        
    def validate(self):
        if not self.checksum:
            return False
        
        # Checksum neu berechnen fuer pruefung
        data_dict = {
            'command': self.command,
            'handle': self.handle,
            'timestamp': self.timestamp,
            'sequence': self.sequence,
            'content': self.content
        }
        data_str = toml.dumps(data_dict, sort_keys=True)
        right_checksum = hashlib.md5(data_str.encode()).hexdigest()[:8]
        
        return self.checksum == right_checksum
                    


###################################################################


def send_slcp_broadcast(command, handle, content="", port=0000):
    """
    Sendet eine slcp-Broadcast-Nachricht.
    """

    try:
        #Nachricht erstellen
        msg = NetworkMessage(command = command, handle = handle, timestamp = time.time(),  content = content)


        #In Bytestrom konvertieren
        data = msg.bytestream()

        # UDP-Broadcast
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock: #socket.AF_INET=IPv4 adr; socket.SOCK_DGRAM= UDP Protokoll; with: Socket wird autom. wieder geschlossen
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #broadcast funktion für Socket aktivieren
            sock.sendto(data, ('255.255.255.255', port)) #Senden an alle clients, die auf diesem Port lauschen; geht an alle Rechner im lokalen netz
            sock.settimeout(5.0)  # Timeout hinzufügen
        
        print(f"[Network] Broadcast gesendet: {command} von {handle}") #DEBUG
        return True

    except Exception as e:
        print(f"[Network] Broadcast-Fehler: {e}")
        return False


# Funktion zum Senden einer Nachricht an einen spezifischen Empfänger
def slcp_MSG(empfaenger, content, contacts_path, handle):

    try:
        # 1. adressbuch laden 
        contacts = adressbuch(contacts_path)
        if not contacts:
            return False
            
        # 2. kontakt suchen 
        target_info = find_contact(empfaenger, contacts)
        if not target_info:
            print(f"Empfänger '{empfaenger}' nicht gefunden")
            return False
            
        # 3. SLCP-Nachricht erstellen
        msg = NetworkMessage(command="CHAT", handle=handle, timestamp=time.time(),content=content)
        
        # 4. Sicher senden
        return send_to_address(msg, target_info['ip'], target_info['port'])
        
    except Exception as e:
        print(f"[Network] Fehler beim Senden: {e}")
        return False


def adressbuch(contacts_path):
    try:
        with open(contacts_path, 'r') as f:
            return toml.load(f)
    except FileNotFoundError:
        print("Konfigurationsdatei nicht gefunden.")
        return None

def find_contact(empfaenger, contacts):
    for handle, data in contacts.items():
        if handle.lower() == empfaenger.strip().lower():
            return {
                'handle': handle,
                'ip': data['ziel_ip'].strip(),
                'port': int(str(data['ziel_port']).strip())
            }
    return None

def send_to_address(network_message, ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(5.0)
            data = network_message.bytestream()
            sock.sendto(data, (ip, port))
            print(f"[Network] SLCP-Nachricht an {ip}:{port} gesendet")
            return True
    except Exception as e:
        print(f"[Network] Send-Error: {e}")
        return False



