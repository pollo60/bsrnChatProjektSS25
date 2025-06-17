# network_daemon.py
import json
import socket
import time
import toml
import os

DISCOVERY_FILE = "discovery_output.json"
CONFIG_PATH = "config.toml"

def load_clients():
    """Liest bekannte Clients aus der Discovery-Datei."""
    if not os.path.exists(DISCOVERY_FILE):
        return {}
    try:
        with open(DISCOVERY_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[Netzwerk] Fehler beim Laden der discovery_output.json: {e}")
        return {}

def send_udp(ip, port, message):
    """Sendet eine Nachricht an einen bestimmten Nutzer."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(message.encode(), (ip, port))
        print(f"[Netzwerk] Nachricht an {ip}:{port} gesendet: {message}")
    except Exception as e:
        print(f"[Netzwerk] Fehler beim Senden: {e}")

def main():
    print("[Netzwerk] Starte Netzwerk-Dienst...")
    
    # Konfiguration laden
    try:
        config = toml.load(CONFIG_PATH)
        my_handle = config.get("handle", "Unbekannt")
    except Exception as e:
        print(f"[Netzwerk] Fehler beim Laden der Konfiguration: {e}")
        return

    try:
        while True:
            clients = load_clients()

            if clients:
                print("\n📡 Bekannte Clients:")
                for h, (ip, p) in clients.items():
                    print(f" - {h}: {ip}:{p}")

            msg_input = input("\nNachricht senden? (Format: Empfänger Nachricht) oder 'q' zum Beenden:\n> ").strip()
            if msg_input.lower() == "q":
                break

            try:
                empfaenger, inhalt = msg_input.split(maxsplit=1)
                if empfaenger in clients:
                    ip, port = clients[empfaenger]
                    nachricht = f"CHAT {my_handle}: {inhalt}"
                    send_udp(ip, int(port), nachricht)
                else:
                    print("⚠️ Empfänger nicht bekannt.")
            except ValueError:
                print("⚠️ Ungültiges Format. Beispiel: Tom Hallo!")

    except KeyboardInterrupt:
        print("\n[Netzwerk] Beende Dienst.")

if __name__ == "__main__":
    main()
