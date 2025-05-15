# discoveryANSATZ.py

import toml
from Netzwerk_Kommunikation.sender import discoveryWHO, MSG


# Abfrage der Benutzerdaten zum Befüllen der Hashmap
def datenAufnehmen():
    login_daten = {}

    login_daten['name']   = input("Gib Deinen Namen ein: ").strip()
    login_daten['port']   = input("Gib deine Portnummer ein: ").strip()
    login_daten['ip']     = "localhost"  # Platzhalter – später evtl. durch socket.gethostbyname(...) ersetzen
    login_daten['hallo']  = input("Gib eine Automatische Wilkommensbotschaft fuer den Broadcast ins Netz ein: ").strip()

    return login_daten


# Schreiben/Updaten der login_daten in benutzerspezifischer Konfigurationsdatei
def inConfigSchreiben(login_daten, config_path):
    try:
        try:
            with open(config_path, 'r') as f:
                config = toml.load(f)
        except FileNotFoundError:
            config = {}

        config['login_daten'] = login_daten

        with open(config_path, 'w') as f:
            toml.dump(config, f)

        print("Config-Datei wurde aktualisiert.")

    except Exception as e:
        print("Fehler beim Schreiben in die Config-Datei:", e)


# Anzeigen der gespeicherten login_daten
def zeigeConfig(config_path):
    try:
        with open(config_path, 'r') as f:
            config = toml.load(f)

        login = config.get('login_daten', {})
        print(login.get('name', ''))
        print(login.get('port', ''))
        print(login.get('ip', ''))
        print(login.get('hallo', ''))

    except Exception as e:
        print("Fehler beim Lesen der Config-Datei:", e)


# WHO-Befehl senden
def WHO():
    print("-> WHO: Teilnehmer werden gesucht....")
    discoveryWHO()


# Nachricht an bestimmten Empfänger senden
def nachrichtSenden(config_path):
    empfaenger = input("Empfaenger: ")
    MSG(empfaenger, config_path)
