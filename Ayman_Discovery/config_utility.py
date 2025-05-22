
import toml
import sys
import os

def config_startup():
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
    
    return config_path, auto_mode






# Funktion zum Anlegen eines neuen Kontakts
def kontaktAnlegen(empfaenger, config_path):
    try:
        # Öffnen und Einlesen der bestehenden Konfigurationsdatei im TOML-Format
        with open(config_path, 'r') as f:
            config = toml.load(f)
    except FileNotFoundError:
        # Falls keine Konfigurationsdatei existiert, wird ein leeres Dictionary verwendet
        config = {}

    name = empfaenger  # Name des neuen Kontakts (wird beim Funktionsaufruf übergeben)
    port = input("Gib die Portnummer ein: ").strip()  # Eingabe der Ziel-Portnummer durch den Benutzer
    ip = input("Gib die IP ein: ").strip()            # Eingabe der Ziel-IP-Adresse durch den Benutzer

    # Speichern der Kontaktdaten im Dictionary
    config[name] = {
        'ziel_name': name,     # Name des Empfängers
        'ziel_port': port,     # Zielport für die Kommunikation
        'ziel_ip': ip          # Ziel-IP-Adresse
    }

  # Öffnen der Konfigurationsdatei im Schreibmodus und Aktualisieren mit den neuen Kontaktdaten
    with open(config_path, 'w') as f:
        toml.dump(config, f)  # Speichern des aktualisierten Dictionarys im TOML-Format

    print("Config-Datei wurde aktualisiert.")              # Bestätigung der erfolgreichen Speicherung
    print(config[name]['ziel_name'])                       # Ausgabe des gespeicherten Kontaktnamens
    print(config[name]['ziel_port'])                       # Ausgabe der gespeicherten Portnummer
    print(config[name]['ziel_ip'])  






    # Funktion zur Anzeige aller gespeicherten Kontakte
def kontakteZeigen(config_path):
    try:
        # Öffnen und Einlesen der Konfigurationsdatei
        with open(config_path, 'r') as f:
            config = toml.load(f)  # Laden des Inhalts im TOML-Format
            print("Inhalt der Konfigurationsdatei:\n")
            print(toml.dumps(config))  # Ausgabe des kompletten Inhalts der Datei

            #  Konfiguration (Login etc.) und Kontakte
            # in getrennten Dateien speichern, um Übersicht zu verbessern
    except FileNotFoundError:
        # Falls Datei nicht existiert Fehlermeldung anzeigen
        print(f"Datei '{config_path}' nicht gefunden.")