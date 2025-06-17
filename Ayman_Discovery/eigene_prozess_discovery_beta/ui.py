import subprocess
import sys
import os
import time
import threading
import toml

from ui import start_cli
from config_utility import config_startup, get_contacts_path


def start_discovery_daemon():
    """Startet discovery_daemon.py als eigenen Prozess."""
    return subprocess.Popen([sys.executable, "discovery_daemon.py"])

def main():
    print("[MAIN] Starte System...")

    # Konfiguration laden
    config_path, auto_mode, handle, port, whoisport, ip, broadcast_ip = config_startup()
    contacts_path = get_contacts_path()

    print("[MAIN] Starte Discovery-Dienst als externen Prozess...")
    discovery_proc = start_discovery_daemon()
    time.sleep(1)  # kleine Wartezeit zur Initialisierung

    try:
        print("[MAIN] Starte CLI...")
        start_cli(
            auto=auto_mode,
            handle=handle,
            port=port,
            whoisport=whoisport,
            config_path=config_path,
            contacts_path=contacts_path,
            broadcast_ip=broadcast_ip
        )
        if auto_mode:
            print("[MAIN] Automodus abgeschlossen.")

    except KeyboardInterrupt:
        print("\n[MAIN] Abbruch durch Benutzer.")
    finally:
        print("[MAIN] Beende Discovery-Dienst...")
        discovery_proc.terminate()
        discovery_proc.wait(timeout=2)
        print("[MAIN] Discovery-Dienst gestoppt.")

if __name__ == "__main__":
    main()
