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

    if empfaenger.lower() not in config:
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
def MSG(empfaenger, CONFIG_PATH):
    import toml
    import socket

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

