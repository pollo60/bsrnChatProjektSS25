import sys
import getpass
import os
import toml

# Pfad zur benutzerspezifischen Konfigurationsdatei definieren
# Im Ordner/.bsrnchat wird für jeden client eine individuelle Konfiguarationsdatei erstellt
def get_config_path():
    username = getpass.getuser()    # Mit den Funktionen aus getpass wird der Benutzer identifiziert
    config_dir = os.path.expanduser("~/.bsrnchat")  # Pfadangabe der Datei
    os.makedirs(config_dir, exist_ok=True)  # Erstellen des Verzeichnis falls noch nicht vorhanden
    return os.path.join(config_dir, f"config_{username}.toml")  # Ausgeben des Dateipfades

CONFIG_PATH = get_config_path() # Aufrufen der Funktion um den Dateipfad weiterverbinden zukönnen

# Funktion zur Anzeige des Menüs
def zeige_menue():
    # Übersichtliche Ausgabe der verfügbaren Optionen im Hauptmenü
    print("\n Menue:")
    print("1: \t WHO - Zeige Teilnehmer")             # Option zur Anzeige aller aktuell verbundenen Clients
    print("2: \t MSG - Nachricht senden")             # Option zum Senden einer Nachricht an andere Teilnehmer
    print("3: \t EXIT - Beenden")                     # Option zum Beenden des Programms
    print("4: \t Kontakt anlegen")                   # Option zum Hinzufügen eines neuen Kontakts zur Kontaktliste
    print("5: \t Kontakte anzeigen")                 # Option zur Anzeige aller gespeicherten Kontakte
    print("6: \t unicastWHO")                        # Option zur gezielten WHO-Anfrage an einen bestimmten Client

# Funktion fuer den Start des Programms mit Login
def startup(CONFIG_PATH):
    # Prüfen, ob die Konfigurationsdatei bereits existiert
    if not os.path.exists(CONFIG_PATH):
        print("Erzeuge neue Konfiguration...")  # Hinweis für den Nutzer
        daten = datenAufnehmen()                # Aufruf zur Eingabe der benötigten Login-Daten
        inConfigSchreiben(daten, CONFIG_PATH)   # Speichern der Daten in der neuen Konfigurationsdatei
    else:
        print(f"Config-Datei '{CONFIG_PATH}' gefunden.")  # Info: bestehende Konfiguration wurde erkannt
        zeigeConfig(CONFIG_PATH)                          # Anzeige der aktuellen Konfigurationsdaten
        configAendern = input("Möchtest Du Deine Config-Datei bearbeiten? (y/n) ").strip().lower()
        if configAendern == "y":
            login_daten = datenAufnehmen()                # Neue Eingabe der Login-Daten
            inConfigSchreiben(login_daten, CONFIG_PATH)   # Überschreiben der bisherigen Konfiguration

    return CONFIG_PATH  # Rückgabe des Pfades zur verwendeten Konfigurationsdatei

# Funktion zum Anlegen eines neuen Kontakts
def kontaktAnlegen(empfaenger):
    try:
        # Öffnen und Einlesen der bestehenden Konfigurationsdatei im TOML-Format
        with open(CONFIG_PATH, 'r') as f:
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
    with open(CONFIG_PATH, 'w') as f:
        toml.dump(config, f)  # Speichern des aktualisierten Dictionarys im TOML-Format

    print("Config-Datei wurde aktualisiert.")              # Bestätigung der erfolgreichen Speicherung
    print(config[name]['ziel_name'])                       # Ausgabe des gespeicherten Kontaktnamens
    print(config[name]['ziel_port'])                       # Ausgabe der gespeicherten Portnummer
    print(config[name]['ziel_ip'])                         # Ausgabe der gespeicherten IP-Adresse

    # Funktion zur Anzeige aller gespeicherten Kontakte
def kontakteZeigen():
    try:
        # Öffnen und Einlesen der Konfigurationsdatei
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)  # Laden des Inhalts im TOML-Format
            print("Inhalt der Konfigurationsdatei:\n")
            print(toml.dumps(config))  # Ausgabe des kompletten Inhalts der Datei

            # HINWEIS: Möglicherweise sinnvoll, Konfiguration (Login etc.) und Kontakte
            # in getrennten Dateien oder Abschnitten zu verwalten, um Übersicht zu verbessern
    except FileNotFoundError:
        # Falls Datei nicht existiert, entsprechende Fehlermeldung anzeigen
        print(f"Datei '{CONFIG_PATH}' nicht gefunden.")

#####################################################################################

# Hauptfunktion zum Programmstart
def main():
    CONFIG_PATH = get_config_path()  # Pfad zur Konfigurationsdatei ermitteln

    start = input("Zum Login y und dann ENTER drücken.   ").strip()  # Benutzerabfrage zum Start

    if start != "y":
        print(" -> Programm wird beendet")  # Hinweis bei Abbruch
        sys.exit()                         # Beenden des Programms

    CONFIG_PATH = startup(CONFIG_PATH)     # Aufruf der Start- bzw. Loginroutine

    netzwerkEmpfMain(CONFIG_PATH)          # Start der Netzwerkempfangslogik (z. B. Thread oder Loop)

    WHO(CONFIG_PATH)                       # Senden einer WHO-Anfrage zur Teilnehmerermittlung

    print("Wilkommen! Was moechtest Du tun?")  # Begrüßung und Übergang zum Menü oder zur Hauptroutine

    while True:
        zeige_menue()  # Menüoptionen anzeigen
        wahl = input("Gib eine Zahl ein (1-5): ").strip()  # Benutzereingabe zur Auswahl

        if wahl == "1":
            WHO(CONFIG_PATH)  # Aufruf der Funktion zur Anzeige der verbundenen Teilnehmer
        elif wahl == "2":
            nachrichtSenden(CONFIG_PATH)  # Aufruf der Funktion zum Versenden einer Nachricht
        elif wahl == "3":
            print(" -> Programm wird beendet")  # Hinweis zur Beendigung
            sys.exit()  # Programm wird ordnungsgemäß beendet
        elif wahl == "4":
            empfaenger = input("Name des Kontakts: ").strip().lower()  # Name des neuen Kontakts abfragen
            empfaenger.lower()  # (Optional redundant – wirkt hier nicht, da nicht zugewiesen)
            kontaktAnlegen(empfaenger)  # Kontakt wird angelegt
        elif wahl == "5":
            kontakteZeigen()  # Alle gespeicherten Kontakte werden angezeigt
        elif wahl == "6":
            unicastWHO(CONFIG_PATH)  # WHO-Anfrage gezielt an einen Kontakt senden
        else:
            # Falls keine gültige Eingabe (1–6), Hinweis zur Korrektur
            print("Ungueltige Eingabe. Bitte 1, 2, 3, 4, 5 oder 6 eingeben.")

            # Einstiegspunkt
if __name__ == "__main__":
    main()  # Aufruf der Hauptfunktion nur, wenn das Skript direkt ausgeführt wird




