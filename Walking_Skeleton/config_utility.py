import os
import getpass
import toml
import socket

def get_config_path():
    username = getpass.getuser()
    config_dir = os.path.expanduser("~/.bsrnchat")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, f"config_{username}.toml")

CONFIG_PATH = get_config_path()

def ermittle_ip_und_broadcast():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    broadcast = ip.rsplit('.', 1)[0] + '.255'
    return ip, broadcast

def datenAufnehmen():
    ip, ipnetz = ermittle_ip_und_broadcast()
    print(f"[DEBUG] Lokale IP = {ip}, Broadcast = {ipnetz}")
    return {
        'name':  input("Gib Deinen Namen ein: ").strip().lower(),
        'port':  input("Gib Deine Portnummer ein: ").strip(),
        'ip':    ip,
        'hallo': input("Gib Deine Willkommensnachricht ein: ").strip(),
        'ipnetz': ipnetz
    }

def inConfigSchreiben(login_daten, config_path=None):
    if config_path is None:
        config_path = CONFIG_PATH
        
    try:
        try:
            with open(config_path, 'r') as f:
                cfg = toml.load(f)
        except FileNotFoundError:
            cfg = {}
        cfg['login_daten'] = login_daten
        with open(config_path, 'w') as f:
            toml.dump(cfg, f)
        print("Config-Datei wurde aktualisiert.")
    except Exception as e:
        print("Fehler beim Schreiben der Config-Datei:", e)

def zeigeConfig():
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