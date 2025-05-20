# empfaenger.py

import toml
import socket
import threading

# Hauptfunktion zum Empfang von Nachrichten über UDP und zur Reaktion auf WHO
def empfangsschleife(CONFIG_PATH):
    # Konfiguration laden
    with open(CONFIG_PATH, 'r') as f:
        config = toml.load(f)

    PORT = int(config['login_daten']['port'])
    # IP = config['login_daten']['ip']
    BUFFER_SIZE = 1024

    # Socket erstellen und binden
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # akzeptiert Broadcasts
    sock.bind(('', PORT)) # Offene IP fuer den Empfang von Broadcast und Unicast Nachrichten

    print("Warte auf Nachrichten...")

    # Endlosschleife zum Empfangen
    while True:
        daten, addr = sock.recvfrom(BUFFER_SIZE)
        nachricht = daten.decode("utf-8").strip()
        print(f"Nachricht von {addr[0]}:{addr[1]} -> {nachricht}")

        # Falls WHO empfangen wird, automatische Antwort senden
        if nachricht == "WHO":
            antwort = f"{config['login_daten']['name']}|{config['login_daten']['ip']}|{config['login_daten']['port']}"
            sock.sendto(antwort.encode("utf-8"), addr)
            print(f"[Antwort gesendet] an {addr}")


# Schutzvariable, um Mehrfachstarts zu verhindern
netzwerkEmpf = False

# Funktion zum Starten des Empfangsprozesses (nur einmal)
def netzwerkEmpfMain(CONFIG_PATH):
    global netzwerkEmpf
    if netzwerkEmpf:
        return
    netzwerkEmpf = True  
    thread = threading.Thread(target=empfangsschleife, args=(CONFIG_PATH,), daemon=True)
    thread.start()
    print("[Empfaenger-Thread wurde gestartet.]")


