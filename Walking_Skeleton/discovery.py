import socket
import toml
import threading
import time

from network import MSG
from config_utility import get_config_path

CONFIG_PATH = get_config_path()

def WHO(timeout=3):
    try:
        with open(CONFIG_PATH, 'r') as f:
            cfg = toml.load(f)
        login = cfg['login_daten']
        port = int(login['port'])
        ipnetz = login['ipnetz']

        print("Teilnehmer werden gesucht...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(timeout)
        sock.sendto(b"WHO", (ipnetz, port))
        print("WHO-Broadcast gesendet.")

        antworten = []
        while True:
            try:
                daten, _ = sock.recvfrom(1024)
                name, ip, p = daten.decode().strip().split("|")
                antworten.append((name, ip, p))
            except socket.timeout:
                break
            except ValueError:
                print("Antwort im falschen Format:", daten)
            except Exception as e:
                print("Fehler beim Empfangen:", e)
                break

        neue = False
        for name, ip, p in antworten:
            print(f"Antwort von {name} -> IP: {ip}, Port: {p}")
            if name not in cfg:
                cfg[name] = {'ziel_ip': ip, 'ziel_port': p}
                neue = True

        if neue:
            with open(CONFIG_PATH, 'w') as f:
                toml.dump(cfg, f)
            print("Neue Teilnehmer wurden in der Config gespeichert.")
        elif not antworten:
            print("Keine Teilnehmer geantwortet.")
        else:
            print("Alle Teilnehmer bereits bekannt.")

    except Exception as e:
        print("Fehler bei WHO():", e)
    finally:
        try: sock.close()
        except: pass

def unicastWHO(timeout=1):
    antworten = []
    try:
        with open(CONFIG_PATH, 'r') as f:
            cfg = toml.load(f)
        for name, data in cfg.items():
            if name == 'login_daten':
                continue
            target = (data['ziel_ip'], int(data['ziel_port']))
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(timeout)
                sock.sendto(b"WHO", target)
                daten, addr = sock.recvfrom(1024)
                antworten.append((daten.decode().strip(), addr))
            except socket.timeout:
                pass
            finally:
                sock.close()
    except Exception as e:
        print("Fehler bei unicastWHO():", e)
    return antworten

def nachrichtSenden():
    empfaenger = input("Empfänger: ").strip()
    MSG(empfaenger, CONFIG_PATH)

DISCOVERY_PORT = 4000
BUFFER_SIZE = 1024

class DiscoveryService:
    def __init__(self):
        self.clients = {}  # {handle: (ip, port)}
        self.running = True
        try:
            cfg = toml.load(CONFIG_PATH)
            self.whoisport = int(cfg.get('login_daten', {}).get('port', DISCOVERY_PORT))
        except:
            self.whoisport = DISCOVERY_PORT
        self.lock = threading.Lock()
        self.listener_thread = None

    def start(self):
        self.listener_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        self.listener_thread.start()
        print(f"Discovery Service laeuft auf Port {self.whoisport}")
        self.announce_join()

    def announce_join(self):
        try:
            with open(CONFIG_PATH, 'r') as f:
                cfg = toml.load(f)
            login = cfg['login_daten']
            name = login['name']
            port = login['port']
            ipnetz = login['ipnetz']
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            message = f"JOIN {name} {port}"
            sock.sendto(message.encode(), (ipnetz, self.whoisport))
            sock.close()
            print(f"JOIN Broadcast gesendet: {name} auf Port {port}")
        except Exception as e:
            print(f"Fehler beim JOIN Broadcast: {e}")

    def listen_for_messages(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('', self.whoisport))
            print(f"Discovery Service gebunden an Port {self.whoisport}")
            
            while self.running:
                try:
                    daten, addr = sock.recvfrom(BUFFER_SIZE)
                    msg = daten.decode().strip()
                    print(f"Discovery Nachricht von {addr}: {msg}")
                    self.handle_message(msg, addr, sock)
                except Exception as e:
                    if self.running:
                        print(f"Fehler im Listener: {e}")
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"Schwerwiegender Fehler im Discovery Service: {e}")
        finally:
            sock.close()
            print("Discovery Listener beendet")

    def handle_message(self, message, addr, sock):
        parts = message.split()
        if not parts:
            return
        cmd = parts[0].upper()
        if cmd == 'JOIN' and len(parts)==3:
            h, p = parts[1], int(parts[2])
            with self.lock:
                self.clients[h] = (addr[0], p)
            print(f"{h} online unter {addr[0]}:{p}")
            
            # Antwort mit eigenen Daten
            try:
                with open(CONFIG_PATH, 'r') as f:
                    cfg = toml.load(f)
                login = cfg['login_daten']
                my_name = login['name']
                my_port = login['port']
                response = f"JOIN {my_name} {my_port}"
                sock.sendto(response.encode(), addr)
            except Exception as e:
                print(f"Fehler beim Senden der JOIN-Antwort: {e}")
                
        elif cmd == 'WHO':
            self.send_known_users(addr, sock)
        elif cmd == 'LEAVE' and len(parts)==2:
            h = parts[1]
            with self.lock:
                self.clients.pop(h, None)
            print(f"{h} hat das Netzwerk verlassen.")
        else:
            print(f"Unbekannter Discovery-Befehl: {message}")

    def send_known_users(self, target, sock):
        with self.lock:
            if not self.clients:
                payload = 'Niemand online'
            else:
                payload = ', '.join(f"{h}:{p}" for h,(i,p) in self.clients.items())
        resp = f"KNOWUSERS {payload}\n"
        sock.sendto(resp.encode(), target)
        print(f"Gesendet an {target}: {resp.strip()}")

    def stop(self):
        # LEAVE Broadcast senden
        try:
            with open(CONFIG_PATH, 'r') as f:
                cfg = toml.load(f)
            login = cfg['login_daten']
            name = login['name']
            ipnetz = login['ipnetz']
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            message = f"LEAVE {name}"
            sock.sendto(message.encode(), (ipnetz, self.whoisport))
            sock.close()
            print(f"LEAVE Broadcast gesendet: {name}")
        except Exception as e:
            print(f"Fehler beim LEAVE Broadcast: {e}")
        
        self.running = False
        if self.listener_thread:
            self.listener_thread.join(timeout=1.0)
        print("Discovery Service gestoppt.")