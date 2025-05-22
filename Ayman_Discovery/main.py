import sys
import os
import toml
from discovery import DiscoveryService
from ui import start_cli
from config_utility import config_startup, get_contacts_path

if __name__ == "__main__":

    config_path, auto_mode = config_startup()

    contacts_path = get_contacts_path()

    # ✅ TOML-Konfigurationsdatei mit `with open(...)` laden
    try:
        with open(config_path, 'r') as f:
            config = toml.load(f)
    except Exception as e:
        print(f"❌ Fehler beim Laden der Konfigurationsdatei: {e}")
        sys.exit(1)

    # Werte aus der geladenen Konfiguration entnehmen
    handle = config.get("handle", "Unbekannt")
    port = config.get("port", 5000)
    whoisport = config.get("whoisport", 54321)

    print(f"[MAIN] Starte Client '{handle}' auf Port {port} mit WHO-Port {whoisport} (auto={auto_mode})")

    # Discovery starten
    discovery = DiscoveryService(config_path)
    discovery.start()

    try:
#############################################################
        start_cli(auto=auto_mode, handle=handle, port=port, whoisport=whoisport, config_path=config_path, contacts_path=contacts_path)
    except KeyboardInterrupt:
        print("\n[MAIN] Abbruch durch Benutzer")
    finally:
        discovery.stop()
        print("[MAIN] Discovery-Dienst gestoppt.")
