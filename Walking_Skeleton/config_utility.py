# config_utility.py

import os               # Für Dateipfade
import getpass           # Für Benutzername
import toml              # Für TOML-Dateien
import socket            # Für IP-Ermittlung

# ---------------------------------------------------------
# 1) Pfad zur benutzerspezifischen Konfigurationsdatei
# ---------------------------------------------------------
def get_config_path():
    """
    Gibt den Pfad zur Config-Datei im Verzeichnis ~/.bsrnchat zurück.
    Jede Datei heißt config_<username>.toml.
    """
    username = getpass.getuser()  # Aktueller Nutzer
    config_dir = os.path.expanduser("~/.bsrnchat")  # Verzeichnis im Home
    os.makedirs(config_dir, exist_ok=True)  # Erstelle Ordner, falls er fehlt
    return os.path.join(config_dir, f"config_{username}.toml")

# Einmalig ermittelter Pfad zur Config
CONFIG_PATH = get_config_path()

# ---------------------------------------------------------
# 2) IP- und Broadcast-Adresse (/24-Netz) ermitteln
# ---------------------------------------------------------
def ermittle_ip_und_broadcast():
    """
    Bestimmt die lokale IP und die Broadcast-Adresse für das /24-Subnetz.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))  # Dummy-Connect, um Interface zu wählen
    ip = s.getsockname()[0]
    s.close()
    broadcast = ip.rsplit('.', 1)[0] + '.255'
    return ip, broadcast

# ---------------------------------------------------------
# 3) Login-Daten-Helper für CLI
# ---------------------------------------------------------
def datenAufnehmen():
    """
    Fragt Name, Port und Willkommensnachricht ab;
    ermittelt IP und Broadcast automatisch.
    """
    ip, ipnetz = ermittle_ip_und_broadcast()
    print(f"[DEBUG] Lokale IP = {ip}, Broadcast = {ipnetz}")
    return {
        'name':  input("Gib Deinen Namen ein: ").strip().lower(),
        'port':  input("Gib Deine Portnummer ein: ").strip(),
        'ip':    ip,
        'hallo': input("Gib Deine Willkommensnachricht ein: ").strip(),
        'ipnetz': ipnetz
    }

# ---------------------------------------------------------
# 4) Config schreiben/aktualisieren
# ---------------------------------------------------------
def inConfigSchreiben(login_daten):
    """
    Schreibt oder aktualisiert die Sektion 'login_daten' in der Config.
    """
    try:
        try:
            with open(CONFIG_PATH, 'r') as f:
                cfg = toml.load(f)
        except FileNotFoundError:
            cfg = {}
        cfg['login_daten'] = login_daten
        with open(CONFIG_PATH, 'w') as f:
            toml.dump(cfg, f)
        print("Config-Datei wurde aktualisiert.")
    except Exception as e:
        print("Fehler beim Schreiben der Config-Datei:", e)

# ---------------------------------------------------------
# 5) Config anzeigen
# ---------------------------------------------------------
def zeigeConfig():
    """
    Zeigt die aktuell gespeicherten Login-Daten aus der Config an.
    """
    try:
        with open(CONFIG_PATH, 'r') as f:
            cfg = toml.load(f)
        login = cfg.get('login_daten', {})
        print(login.get('name', ''))
        print(login.get('port', ''))
        print(login.get('ip', ''))
        print(login.get('hallo', ''))
    except Exception as e:
        print("Fehler beim Lesen der Config-Datei:", e)
