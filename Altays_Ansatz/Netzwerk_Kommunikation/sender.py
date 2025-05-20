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
def discoveryWHO(ipnetz, port, timeout=3):
    antworten = []

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(timeout)

        # WHO senden
        sock.sendto(b"WHO", (ipnetz, port))
        print("WHO-Broadcast gesendet.")

        while True:
            try:
                daten, addr = sock.recvfrom(1024)
                teilnehmername = daten.decode().strip()
                ip = addr[0]
                port = addr[1]
                antworten.append((teilnehmername, ip, port))
            except socket.timeout:
                break  # Ende der Antwortphase
            except Exception as e:
                print("Fehler beim Empfangen einer Antwort:", e)
                break
    finally:
        sock.close()

    return antworten
