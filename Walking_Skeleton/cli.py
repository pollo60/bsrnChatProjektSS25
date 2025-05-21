import sys               # Für Exit-Funktionen
import os                # Für Dateisystem-Operationen
import toml              # Für TOML-Konfiguration

from discovery import WHO, nachrichtSenden, unicastWHO, DiscoveryService  # Importieren der Discovery-Funktionen
from network import ermittle_ip_und_broadcast                             # Importieren der Netzwerkfunktionen
from config_utility import get_config_path, datenAufnehmen, inConfigSchreiben, zeigeConfig  # Importieren der Konfigurations-Funktionen

CONFIG_PATH = get_config_path()  # Ermitteln des Pfads zur Konfigurationsdatei

discovery_service = None  # Globale Variable für den Discovery Service

# Funktion zur Anzeige des Menüs
def zeige_menue():
    # Übersichtliche Ausgabe der verfügbaren Optionen im Hauptmenü
    print("\n Menue:")
    print("1: \t WHO - Zeige Teilnehmer")             # Option zur Anzeige aller aktuell verbundenen Clients
    print("2: \t MSG - Nachricht senden")             # Option zum Senden einer Nachricht an andere Teilnehmer
    print("3: \t unicastWHO")                         # Option zur gezielten WHO-Anfrage an einen bestimmten Client
    print("4: \t Kontakt anlegen")                    # Option zum Hinzufügen eines neuen Kontakts zur Kontaktliste
    print("5: \t Kontakte anzeigen")                  # Option zur Anzeige aller gespeicherten Kontakte
    print("6: \t Discovery Service starten")          # Option zum Starten des Discovery Service
    print("7: \t Discovery Service stoppen")          # Option zum Stoppen des Discovery Service
    print("8: \t EXIT - Beenden")                     # Option zum Beenden des Programms

# Funktion für den Start des Programms mit Login
def startup(CONFIG_PATH):
    # Prüfen, ob die Konfigurationsdatei bereits existiert
    if not os.path.exists(CONFIG_PATH):
        print("Erzeuge neue Konfiguration...")  # Hinweis für den Nutzer
        daten = datenAufnehmen()                # Aufruf zur Eingabe der benötigten Login-Daten
        inConfigSchreiben(daten, CONFIG_PATH)   # Speichern der Daten in der neuen Konfigurationsdatei
    else:
        print(f"Config-Datei '{CONFIG_PATH}' gefunden.")  # Info: bestehende Konfiguration wurde erkannt
        zeigeConfig()                          # Anzeige der aktuellen Konfigurationsdaten
        configAendern = input("Moechtest Du Deine Config-Datei bearbeiten? (y/n) ").strip().lower()
        if configAendern == "y":
            login_daten = datenAufnehmen()                # Neue Eingabe der Login-Daten
            inConfigSchreiben(login_daten)   # Überschreiben der bisherigen Konfiguration

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
    port = input("Gib deine Portnummer ein: ").strip()  # Eingabe der Ziel-Portnummer durch den Benutzer
    ip = input("Gib deine IP ein: ").strip()            # Eingabe der Ziel-IP-Adresse durch den Benutzer

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

# ---------------------------------------------------------
# Login-Daten abfragen: Name, Port, Willkommensnachricht FUER CLI
# ---------------------------------------------------------
def datenAufnehmen():
    ip, ipnetz = ermittle_ip_und_broadcast()
    print(f"[DEBUG] Lokale IP = {ip}, Broadcast = {ipnetz}")
    name = input("Gib Deinen Namen ein: ").strip().lower()
    port = input("Gib Deine Portnummer ein: ").strip()
    hallo = input("Gib eine automatische Willkommensnachricht ein: ").strip()
    return {
        'name': name,
        'port': port,
        'ip': ip,
        'hallo': hallo,
        'ipnetz': ipnetz
    }

# ---------------------------------------------------------
# Login-Daten in Config schreiben oder updaten FUER CLI
# ---------------------------------------------------------
def inConfigSchreiben(login_daten):
    try:
        # Bestehende Config einlesen, falls vorhanden
        try:
            with open(CONFIG_PATH, 'r') as f:
                cfg = toml.load(f)
        except FileNotFoundError:
            cfg = {}
        # Schreibe unter 'login_daten'
        cfg['login_daten'] = login_daten
        with open(CONFIG_PATH, 'w') as f:
            toml.dump(cfg, f)
        print("Config-Datei wurde aktualisiert.")
    except Exception as e:
        print("Fehler beim Schreiben der Config-Datei:", e)

# ---------------------------------------------------------
# Funktionen zum Verwalten des Discovery Service
# ---------------------------------------------------------

# Funktion zum Starten des Discovery Service
def start_discovery_service():
    global discovery_service  # Zugriff auf die globale Variable
    if discovery_service is not None:
        print("Discovery Service laeuft bereits!")  # Hinweis, dass der Service schon läuft
        return
    
    try:
        discovery_service = DiscoveryService()  # Erzeugung einer neuen Instanz
        discovery_service.start()               # Starten des Services
        print("Discovery Service gestartet.")   # Bestätigung an den Benutzer
    except Exception as e:
        print("Fehler beim Starten des Discovery Service:", e)  # Fehlerbehandlung
        discovery_service = None  # Variable zurücksetzen bei Fehler

# Funktion zum Stoppen des Discovery Service
def stop_discovery_service():
    global discovery_service  # Zugriff auf die globale Variable
    if discovery_service is None:
        print("Discovery Service ist nicht aktiv.")  # Hinweis, dass kein Service läuft
        return
    
    try:
        discovery_service.stop()  # Ordentliches Beenden des Services
        discovery_service = None  # Variable zurücksetzen
        print("Discovery Service gestoppt.")    # Bestätigung an den Benutzer
    except Exception as e:
        print("Fehler beim Stoppen des Discovery Service:", e)  # Fehlerbehandlung

# ---------------------------------------------------------
# Hauptfunktion zum Programmstart
# ---------------------------------------------------------
def main():
    global CONFIG_PATH  # Zugriff auf globale Konfigurationspfad-Variable
    CONFIG_PATH = get_config_path()  # Pfad zur Konfigurationsdatei ermitteln

    start = input("Zum Login y und dann ENTER druecken.   ").strip()  # Benutzerabfrage zum Start

    if start != "y":
        print(" -> Programm wird beendet")  # Hinweis bei Abbruch
        sys.exit()                         # Beenden des Programms

    ip, ipnetz = ermittle_ip_und_broadcast()  # Netzwerkadressen ermitteln
    print(f"[DEBUG] Lokale IP = {ip}, Broadcast = {ipnetz}")  # Debug-Info ausgeben
    
    CONFIG_PATH = startup(CONFIG_PATH)     # Aufruf der Start- bzw. Loginroutine

    WHO()  # Anfängliche WHO-Anfrage zur Teilnehmerermittlung

    print("Wilkommen! Was moechtest Du tun?")  # Begrüßung und Übergang zum Menü

    # Hauptprogrammschleife
    while True:
        zeige_menue()  # Menüoptionen anzeigen
        wahl = input("Gib eine Zahl ein (1-8): ").strip()  # Benutzereingabe zur Auswahl

        if wahl == "1":
            WHO()  # Aufruf der Funktion zur Anzeige der verbundenen Teilnehmer
        elif wahl == "2":
            nachrichtSenden()  # Aufruf der Funktion zum Versenden einer Nachricht
        elif wahl == "3":
            unicastWHO()  # WHO-Anfrage gezielt an einen Kontakt senden
        elif wahl == "4":
            empfaenger = input("Name des Kontakts: ").strip().lower()  # Name des neuen Kontakts abfragen
            kontaktAnlegen(empfaenger)  # Kontakt wird angelegt
        elif wahl == "5":
            kontakteZeigen()  # Alle gespeicherten Kontakte werden angezeigt
        elif wahl == "6":
            start_discovery_service()  # Discovery Service starten
        elif wahl == "7":
            stop_discovery_service()  # Discovery Service stoppen
        elif wahl == "8":
            print(" -> Programm wird beendet")  # Hinweis zur Beendigung
            if discovery_service is not None:
                stop_discovery_service()  # Discovery Service stoppen falls aktiv
            sys.exit()  # Beenden des Programms
        else:
            # Falls keine gültige Eingabe (1–8), Hinweis zur Korrektur
            print("Ungueltige Eingabe. Bitte 1, 2, 3, 4, 5, 6, 7 oder 8 eingeben.")

# ---------------------------------------------------------
# Einstiegspunkt
# ---------------------------------------------------------
if __name__ == "__main__":
    main()  # Aufruf der Hauptfunktion nur, wenn das Skript direkt ausgeführt wird