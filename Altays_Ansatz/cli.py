# cli.py

import sys
import getpass
import os
import toml

from Altays_Ansatz.discoveryANSATZ import datenAufnehmen, inConfigSchreiben, zeigeConfig, WHO, MSG, nachrichtSenden
from Netzwerk_Kommunikation.empfaenger import netzwerkEmpfMain


# Pfad zur benutzerspezifischen Konfigurationsdatei definieren
def get_config_path():
    username = getpass.getuser()
    config_dir = os.path.expanduser("~/.bsrnchat")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, f"config_{username}.toml")


CONFIG_PATH = get_config_path()


# Funktion zur Anzeige des Menüs
def zeige_menue():
    print("\n Menue:")
    print("1: \t WHO - Zeige Teilnehmer")
    print("2: \t MSG - Nachricht senden")
    print("3: \t EXIT - Beenden")
    print("4: \t Kontakt anlegen")
    print("5: \t Kontakte anzeigen")


# Funktion fuer den Start des Programms mit Login
def startup(CONFIG_PATH):
    if not os.path.exists(CONFIG_PATH):
        print("Erzeuge neue Konfiguration...")
        daten = datenAufnehmen()
        inConfigSchreiben(daten, CONFIG_PATH)
    else:
        print(f"Config-Datei '{CONFIG_PATH}' gefunden.")
        zeigeConfig(CONFIG_PATH)
        configAendern = input("Möchtest Du Deine Config-Datei bearbeiten? (y/n) ").strip().lower()
        if configAendern == "y":
            login_daten = datenAufnehmen()
            inConfigSchreiben(login_daten, CONFIG_PATH)

    return CONFIG_PATH
            



# Funktion zum Anlegen eines neuen Kontakts
def kontaktAnlegen(empfaenger):
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
    except FileNotFoundError:
        config = {}

    name = empfaenger
    port = input("Gib die Portnummer ein: ").strip()
    ip = input("Gib die IP ein: ").strip()

    config[name] = {
        'ziel_name': name,
        'ziel_port': port,
        'ziel_ip': ip
    }

    with open(CONFIG_PATH, 'w') as f:
        toml.dump(config, f)

    print("Config-Datei wurde aktualisiert.")
    print(config[name]['ziel_name'])
    print(config[name]['ziel_port'])
    print(config[name]['ziel_ip'])


def kontakteZeigen():
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
            print("Inhalt der Konfigurationsdatei:\n")
            print(toml.dumps(config))  # Gibt die ganze Datei aus \\ VIELLEICHT SEPARATE DATEI FUER CONFIG UND KONTAKTE?
    except FileNotFoundError:
        print(f"Datei '{CONFIG_PATH}' nicht gefunden.")


#####################################################################################



# Hauptfunktion zum Programmstart
def main():
    CONFIG_PATH = get_config_path()

    start = input("Zum Login y und dann ENTER drücken.   ").strip()

    if start != "y":
        print(" -> Programm wird beendet")
        sys.exit()

    CONFIG_PATH = startup(CONFIG_PATH)

    netzwerkEmpfMain(CONFIG_PATH)

    WHO(CONFIG_PATH)

    print("Wilkommen! Was moechtest Du tun?")

    while True:
        zeige_menue()
        wahl = input("Gib eine Zahl ein (1-5): ").strip()

        if wahl == "1":
            WHO(CONFIG_PATH)
        elif wahl == "2":
            nachrichtSenden(CONFIG_PATH)
        elif wahl == "3":
            print(" -> Programm wird beendet")
            sys.exit()
        elif wahl == "4":
            empfaenger = input("Name des Kontakts: ")
            empfaenger.lower()
            kontaktAnlegen(empfaenger)
        elif wahl == "5":
            kontakteZeigen()
        else:
            print("Ungueltige Eingabe. Bitte 1, 2, 3, 4 oder 5 eingeben.")


# Einstiegspunkt
if __name__ == "__main__":
    main()
