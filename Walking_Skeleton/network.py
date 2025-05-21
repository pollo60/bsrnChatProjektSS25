# network.py


import toml
import socket
import threading


def send_udp_broadcast(CONFIG_PATH, message):
    
    with open(CONFIG_PATH, 'r') as f:
        config = toml.load(f)
    
    
    PORT = int(config['login_daten']['port'])
    IPNETZ = config['login_daten']['ipnetz']

    addr = {}
    addr [0] = IPNETZ
    addr [1] = PORT


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(('', PORT))

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(message.encode("utf-8"), addr)
            print(f"[Network] Broadcast gesendet: {message}")
    

# Funktion zum Senden einer Nachricht an einen spezifischen Empfänger
def MSG(empfaenger, CONFIG_PATH):

    # 1. Konfiguration laden
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
    except FileNotFoundError:
        print("Konfigurationsdatei nicht gefunden.")
        return

    # 2. Kontaktschlüssel case‑insensitive finden
    gesucht = empfaenger.strip().lower()
    key = next((k for k in config if k.lower() == gesucht), None)
    if key is None or key == 'login_daten':
        print(f"Empfänger '{empfaenger}' nicht gefunden. Verfügbare Kontakte: {[k for k in config if k!='login_daten']}")
        return

    # 3. IP und Port sauber auslesen und strippen
    data = config[key]
    ZIEL_IP   = data['ziel_ip'].strip()
    ZIEL_PORT = int(str(data['ziel_port']).strip())

    # 4. Nachricht vom Benutzer abfragen
    nachricht = input("Nachricht: ").strip()

    # 5. Debug-Ausgabe
    print(f"[DEBUG] Sende Nachricht an {key} -> IP={ZIEL_IP!r}, Port={ZIEL_PORT}")

    # 6. Nachricht per UDP senden
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(nachricht.encode("utf-8"), (ZIEL_IP, ZIEL_PORT))
        print(f"Nachricht an {ZIEL_IP}:{ZIEL_PORT} gesendet.")
    except Exception as e:
        print("Send-Error:", e)
    finally:
        sock.close()


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
