import socket
import toml


# Funktion zum Senden einer Nachricht an einen spezifischen Empfänger
def MSG(empfaenger, CONFIG_PATH):
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
    except FileNotFoundError:
        print("Konfigurationsdatei nicht gefunden.")
        return

    if empfaenger not in config:
        print(f"Empfänger '{empfaenger}' nicht gefunden.")
        return

    ZIEL_IP = config[empfaenger]['ziel_ip']
    ZIEL_PORT = int(config[empfaenger]['ziel_port'])

    nachricht = input("Nachricht: ").strip()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(nachricht.encode("utf-8"), (ZIEL_IP, ZIEL_PORT))
    print(f"Nachricht an {ZIEL_IP}:{ZIEL_PORT} gesendet.")
    sock.close()

# Funktion zum Senden eines WHO-Broadcasts
def discoveryWHO(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
        PORT = int(config['login_daten']['port'])
        IPNETZ = config['login_daten']['ipnetz']  # Broadcast-Adresse (z. B. 192.168.x.255)

        print("Teilnehmer werden gesucht.")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(3)

        sock.sendto(b"WHO", (IPNETZ, PORT))  # WHO-Befehl senden

        try:
            daten, addr = sock.recvfrom(1024)
            print("Antwort vom Discovery-Dienst:", daten.decode())
        except socket.timeout:
            print("Keine Teilnehmer vorhanden.")
        finally:
            sock.close()

    except Exception as e:
        print("Fehler bei WHO:", e)
