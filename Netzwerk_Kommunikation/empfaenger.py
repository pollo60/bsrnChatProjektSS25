# empfaenger.py

import toml
import socket
import threading

# Hauptfunktion zum Empfang von Nachrichten über UDP und zur Reaktion auf WHO
def empfangsschleife():
    # Konfiguration laden
    with open('configANSATZ.toml', 'r') as f:
        config = toml.load(f)

    PORT = int(config['login_daten']['port'])
    IP = config['login_daten']['ip']
    BUFFER_SIZE = 1024

    # Socket erstellen und binden
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))

    print("Warte auf Nachrichten...")

    # Endlosschleife zum Empfangen
    while True:
        daten, addr = sock.recvfrom(BUFFER_SIZE)
        nachricht = daten.decode("utf-8").strip()
        print(f"Nachricht von {addr[0]}:{addr[1]} -> {nachricht}")

        # Falls WHO empfangen wird, automatische Antwort senden
        if nachricht == "WHO":
            antwort = f"{config['login_daten']['name']} ist online"
            sock.sendto(antwort.encode("utf-8"), addr)
            print(f"[Antwort gesendet] an {addr}")


# Schutzvariable, um Mehrfachstarts zu verhindern
netzwerkEmpf = False

# Funktion zum Starten des Empfangsprozesses (nur einmal)
def netzwerkEmpfMain():
    global netzwerkEmpf
    if netzwerkEmpf:
        return
    netzwerkEmpf = True  

    # Optional: Einmaliger WHO-Broadcast zur initialen Suche
    discoveryWHO()

    thread = threading.Thread(target=empfangsschleife, daemon=True)
    thread.start()
    print("[Empfaenger-Thread wurde gestartet.]")


# Funktion zum Senden eines WHO-Broadcasts
def discoveryWHO():
    try:
        with open('configANSATZ.toml', 'r') as f:
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
