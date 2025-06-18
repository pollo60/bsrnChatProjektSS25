# main.py
from message_listener import listen_for_messages
import threading
import sys
import multiprocessing
from config_utility import config_startup, get_contacts_path
from ui import start_cli
from discovery_daemon import run_discovery


def main():
    config_path, auto_mode, handle, port, whoisport, ip, broadcast_ip = config_startup()
    contacts_path = get_contacts_path()

    # Starte Discovery als separaten Prozess
    discovery_proc = multiprocessing.Process(
        target=run_discovery,
        args=(config_path,)
    )
    discovery_proc.start()
    print("[DEBUG] Discovery-Prozess gestartet")

    # Startet listeners für Nachrichten
    receiver_thread = threading.Thread(target=listen_for_messages, args=(port,), daemon=True)
    receiver_thread.start()
    print("Debug:listener gestartet ")

    try:
        start_cli(
            auto=auto_mode,
            handle=handle,
            port=port,
            whoisport=whoisport,
            config_path=config_path,
            contacts_path=contacts_path,
            broadcast_ip=broadcast_ip
        )
    except KeyboardInterrupt:
        print("[ABBRUCH] Benutzer hat mit Strg+C beendet.")
    finally:
        discovery_proc.terminate()
        discovery_proc.join()
        print("[ENDE] Discovery-Prozess gestoppt.")

if __name__ == "__main__":
    main()
