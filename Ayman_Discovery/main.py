import sys # Importieren des sys-Moduls für Systemfunktionen
import os # Importieren des os-Moduls zur Arbeit mit Pfaden
import toml  # Importieren des toml-Moduls zum Lesen/Schreiben von TOML-Dateien
from discovery import DiscoveryService # Importieren des Discovery-Dienstes
from ui import start_cli # Importieren der CLI-Funktion für Benutzerinteraktionen
from config_utility import config_startup, get_contacts_path # Importieren der Konfigurationsstart-Funktion

if __name__ == "__main__":

    config_path, auto_mode = config_startup()  # Pfad zur Konfigurationsdatei & Automodus ermitteln

    contacts_path = get_contacts_path()

    # TOML-Konfigurationsdatei mit `with open(...)` laden
    try:
        with open(config_path, 'r') as f:
            config = toml.load(f) # Konfigurationsdaten aus Datei lesen
    except Exception as e:
        print(f"Fehler beim Laden der Konfigurationsdatei: {e} ⚠️") # Fehlermeldung ausgeben
        sys.exit(1) # Programm beenden

    # Werte aus der geladenen Konfiguration entnehmen
    handle = config.get("handle", "Unbekannt") # Benutzername 
    port = config.get("port", 0000) # Port für den Client, mit standardargument, falls der prozess scheitert
    whoisport = config.get("whoisport", 1111) # WHO-Port für Discovery-Kommunikation, mit standardargument, falls der prozess scheitert
    # Falls ein Wert fehlt, wird ein Standartwert verwendet
    #print(f"[MAIN] Starte Client '{handle}' auf Port {port} mit WHO-Port {whoisport} (auto={auto_mode})") #Das vielleicht nicht printen? Oder gibt das ohne Testzwecke Infos?

    # Discovery starten
    discovery = DiscoveryService(config_path)  # Discovery-Service initialisieren
    discovery.start()  # Discovery-Dienst starten

    try:
        # Start der Benutzeroberfläche (CLI)
        start_cli(auto=auto_mode, handle=handle, port=port, whoisport=whoisport, config_path = config_path, contacts_path=contacts_path)
    except KeyboardInterrupt:
        print("\nBenutzer hat abgebrochen🛑") # Nachricht bei Abbruch durch Strg+C, wiird von der Main ausgeführt
    finally:
        discovery.stop()
        print("Discovery-Dienst gestoppt👋") # Bestätigung der Beendigung, wird von der Main ausgeführt
