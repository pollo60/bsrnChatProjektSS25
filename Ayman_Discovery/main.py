import sys      # Zugriff auf Kommandozeilenargumente
import os       # Arbeiten mit Dateipfaden
import toml     # Einlesen von TOML-Konfigurationsdateien

from discovery import DiscoveryService
from ui import start_cli
from config_utility import (
    config_startup,
    get_contacts_path
)

def main():
    print("[DEBUG] main.py gestartet.")
    print(f"[DEBUG] sys.argv = {sys.argv}")

    # Konfiguration laden (von Datei oder automatisch)
    config_path, auto_mode, handle, port, whoisport, ip, broadcast_ip = config_startup()
    print(f"[DEBUG] config_startup abgeschlossen: {config_path}")

    # Kontaktliste initialisieren
    contacts_path = get_contacts_path()
    print(f"[DEBUG] contacts_path: {contacts_path}")
    print(f"[DEBUG] handle={handle}, port={port}, whoisport={whoisport}, broadcast_ip={broadcast_ip}")

    # Discovery-Dienst starten
    print("[DEBUG] Starte Discovery-Dienst...")
    discovery = DiscoveryService(config_path)
    discovery.start()
    print("[DEBUG] Discovery-Dienst gestartet")

    try:
        # Benutzeroberfläche (CLI) starten
        print("[DEBUG] Starte CLI...")
        start_cli(
            auto=auto_mode,
            handle=handle,
            port=port,
            whoisport=whoisport,
            config_path=config_path,
            contacts_path=contacts_path,
            broadcast_ip=broadcast_ip
        )
        if auto_mode:
            print("[INFO] Automodus abgeschlossen. Netzwerkbeitritt und WHO-Anfrage gesendet.")
    except KeyboardInterrupt:
        print("\n[ABBRUCH] Benutzer hat mit Strg+C beendet.")
    finally:
        discovery.stop()
        print("[ENDE] Discovery-Dienst wurde gestoppt.")

if __name__ == "__main__":
    main()
