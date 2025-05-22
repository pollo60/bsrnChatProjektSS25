import sys # Importieren des sys-Moduls für Systemfunktionen
import os # Importieren des os-Moduls zur Arbeit mit Pfaden
import toml  # Importieren des toml-Moduls zum Lesen/Schreiben von TOML-Dateien
from discovery import DiscoveryService # Importieren des Discovery-Dienstes
from ui import start_cli # Importieren der CLI-Funktion für Benutzerinteraktionen
from config_utility import config_startup # Importieren der Konfigurationsstart-Funktion

if __name__ == "__main__":

    config_path, auto_mode = config_startup()  # Pfad zur Konfigurationsdatei & Automodus ermitteln

    # TOML-Konfigurationsdatei mit `with open(...)` laden
    try:
        with open(config_path, 'r') as f:
            config = toml.load(f) # Konfigurationsdaten aus Datei lesen
    except Exception as e:
        print(f"Fehler beim Laden der Konfigurationsdatei: {e}") # Fehlermeldung ausgeben
        sys.exit(1) # Programm beenden

    # Werte aus der geladenen Konfiguration entnehmen
    handle = config.get("handle", "Unbekannt") # Benutzername 
    port = config.get("port", 5000) # Port für den Client
    whoisport = config.get("whoisport", 54321) # WHO-Port für Discovery-Kommunikation
    # Falls ein Wert fehlt, wird ein Standartwert verwendet
    print(f"[MAIN] Starte Client '{handle}' auf Port {port} mit WHO-Port {whoisport} (auto={auto_mode})")

    # Discovery starten
    discovery = DiscoveryService(config_path)  # Discovery-Service initialisieren
    discovery.start()  # Discovery-Dienst starten

    try:
        # Start der Benutzeroberfläche (CLI)
        start_cli(auto=auto_mode, handle=handle, port=port, whoisport=whoisport, config_path=config_path)
    except KeyboardInterrupt:
        print("\n[MAIN] Abbruch durch Benutzer") # Nachricht bei Abbruch durch Strg+C
    finally:
        discovery.stop()
        print("[MAIN] Discovery-Dienst gestoppt.") # Bestätigung der Beendigung
