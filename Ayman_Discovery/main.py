import sys
import toml
from discovery import DiscoveryService
from ui import start_cli

if __name__ == "__main__":
    # Standard: config.toml oder benutzerdefiniert übergeben
    config_file = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "config.toml"
    auto_mode = "--auto" in sys.argv

    # Konfiguration aus TOML laden
    config = toml.load(config_file)
    handle = config["handle"]
    port = config["port"]
    whoisport = config["whoisport"]

    print(f"[MAIN] Starte Client '{handle}' auf Port {port} mit WHO-Port {whoisport} (auto={auto_mode})")

    # Discovery starten
    discovery = DiscoveryService(config_file)
    discovery.start()

    try:
        # CLI mit übergebenen Werten aufrufen
        start_cli(auto=auto_mode, handle=handle, port=port, whoisport=whoisport)
    except KeyboardInterrupt:
        print("\n[MAIN] Abbruch durch Benutzer")
    finally:
        discovery.stop()
        print("[MAIN] Discovery-Dienst gestoppt.")
