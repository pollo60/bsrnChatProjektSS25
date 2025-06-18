import toml
import sys
import os
import getpass
import socket
import ipaddress

# -------------------------------------
# IP & Netzwerkerkennung
# -------------------------------------

def ermittle_ip_und_broadcast():
    """Ermittelt lokale IP und zugehörige Broadcast-Adresse (Subnetz /24)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # Verbindung zu Google DNS simulieren
            ip = s.getsockname()[0]
        net = ipaddress.ip_network(ip + '/24', strict=False)
        return ip, str(net.broadcast_address), 1111
    except Exception as e:
        print(f"[FEHLER] IP-Ermittlung fehlgeschlagen: {e}")
        return "127.0.0.1", "255.255.255.255", 1111

def validate_port(port):
    """Prüft, ob der Port im gültigen Bereich liegt."""
    try:
        port = int(port)
        if not (0 < port <= 65535):
            raise ValueError
        return port
    except Exception:
        print(f"[FEHLER] Ungültiger Port: {port}")
        sys.exit(1)

# -------------------------------------
# Konfigurationslogik
# -------------------------------------

def config_startup():
    """Lädt Konfiguration aus Datei oder legt neue an."""
    auto_mode = "--auto" in sys.argv
    using_custom_config = len(sys.argv) > 1 and not sys.argv[1].startswith("--")

    if using_custom_config:
        config_path = sys.argv[1]
        print(f"[DEBUG] Verwende externe Konfigurationsdatei: {config_path}")
        try:
            with open(config_path, 'r', encoding="utf-8") as f:
                config = toml.load(f)
        except Exception as e:
            print(f"[FEHLER] Konnte Datei nicht laden: {e}")
            sys.exit(1)

        data = config.get("login_daten", config)
        handle = data.get("name", config.get("handle", "Unbekannt"))
        port = validate_port(data.get("port", config.get("port", 0)))
        whoisport = int(data.get("whoisport", config.get("whoisport", 1111)))
        ip, broadcast_ip, _ = ermittle_ip_und_broadcast()
        return config_path, auto_mode, handle, port, whoisport, ip, broadcast_ip

    # Lokale Datei verwenden (z. B. ~/.bsrnchat/config_USERNAME.toml)
    username = getpass.getuser()
    config_dir = os.path.expanduser("~/.bsrnchat")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, f"config_{username}.toml")

    if not os.path.exists(config_path):
        print("[INFO] Keine Konfiguration vorhanden. Neue wird erstellt.")
        login_daten = datenAufnehmen()
        inConfigSchreiben(login_daten, config_path)
    else:
        try:
            with open(config_path, "r") as f:
                config = toml.load(f)
            login_daten = config.get("login_daten")
            if not login_daten:
                raise ValueError("[login_daten] fehlt oder leer.")
        except Exception as e:
            print(f"[WARNUNG] Ungültige Konfigurationsdatei: {e}")
            login_daten = datenAufnehmen()

        ip, broadcast_ip, whoisport = ermittle_ip_und_broadcast()
        login_daten.update({"ip": ip, "ipnetz": broadcast_ip, "whoisport": whoisport})
        inConfigSchreiben(login_daten, config_path)

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
    """Speichert Login-Daten in eine TOML-Datei."""
    try:
        config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = toml.load(f)
        config['login_daten'] = login_daten
        with open(config_path, 'w') as f:
            toml.dump(config, f)
        print("[DEBUG] Konfiguration gespeichert.")
    except Exception as e:
        print(f"[FEHLER] Konnte Konfiguration nicht speichern: {e}")

def configAnzeigen(config_path):
    """Zeigt die gespeicherte Konfigurationsdatei an."""
    try:
        with open(config_path, 'r') as f:
            config = toml.load(f)
            print(toml.dumps(config))
    except FileNotFoundError:
        print(f"Datei '{config_path}' nicht gefunden.")

# -------------------------------------
# Kontakte
# -------------------------------------

def get_contacts_path():
    """Pfad zur Kontaktdatei des Nutzers."""
    username = getpass.getuser()
    contacts_dir = os.path.expanduser("~/.bsrnchat")
    os.makedirs(contacts_dir, exist_ok=True)
    return os.path.join(contacts_dir, f"contacts_{username}.toml")

def check_for_contact_list(contacts_path):
    """Stellt sicher, dass eine gültige Kontaktdatei existiert."""
    if not os.path.exists(contacts_path):
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
            with open(contacts_path, "w") as f:
                f.write("[kontakte]\n")

def kontaktAnlegen(empfaenger, contacts_path):
    """Fügt einen Kontakt hinzu (manuell durch Eingabe)."""
    try:
        with open(contacts_path, 'r') as f:
            contacts = toml.load(f)
    except FileNotFoundError:
        contacts = {"kontakte": {}}

    contacts.setdefault("kontakte", {})
    name = empfaenger.strip()
    contacts["kontakte"][name] = {
        "ziel_name": name,
        "ziel_port": input("Port: ").strip(),
        "ziel_ip": input("IP: ").strip()
    }

    with open(contacts_path, 'w') as f:
        toml.dump(contacts, f)

    print("Kontakt gespeichert ✅")

def kontakteZeigen(contacts_path):
    """Gibt alle Kontakte im Terminal aus."""
    try:
        with open(contacts_path, 'r') as f:
            contacts = toml.load(f)
            print(toml.dumps(contacts))
    except FileNotFoundError:
        print(f"Datei '{contacts_path}' nicht gefunden.")
