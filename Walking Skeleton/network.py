# network.py


import toml
import socket
import threading


def send_udp_broadcast(CONFIG_PATH):
    
    with open(CONFIG_PATH, 'r') as f:
        config = toml.load(f)
    
    PORT = int(config['login_daten']['port'])
    IP = config['login_daten']['ip']
    message = config['login_daten']['hallo']
    BUFFER_SIZE = 1024

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(('', PORT))

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(message.encode(), ('255.255.255.255', PORT))
            print(f"[Network] Broadcast gesendet: {message}")





def empfangsschleifeWHO(CONFIG_PATH):
    # Konfiguration laden
    with open(CONFIG_PATH, 'r') as f:
        config = toml.load(f)

    PORT = int(config['login_daten']['port'])
    IP = config['login_daten']['ip']
    BUFFER_SIZE = 1024

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(('', PORT))

    print("Warte auf Nachrichten...")

    # Endlosschleife zum Empfangen
    while True:
        daten, addr = sock.recvfrom(BUFFER_SIZE)
        message = daten.decode("utf-8").strip()
        print(f"Nachricht von {addr[0]}:{addr[1]} -> {message}")

        # Falls WHO empfangen wird, automatische Antwort senden
        if message == "WHO":
            antwort = f"{config['login_daten']['name']}|{config['login_daten'][IP]}|{config['login_daten'][PORT]}"
            sock.sendto(antwort.encode("utf-8"), addr)
            print(f"[Antwort gesendet] an {addr}")

