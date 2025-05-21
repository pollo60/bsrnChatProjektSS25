# discovery.py

import socket                # Für UDP-Kommunikation
import toml                  # Für Konfigurationsdatei im TOML-Format
import threading             # Für Thread-Synchronisation

from network import send_udp_broadcast, ermittle_ip_und_broadcast, MSG  # Externe Broadcast-Funktion
from cli import get_config_path, datenAufnehmen, inConfigSchreiben, zeigeConfig         # Ermittelt Pfad zur User-Config


# ---------------------------------------------------------
# Einmaliger, global verwendeter Pfad zur Konfigurationsdatei
# ---------------------------------------------------------
CONFIG_PATH = get_config_path()


# ---------------------------------------------------------
# IP- und Broadcast-Adresse ermitteln (Standard /24-Netz)  FUER NETWORK
# ---------------------------------------------------------
def ermittle_ip_und_broadcast():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Dummy-Connect, um Interface zu wählen
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]     # Lokale IP
    s.close()
    # Erzeuge /24-Netz auf Basis der IP
    net = socket.inet_ntoa(socket.inet_aton(ip))  # rein gefahrloser Platzhalter
    # Tatsächliche Netzberechnung via ipaddress falls gewünscht:
    # import ipaddress; net = ipaddress.ip_network(ip + '/24', strict=False)
    broadcast = ip.rsplit('.', 1)[0] + '.255'
    return ip, broadcast


# ---------------------------------------------------------
# Login-Daten abfragen: Name, Port, Willkommensnachricht FUER CLI
# ---------------------------------------------------------
def datenAufnehmen():
    ip, ipnetz = ermittle_ip_und_broadcast()
    print(f"[DEBUG] Lokale IP = {ip}, Broadcast = {ipnetz}")
    name = input("Gib Deinen Namen ein: ").strip().lower()
    port = input("Gib Deine Portnummer ein: ").strip()
    hallo = input("Gib eine automatische Willkommensnachricht ein: ").strip()
    return {
        'name': name,
        'port': port,
        'ip': ip,
        'hallo': hallo,
        'ipnetz': ipnetz
    }


# ---------------------------------------------------------
# Login-Daten in Config schreiben oder updaten          FUER CLI
# ---------------------------------------------------------
def inConfigSchreiben(login_daten):
    try:
        # Bestehende Config einlesen, falls vorhanden
        try:
            with open(CONFIG_PATH, 'r') as f:
                cfg = toml.load(f)
        except FileNotFoundError:
            cfg = {}
        # Schreibe unter 'login_daten'
        cfg['login_daten'] = login_daten
        with open(CONFIG_PATH, 'w') as f:
            toml.dump(cfg, f)
        print("Config-Datei wurde aktualisiert.")
    except Exception as e:
        print("Fehler beim Schreiben der Config-Datei:", e)


# ---------------------------------------------------------
# Gespeicherte Login-Daten anzeigen                             FUER CLI
# ---------------------------------------------------------
def zeigeConfig():
    try:
        with open(CONFIG_PATH, 'r') as f:
            cfg = toml.load(f)
        login = cfg.get('login_daten', {})
        print(login.get('name', ''))
        print(login.get('port', ''))
        print(login.get('ip', ''))
        print(login.get('hallo', ''))
    except Exception as e:
        print("Fehler beim Lesen der Config-Datei:", e)


# ---------------------------------------------------------
# WHO-Broadcast senden und Antworten in Config integrieren
# ---------------------------------------------------------
def WHO(timeout=3):
    """
    Liest Port und Broadcast-Netz aus der Config, schickt einen WHO-Broadcast
    und verarbeitet alle Antworten – neue Kontakte werden direkt in der Config
    gespeichert.
    """
    try:
        # 1) Config laden
        with open(CONFIG_PATH, 'r') as f:
            cfg = toml.load(f)
        login = cfg.get('login_daten', {})
        port = int(login['port'])
        ipnetz = login['ipnetz']

        print("Teilnehmer werden gesucht...")

        # 2) Socket vorbereiten
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(timeout)

        # 3) WHO-Broadcast senden
        sock.sendto(b"WHO", (ipnetz, port))
        print("WHO-Broadcast gesendet.")

        antworten = []
        # 4) Antworten sammeln
        while True:
            try:
                daten, addr = sock.recvfrom(1024)
                antwort_str = daten.decode().strip()
                # Format: name|ip|port
                name, ip, p = antwort_str.split("|")
                antworten.append((name, ip, p))
            except socket.timeout:
                break  # keine weiteren Antworten
            except ValueError:
                print("Antwort im falschen Format:", antwort_str)
            except Exception as e:
                print("Fehler beim Empfangen:", e)
                break

        # 5) Config mit neuen Teilnehmern aktualisieren
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
        # 6) Socket schließen
        try:
            sock.close()
        except:
            pass


# ---------------------------------------------------------
# Unicast-WHO an einzelne bekannte Kontakte senden
# ---------------------------------------------------------
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
        print("Fehler bei unicastWHO:", e)
    return antworten


# ---------------------------------------------------------
# Nachricht an bestimmten Empfänger senden
# ---------------------------------------------------------
def nachrichtSenden():
    empfaenger = input("Empfänger: ").strip()
    MSG(empfaenger, CONFIG_PATH)


# ---------------------------------------------------------
# DiscoveryService-Klasse (JOIN, WHO, LEAVE)
# ---------------------------------------------------------
DISCOVERY_PORT = 4000
BUFFER_SIZE = 1024

class DiscoveryService:
    def __init__(self):
        # Bekannte Clients zwischenspeichern
        self.clients = {}
        # Steuerflag
        self.running = True
        # Config laden und Port setzen
        try:
            cfg = toml.load(CONFIG_PATH)
            self.whoisport = int(cfg.get('login_daten', {}).get('port', DISCOVERY_PORT))
        except Exception:
            self.whoisport = DISCOVERY_PORT
        # Lock für Threads
        self.lock = threading.Lock()

    def start(self):
        # Launch Listener-Thread
        t = threading.Thread(target=self.listen_for_messages, daemon=True)
        t.start()

    def listen_for_messages(self):
        # Socket für eingehende UDP-Pakete
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', self.whoisport))
        print(f"🌐 Discovery läuft auf Port {self.whoisport}...")
        # Endlosschleife
        while self.running:
            try:
                daten, addr = sock.recvfrom(BUFFER_SIZE)
                msg = daten.decode().strip()
                print(f"Nachricht von {addr}: {msg}")
                self.handle_message(msg, addr, sock)
            except Exception as e:
                print(f"Fehler im Listener: {e}")

    def handle_message(self, message, addr, sock):
        parts = message.split()
        if not parts:
            return
        cmd = parts[0].upper()
        # JOIN <handle> <port>
        if cmd == 'JOIN' and len(parts) == 3:
            handle, port = parts[1], int(parts[2])
            with self.lock:
                self.clients[handle] = (addr[0], port)
            print(f"✅ {handle} online unter {addr[0]}:{port}")
        # WHO
        elif cmd == 'WHO':
            self.send_known_users(addr, sock)
        # LEAVE <handle>
        elif cmd == 'LEAVE' and len(parts) == 2:
            handle = parts[1]
            with self.lock:
                self.clients.pop(handle, None)
            print(f"👋 {handle} hat das Netzwerk verlassen.")
        else:
            print(f"Unbekannter Befehl: {message}")

    def send_known_users(self, target, sock):
        with self.lock:
            if not self.clients:
                payload = 'Niemand online'
            else:
                payload = ', '.join(f"{h}:{p}" for h, (_, p) in self.clients.items())
        resp = f"KNOWUSERS {payload}\n"
        sock.sendto(resp.encode(), target)
        print(f"Gesendet an {target}: {resp.strip()}")

    def stop(self):
        self.running = False
        print("🛑 Discovery gestoppt.")
