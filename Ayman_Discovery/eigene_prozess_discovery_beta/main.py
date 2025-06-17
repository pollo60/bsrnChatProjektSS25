
import subprocess
import sys
import os
from config_utility import config_startup, get_contacts_path
from ui import start_cli

def main():
    print("[DEBUG] main.py gestartet.")
    config_path, auto_mode, handle, port, whoisport, ip, broadcast_ip = config_startup()
    contacts_path = get_contacts_path()

    print("[DEBUG] Starte discovery_daemon.py als Subprozess...")
    subprocess.Popen([sys.executable, "discovery_daemon.py", config_path])

    try:
        start_cli(auto=auto_mode, handle=handle, port=port, whoisport=whoisport,
                  config_path=config_path, contacts_path=contacts_path, broadcast_ip=broadcast_ip)
    except KeyboardInterrupt:
        print("Beendet durch Benutzer.")
    finally:
        print("Anwendung beendet.")

if __name__ == "__main__":
    main()
