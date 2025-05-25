import socket
import toml

def send_udp_broadcast(message, whoisport):
    """
    Sendet eine UDP-Broadcast-Nachricht.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock: #socket.AF_INET=IPv4 adr; socket.SOCK_DGRAM= UDP Protokoll; with: Socket wird autom. wieder geschlossen
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #broadcast funktion für Socket aktivieren
        sock.sendto(message.encode(), ('255.255.255.255', whoisport)) #Senden an alle clients, die auf diesem Port lauschen; geht an alle Rechner im lokalen netz
        print(f"[Network] Broadcast gesendet: {message}") #Kann man das weglassen?


# Funktion zum Senden einer Nachricht an einen spezifischen Empfänger
def MSG(empfaenger, contacts_path):

    # 1. Konfiguration laden
    try:
        with open(contacts_path, 'r') as f:
            contacts = toml.load(f)
    except FileNotFoundError:
        print("Konfigurationsdatei nicht gefunden.")
        return

    # suche nach empfaenger in config
    key = None
    for k in contacts:
        if k.lower() == empfaenger.strip().lower():
            key = k
            break
    if not key:
        print(f"Empfänger '{empfaenger}' nicht gefunden in {list(contacts.keys())}")
        return

    # 3. IP und Port sauber auslesen und strippen
    data = contacts[key]
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

