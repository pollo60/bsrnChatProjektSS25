import toml # Liest und schreibt TOML-Konfigurationsdatein ein
import sys # Greift auf Systemfunktionen und cd Argumente zu
import os # Orderstrukture und Dateupfade 
import getpass # Ermittelt aktuellen Benutzernamen
import socket # Ermöglicht Netzwerkverbindung
import ipaddress # Für IP-Adressen und Netzwerke

# -------------------------------------
# IP & Netzwerkerkennung
# -------------------------------------

def ermittle_ip_und_broadcast():
    """
     @brief Überprüft die aktuelle Broadcast und IP-Adresse im Netzwerk
     Simulierteine Verbindung zu Googles DNS um herrauszufinden welche IP-Adresse im Netzwerk zugewiesen ist.
     Berechnet das Subnetz um eine Broadcast zu ermitteln
     @return tuple IP-Adresse und Breadcast Adresse als String
    """
    try:
        #Erstellt UDP-Socket tepmporär um IP zu ermittlen
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # Verbindung zu Google DNS simulieren
            ip = s.getsockname()[0] # Eigene lokale IP-Adresse auslesen
            # Erzeuge eine IP-Adresse mit Netzwerkmaske /24
        net = ipaddress.ip_network(ip + '/24', strict=False)
        # @retrun IP. berechnet Brodcast Adresse und gibt WHOIS-Port zurück
        return ip, str(net.broadcast_address), 1111
    except Exception as e:
        # Fehlermeldung dalls kein Netzwerk verfügbar ist 
        print(f"[FEHLER] IP-Ermittlung fehlgeschlagen: {e}")
        return "127.0.0.1", "255.255.255.255", 1111 # return auf Localhost und Broadcast

def validate_port(port):
    """"
     @brief Überprüft ob ein Portwert gültig ist
     
    Stellt sicher, dass der gegebene Port gültig ist in dem es den übergebenen Port in eine Zahl zwischen 
    0 und 65535 wandelt. 
    Falls Port ungültig, wird das Programm beendet
     @param port Portnummer als Zahl oder String
     @return int als Gültige Portnummer
     """
    

    """Prüft, ob der Port im gültigen Bereich liegt."""
    try:
        port = int(port) # Wandelt Port in Zahl um
        if not (0 < port <= 65535): # Ports müssen zwischen 0 und 65535 liegen
            raise ValueError
        return port # Gültiger Port wird erkannt und zurückgegeben
    except Exception:
        # Port ungültig, daher Fehlermeldung
        print(f"[FEHLER] Ungültiger Port: {port}")
        sys.exit(1) # Beende das Program mit dem Fehlercode

# -------------------------------------
# Konfigurationslogik
# -------------------------------------

def config_startup():
    """"
     @brief Läd Konfig Datei oder erstellt eine neue falls nicht vorhanden
    
     Diese Funktion läd beim Programmstart Benutzdaten aus den jeweiligen TOML-Konfig Dateien. 
     Es werden bereits bestehende Dateien geladen oder neue erstellt.
    
     Prüfung des Auto Modus was eine manuelle Eingabe unterdrücken könnte
     @return Pfad zur Konfig Datei, Benutzname, Port, WHOIS-Port. IP-Adresse und Broadcast-Adresse
"""
    """Lädt Konfiguration aus Datei oder legt neue an."""
    auto_mode = "--auto" in sys.argv # Prüft ob --auto als Agument gültig ist
    using_custom_config = len(sys.argv) > 1 and not sys.argv[1].startswith("--") # Prüft ob eine externe Datei übergeben wurde

    if using_custom_config:
        # Manuelle Eingabe eines Konfigpfades
        config_path = sys.argv[1]
        print(f"[DEBUG] Verwende externe Konfigurationsdatei: {config_path}")
        try:
            with open(config_path, 'r', encoding="utf-8") as f:
                config = toml.load(f) # Versucht Konfig TOML Datei zu laden
        except Exception as e:
            print(f"[FEHLER] Konnte Datei nicht laden: {e}")
            sys.exit(1)

        data = config.get("login_daten", config) # Falls login daten nicht vorhanden sind, benutze Root
        handle = data.get("name", config.get("handle", "Unbekannt"))
        port = validate_port(data.get("port", config.get("port", 0)))
        whoisport = int(data.get("whoisport", config.get("whoisport", 1111)))
        ip, broadcast_ip, _ = ermittle_ip_und_broadcast()
        return config_path, auto_mode, handle, port, whoisport, ip, broadcast_ip

    # Lokale Datei verwenden (z. B. ~/.bsrnchat/config_USERNAME.toml)
    username = getpass.getuser() # Aktuellen Benutzer ermitteln
    config_dir = os.path.expanduser("~/.bsrnchat") # Konfig Ordner im main Verzeichnis
    os.makedirs(config_dir, exist_ok=True) # Ordner erstellen falls nicht vorhanden
    config_path = os.path.join(config_dir, f"config_{username}.toml") # Kompletter Pfad zur Datei

    if not os.path.exists(config_path):
        # Neue Datei anlegen falls noch keine existiert
        print("[INFO] Keine Konfiguration vorhanden. Neue wird erstellt.")
        login_daten = datenAufnehmen() # Benutzerdaten abfragen
        inConfigSchreiben(login_daten, config_path) # Neue Datei erstellen
    else:
        try:
            with open(config_path, "r") as f:
                config = toml.load(f) # Bestehende TOML Datei laden
            login_daten = config.get("login_daten") # Login daten auslesen
            if not login_daten:
                raise ValueError("[login_daten] fehlt oder leer.") # Fehler anzeigen wenn leer
        except Exception as e:
            print(f"[WARNUNG] Ungültige Konfigurationsdatei: {e}")
            login_daten = datenAufnehmen() # Neue Eingabe anfordern
            
            # Netzwerkdaten aktualiesieren
        ip, broadcast_ip, whoisport = ermittle_ip_und_broadcast()
        login_daten.update({"ip": ip, "ipnetz": broadcast_ip, "whoisport": whoisport})
        inConfigSchreiben(login_daten, config_path) # Datei aktualiesieren

    # Daten auslesen und return
    handle = login_daten.get("name", "Unbekannt")
    port = validate_port(login_daten.get("port", 0))
    whoisport = int(login_daten.get("whoisport", 1111))
    ip = login_daten.get("ip", "127.0.0.1")
    broadcast_ip = login_daten.get("ipnetz", "255.255.255.255")
    return config_path, auto_mode, handle, port, whoisport, ip, broadcast_ip

    #debug ausgabe
    print(f"[DEBUG] config_startup geladen: handle={handle}, port={port}, whoisport={whoisport}, ip={ip}, broadcast_ip={broadcast_ip}")
    return config_path, auto_mode, handle, port, whoisport, ip, broadcast_ip

def datenAufnehmen():
    """Benutzerdaten vom Terminal abfragen und IP-Daten ergänzen."""
    ip, ipnetz, whoisport = ermittle_ip_und_broadcast()
    print(f"[DEBUG] Lokale IP = {ip}, Broadcast = {ipnetz}")
    return {
        "name": input("Name: ").strip().lower(),
        "port": input("Portnummer: ").strip(),
        "hallo": input("Willkommensbotschaft: ").strip(),
        "ip": ip,
        "ipnetz": ipnetz,
        "whoisport": whoisport
    }

def inConfigSchreiben(login_daten, config_path):
    """"
     @brief Speichert Login Daten in TOML Datei
    @param login Daten dict mit Benutzer
    @param config path zur Konfig Datei
    """

    """Speichert Login-Daten in eine TOML-Datei."""
    try:
        config = {}
        if os.path.exists(config_path):
            # Bestehende config laden
            with open(config_path, 'r') as f:
                config = toml.load(f)
        config['login_daten'] = login_daten # Block aktualiesieren oder neu starten
        with open(config_path, 'w') as f:
            toml.dump(config, f) # Datei speichern
        print("[DEBUG] Konfiguration gespeichert.")
    except Exception as e:
        print(f"[FEHLER] Konnte Konfiguration nicht speichern: {e}")

def configAnzeigen(config_path):
    """"
     @brief zeigt Konfig Datei im Terminal an
     @param config path Pfad zur Datei
    """
    
    try:
        with open(config_path, 'r') as f:
            config = toml.load(f)
            print(toml.dumps(config)) # Inhalt formatiert wiedergeben
    except FileNotFoundError:
        print(f"Datei '{config_path}' nicht gefunden.")

# -------------------------------------
# Kontakte
# -------------------------------------

def get_contacts_path():
    """"
     @brief zeigt Kontakte des aktuellen Benutzeres an
     @return str Pfad zu Kontaktdatei
    """
    
    username = getpass.getuser()
    contacts_dir = os.path.expanduser("~/.bsrnchat")
    os.makedirs(contacts_dir, exist_ok=True)
    return os.path.join(contacts_dir, f"contacts_{username}.toml")

def check_for_contact_list(contacts_path):
    """"
     @brief Prüft ob die Kontakte existieren
     @param contacts path zur Kontakt Datei
    """
    
    if not os.path.exists(contacts_path):
        # Erstellt neue Datei falls keine existiert
        print(f"[INFO] Kontaktliste wird angelegt: {contacts_path}")
        with open(contacts_path, "w") as f:
            f.write("[kontakte]\n")
    else:
        try:
            with open(contacts_path, "r") as f:
                data = toml.loads(f.read().strip())
                if "kontakte" not in data:
                    raise ValueError
        except Exception:
            # Falls Datei ungültig wird der prozess neu gestartet
            with open(contacts_path, "w") as f:
                f.write("[kontakte]\n")

def kontaktAnlegen(empfaenger, contacts_path):
    """"
    @brief Fügt Kontakte zu Kontaktliste hinzu
    @param Name von neuen Kontakt
    @param contacts path zur Kontaktdatei
    """
   
    try:
        with open(contacts_path, 'r') as f:
            contacts = toml.load(f)
    except FileNotFoundError:
        contacts = {"kontakte": {}} # Neue Datei vorbereiten

    contacts.setdefault("kontakte", {}) # Sicherstellen, dass Kontakte existieren
    name = empfaenger.strip() # Whitespace entfernen
    contacts["kontakte"][name] = {
        "ziel_name": name,
        "ziel_port": input("Port: ").strip(), # Port manuell  eingeben
        "ziel_ip": input("IP: ").strip() # IP-Adresse eingeben
    }

    with open(contacts_path, 'w') as f:
        toml.dump(contacts, f) # Kontaktänderungen Speichern

    print("Kontakt gespeichert ✅")

def kontakteZeigen(contacts_path):
    """"
     @brief Zeiegt gespeicherte Kontake im Terminal an
     @param contact path zur Konfi Datei
    """
    """Gibt alle Kontakte im Terminal aus."""
    try:
        with open(contacts_path, 'r') as f:
            contacts = toml.load(f)
            print(toml.dumps(contacts)) # Ausgabe der TOML Kontakt Dateien
    except FileNotFoundError:
        print(f"Datei '{contacts_path}' nicht gefunden.")
