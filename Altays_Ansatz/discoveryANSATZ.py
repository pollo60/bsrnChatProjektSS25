# discoveryANSATZ.py

import toml
import ipaddress
import socket
import threading
from Netzwerk_Kommunikation.sender import discoveryWHO, MSG


# Erreichbarkeit von teilnehmern ueberpruefen! Ping!

# Eigene IP Adresse automatisch abfragen und in Config schreiben (login_daten: ip, ipnetz)
def ermittle_ip_und_broadcast():
    try:
        # Dummy-Verbindung zur Ermittlung der aktiven Netzwerkschnittstelle
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Verbindet sich nicht wirklich
        ip = s.getsockname()[0]
        s.close()

        ipnetz = ipaddress.ip_network(ip + '/24', strict=False)
        return str(ip), str(ipnetz.broadcast_address)
    except Exception as e:
        print("Fehler bei IP-Ermittlung:", e)
        raise RuntimeError("Netzwerkverbindung erforderlich, um IP zu ermitteln.")





# Client file?
# Abfrage der Benutzerdaten zum Befüllen der Hashmap
def datenAufnehmen():

    ip, ipnetz = ermittle_ip_und_broadcast()
    login_daten = {}

    login_daten['name']   = input("Gib Deinen Namen ein: ").strip()
    login_daten['name'].lower()
    login_daten['port']   = input("Gib deine Portnummer ein: ").strip()
    login_daten['ip']     = ip # Platzhalter – später evtl. durch socket.gethostbyname(...) ersetzen
    login_daten['hallo']  = input("Gib eine Automatische Wilkommensbotschaft fuer den Broadcast ins Netz ein: ").strip()
    login_daten['ipnetz'] = ipnetz # Platzhalter

    return login_daten

# Client file?
# Schreiben/Updaten der login_daten in benutzerspezifischer Konfigurationsdatei
def inConfigSchreiben(login_daten, CONFIG_PATH):
    try:
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = toml.load(f)
        except FileNotFoundError:
            config = {}

        config['login_daten'] = login_daten

        with open(CONFIG_PATH, 'w') as f:
            toml.dump(config, f)

        print("Config-Datei wurde aktualisiert.")

    except Exception as e:
        print("Fehler beim Schreiben in die Config-Datei:", e)


# Vielleicht in CLIENT FILE?
# Anzeigen der gespeicherten login_daten
def zeigeConfig(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)

        login = config.get('login_daten', {})
        print(login.get('name', ''))
        print(login.get('port', ''))
        print(login.get('ip', ''))
        print(login.get('hallo', ''))

    except Exception as e:
        print("Fehler beim Lesen der Config-Datei:", e)


# WHO-Befehl senden
def WHO(CONFIG_PATH):
    try:
        # Konfiguration laden
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)

        port = int(config['login_daten']['port'])
        ipnetz = config['login_daten']['ipnetz']

        print("Teilnehmer werden gesucht...")

        antworten = discoveryWHO(ipnetz, port)

        neue_teilnehmer = False
        for name, ip, port in antworten:
            print(f"Antwort von {name} -> IP: {ip}, Port: {port}")
            if name not in config:
                config[name] = {
                    'ziel_ip': ip,
                    'ziel_port': port
                }
                neue_teilnehmer = True

        if neue_teilnehmer:
            with open(CONFIG_PATH, 'w') as f:
                toml.dump(config, f)
            print("Neue Teilnehmer wurden in der Config gespeichert.")
        elif not antworten:
            print("Keine Teilnehmer geantwortet.")
        else:
            print("Alle Teilnehmer bereits bekannt.")

    except Exception as e:
        print("Fehler bei discoveryWHO:", e)



# Nachricht an bestimmten Empfänger senden
def nachrichtSenden(CONFIG_PATH):
    empfaenger = input("Empfaenger: ")
    MSG(empfaenger, CONFIG_PATH)
