import sys
import os
import toml
from discovery import DiscoveryService
from ui import start_cli

if __name__ == "__main__":
    # Bestimme das aktuelle Verzeichnis, in dem sich main.py befindet
    current_dir = os.path.dirname(os.path.abspath(__file__))
    default_config = os.path.join(current_dir, "config.toml")

    # Finde benutzerdefinierte Konfigurationsdatei oder nutze Standard
    user_arg = next((arg for arg in sys.argv[1:] if not arg.startswith("--")), None)
    config_path = os.path.abspath(user_arg) if user_arg else default_config
    auto_mode = "--auto" in sys.argv

    # Prüfe, ob die Datei existiert
    if not os.path.isfile(config_path):
        print(f"❌ Fehler: Die Konfigurationsdatei '{config_path}' wurde nicht gefunden.")
        sys.exit(1)

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
        start_cli(auto=auto_mode, handle=handle, port=port, whoisport=whoisport, config_path=config_path)
    except KeyboardInterrupt:
        print("\n[MAIN] Abbruch durch Benutzer")
    finally:
        discovery.stop()
        print("[MAIN] Discovery-Dienst gestoppt.")
