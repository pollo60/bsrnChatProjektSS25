# cli.py

import sys
import getpass
import os
import toml

from discoveryANSATZ import datenAufnehmen, inConfigSchreiben, zeigeConfig, WHO, MSG, nachrichtSenden
from Netzwerk_Kommunikation.empfaenger import netzwerkEmpfMain, discoveryWHO


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


# Funktion fuer den Start des Programms mit Login
def startup():
    if not os.path.exists(CONFIG_PATH):
        print("Erzeuge neue Konfiguration...")
        daten = datenAufnehmen()
        inConfigSchreiben(daten, CONFIG_PATH)
    else:
        print(f"Config-Datei '{CONFIG_PATH}' gefunden.")
        zeigeConfig(CONFIG_PATH)


# Funktion zum Anlegen eines neuen Kontakts
def kontaktAnlegen(empfaenger):
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
    except FileNotFoundError:
        config = {}

    name = input("Gib den Namen ein: ").strip()
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


# Hauptfunktion zum Programmstart
def main():
    start = input("Zum Login y und dann ENTER drücken.   ").strip()

    if start == "y":
        startup()
    else:
        print(" -> Programm wird beendet")
        sys.exit()

    discoveryWHO()
    netzwerkEmpfMain()

    print("Wilkommen! Was moechtest Du tun?")

    while True:
        zeige_menue()
        wahl = input("Gib eine Zahl ein (1-4): ").strip()

        if wahl == "1":
            WHO(CONFIG_PATH)
        elif wahl == "2":
            nachrichtSenden(CONFIG_PATH)
        elif wahl == "3":
            print(" -> Programm wird beendet")
            sys.exit()
        elif wahl == "4":
            empfaenger = input("Name des Kontakts: ")
            kontaktAnlegen(empfaenger)
        else:
            print("Ungueltige Eingabe. Bitte 1, 2, 3 oder 4 eingeben.")


# Einstiegspunkt
if __name__ == "__main__":
    main()
