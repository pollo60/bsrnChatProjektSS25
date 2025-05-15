# cliANSATZ

import sys

from discoveryANSATZ import datenAufnehmen, inConfigSchreiben, zeigeConfig, WHO, MSG, nachrichtSenden
from Netzwerk_Kommunikation.empfaenger import netzwerkEmpfMain, discoveryWHO

# Funktion zur Anzeige des Menüs
def zeige_menue():
    print("\n Menue:")
    print("1: \t WHO - Zeige Teilnehmer")
    print("2: \t MSG - Nachricht senden")
    print("3: \t EXIT - Beenden")
    print("4: \t Kontakt anlegen")

# Funktion fuer den Start des Programms mit Login
def startup():
    zeigeConfig()
    login_daten = datenAufnehmen()
    inConfigSchreiben(login_daten)
    zeigeConfig()


def kontaktAnlegen(empfaenger):
    try:
        with open('configANSATZ.toml', 'r') as f:
            config = toml.load(f)
    except FileNotFoundError:
        config = {}
# config oeffnen

    name = input("Gib den Namen ein: ").strip()
    port = input("Gib die Portnummer ein: ").strip()
    ip = input("Gib die IP ein: ").strip()
# Neue Kontaktdaten aufnehmen

    config[name] = {
        'ziel_name': name,
        'ziel_port': port,
        'ziel_ip': ip
    }
# Kontaktdaten in Config speichern


    with open('configANSATZ.toml', 'w') as f:
        toml.dump(config, f)
# Config aktualisieren

    print("Config-Datei wurde aktualisiert.")

# Zur Kontrolle anzeigen
    print(config[name]['ziel_name'])
    print(config[name]['ziel_port'])
    print(config[name]['ziel_ip'])


# Hauptfunktion zum Programmstart
def main():
    start = input("Zum Login y und dann ENTER drücken.   ").strip()

    # if start == "y":
    #     startup()
       
    # else:
    #     print(" -> Programm wird beendet")
    #     sys.exit()

    discoveryWHO()         # Teilnehmer im Netz suchen
    netzwerkEmpfMain()     # Empfangsthread einmalig starten

    print("Wilkommen! Was moechtest Du tun?")

    # Menüschleife
    while True:
        zeige_menue()
        wahl = input("Gib eine Zahl ein (1-4): ").strip()

        if wahl == "1":
            WHO()
        elif wahl == "2":
            nachrichtSenden()
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