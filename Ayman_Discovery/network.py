import socket
import toml

def send_udp_broadcast(message, whoisport):
    """
    Sendet eine UDP-Broadcast-Nachricht.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(message.encode(), ('255.255.255.255', whoisport))
        print(f"[Network] Broadcast gesendet: {message}")


# Funktion zum Senden einer Nachricht an einen spezifischen Empfänger
def MSG(empfaenger, config_path):

    # 1. Konfiguration laden
    try:
        with open(config_path, 'r') as f:
            config = toml.load(f)
    except FileNotFoundError:
        print("Konfigurationsdatei nicht gefunden.")
        return

    # suche nach empfaenger in config
    key = None
    for k in config:
        if k.lower() == empfaenger.strip().lower():
            key = k
            break
    if not key:
        print(f"Empfänger '{empfaenger}' nicht gefunden in {list(config.keys())}")
        return

    # 3. IP und Port sauber auslesen und strippen
    data = config[key]
    ZIEL_IP   = data['ziel_ip'].strip()
    ZIEL_PORT = int(str(data['ziel_port']).strip())

    # 4. Nachricht vom Benutzer abfragen
    message = input("Nachricht: ").strip()

    # 5. Debug-Ausgabe
    print(f"[DEBUG] Sende Nachricht an {key} -> IP={ZIEL_IP!r}, Port={ZIEL_PORT}")

    # 6. Nachricht per UDP senden
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(message.encode("utf-8"), (ZIEL_IP, ZIEL_PORT))
        print(f"Nachricht an {ZIEL_IP}:{ZIEL_PORT} gesendet.")
    except Exception as e:
        print("Send-Error:", e)
    finally:
        sock.close()



# Nachricht an bestimmten Empfänger senden
def nachrichtSenden(config_path):
    empfaenger = input("Empfaenger: ")
    MSG(empfaenger, config_path)

