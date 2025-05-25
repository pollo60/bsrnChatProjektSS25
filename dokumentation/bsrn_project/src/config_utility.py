
## \file config_utility.py
## \brief Funktionen zum Laden und Verwalten der Konfiguration und Userdaten.
## beinhaltet:

## -1 Pfadfindung zur Konfigurationsdatei
## -2 Prüfung und Erzeugung von Kontaktlisten
## -3 Schreiben und Anzeigen von Kontakten

import toml
import sys
import os
import getpass

## \brief Bestimmt und lädt die passende Konfigurationsdatei.
## \return Tupel -Pfad zur config.toml, Auto-Start-Flag

def config_startup():
    # Bestimme das aktuelle Verzeichnis, in dem sich main.py befindet
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Standard-Konfigurationsdatei im aktuellen Ordner
    default_config = os.path.join(current_dir, "config.toml")
    

    # Finde benutzerdefinierte Konfigurationsdatei oder nutze Standard
    user_arg = next((arg for arg in sys.argv[1:] if not arg.startswith("--")), None)
    config_path = os.path.abspath(user_arg) if user_arg else default_config
    # Prüft ob "--auto" als Argument übergeben wurde
    auto_mode = "--auto" in sys.argv

    # Prüfe, ob die Datei existiert
    if not os.path.isfile(config_path):
        print(f"Fehler: Die Konfigurationsdatei '{config_path}' wurde nicht gefunden.")
        sys.exit(1)
    
    return config_path, auto_mode



## \brief Gibt den Pfad zur kontaktdatei zurück.
## Die datei wird im ornder ~/.bsrnchat abgelegt.
## \return zur Kontaktdatei

# Pfad zur benutzerspezifischen Konfigurationsdatei definieren
def get_contacts_path():
    username = getpass.getuser()   # erhalte aktuellen Benutzername
    contacts_dir = os.path.expanduser("~/.bsrnchat") # Verzeichnis im hauptordner
    os.makedirs(contacts_dir, exist_ok=True) # Erstelle Ordner falls nicht vorhanden
    return os.path.join(contacts_dir, f"contacts_{username}.toml")


##\brief prüft ob die Datei existiert und funktioniert
## wenn nicht wird eine neue Struktur erstellt
## \param contacts_path zur Kontaktdatei

def check_for_contact_list(contacts_path):
    if not os.path.exists(contacts_path):
        print(f"Kontaktliste nicht gefunden. Erzeuge neue Datei unter: {contacts_path}")
        with open(contacts_path, "w") as f:
            f.write("[kontakte]\n") #Kontakt sektion erstellen
    else:
        try:
            with open(contacts_path, "r") as f:
                content = f.read().strip()
                if not content:
                    raise ValueError("Datei ist leer.")

                data = toml.loads(content)

                if "kontakte" not in data:
                    raise ValueError("Fehlender [kontakte]-Abschnitt.")
        except (toml.TomlDecodeError, ValueError) as e:
            # print(f"[WARNUNG] Ungültige Kontaktdatei: {e}. Datei wird neu erstellt
            with open(contacts_path, "w") as f:
                f.write("[kontakte]\n")



## \brief Schreibt den eigenen Namen in die Kontaktdatei
## \param name = eigener Nutzername
## \param contacts_path zur Kontaktdatei

def write_contacts(name, contacts_path):
    try:
        try:
            with open(contacts_path, 'r') as f:
                contacts = toml.load(f)  # Vorhandene Kontakte werden geladen
        except FileNotFoundError:
            contacts = {} # Neue Kontaktliste, wenn die Datei nicht existiert

        contacts['name'] = name  # Eigenen Namen speichern

        with open(contacts_path, 'w') as f:
            toml.dump(contacts, f)   # Änderungen zurückschreiben-

        print("Kontakte-Datei wurde aktualisiert.")

    except Exception as e:
        print("Fehler beim Schreiben in die Kontakte-Datei:", e)


## \brief Legt einen neuen Kontakt mit Name, Port und IP in der Kontaktdatei an
## \param empfänger Name = neuen Kontakt
##         \param contacts_path zur Kontaktdatei

def kontaktAnlegen(empfaenger, contacts_path):
    
    try:
        # Öffnen und Einlesen der bestehenden Konfigurationsdatei im TOML-Format
        with open(contacts_path, 'r') as f:
            contacts = toml.load(f) #Kontakte Laden
    except FileNotFoundError:
        # Falls keine Konfigurationsdatei existiert, wird ein leeres Dictionary verwendet
        contacts = {}  

    
    name = empfaenger  # Name des neuen Kontakts (wird beim Funktionsaufruf übergeben)
    port = input("Gib die Portnummer ein: ").strip()  # Eingabe der Ziel-Portnummer durch den Benutzer
    ip = input("Gib die IP ein: ").strip()            # Eingabe der Ziel-IP-Adresse durch den Benutzer

    # Speichern der Kontaktdaten im Dictionary
    contacts[name] = {
        'ziel_name': name,     # Name des Empfängers
        'ziel_port': port,     # Zielport für die Kommunikation
        'ziel_ip': ip          # Ziel-IP-Adresse
    }

  # Öffnen der Konfigurationsdatei im Schreibmodus und Aktualisieren mit den neuen Kontaktdaten
    with open(contacts_path, 'w') as f:
        toml.dump(contacts, f)  # Speichern des aktualisierten Dictionarys im TOML-Format

    print("Config-Datei wurde aktualisiert.")              # Bestätigung der erfolgreichen Speicherung
    print(contacts[name]['ziel_name'])                       # Ausgabe des gespeicherten Kontaktnamens
    print(contacts[name]['ziel_port'])                       # Ausgabe der gespeicherten Portnummer
    print(contacts[name]['ziel_ip'])  




## \brief Gibt alle gespeicherten Kontakte aus der Kontaktdatei auf der Konsole aus
##                                                   \param contacts_path Pfad zur Kontaktdatei

    
def kontakteZeigen(contacts_path):
   
    try:
        # Öffnen und Einlesen der Konfigurationsdatei
        with open(contacts_path, 'r') as f:
            contacts = toml.load(f)  # Laden des Inhalts im TOML-Format
            print("Inhalt der Kontaktliste:\n")
            print(toml.dumps(contacts))  # Ausgabe des kompletten Inhalts der Datei

            #  Konfiguration (Login etc.) und Kontakte
            # in getrennten Dateien speichern, um Übersicht zu verbessern
    except FileNotFoundError:
        # Falls Datei nicht existiert Fehlermeldung anzeigen
        print(f"Datei '{contacts_path}' nicht gefunden.")
