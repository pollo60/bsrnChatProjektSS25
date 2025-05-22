
import toml


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
    port = input("Gib deine Portnummer ein: ").strip()  # Eingabe der Ziel-Portnummer durch den Benutzer
    ip = input("Gib deine IP ein: ").strip()            # Eingabe der Ziel-IP-Adresse durch den Benutzer

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