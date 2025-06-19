# main.py
from multiprocessing import Process, Queue
from config_utility import config_startup, get_contacts_path
from ui import start_cli
from discovery_daemon_queue import run_discovery
from message_listener_queue import listen_for_messages
from network_process import send_slcp_broadcast

def main():

    """
    @brief Huaptprozess des Gesamten Progamms. Started alle Prozesse 

     - Läd Die Konfigurationsdatein und Kontaktlisten
     - Initialisiert IPC für Kommunikation zwischen Clients/Prozessen
     - Startet : Discovery, Broadcast und Nachichtenempänger
     - Kommandozeile wird ausgeführt
     - Beedndet Prozesse mit Strg+C

"""
    config_path, auto_mode, handle, port, whoisport, ip, broadcast_ip = config_startup()
    contacts_path = get_contacts_path()
    # Queue für Netzwerkprozess
    input_queue = Queue()   # Befehle von UI an Netzwerkprozess
    output_queue = Queue()  # Netzwerk-Nachrichten an UI

    # Erstellt und started Discovery Process
    discovery_proc = Process(target=run_discovery, args=(config_path, output_queue))
    # Erstellt und startet Nachihchten Prozess
    receiver_proc = Process(target=listen_for_messages, args=(port, output_queue))
    # Erstellt und started Broadcast
    network_proc = Process(target=send_slcp_broadcast, args=(input_queue, whoisport, broadcast_ip))

    discovery_proc.start()
    receiver_proc.start()
    network_proc.start()

    print("[DEBUG] Prozesse gestartet")

    try:
        #Startet CLI
        start_cli(
            auto=auto_mode,
            handle=handle,
            port=port,
            whoisport=whoisport,
            config_path=config_path,
            contacts_path=contacts_path,
            broadcast_ip=broadcast_ip,
            message_queue=output_queue,
            input_queue=input_queue
        )
    except KeyboardInterrupt:
        # Benutzer hat das Programm Beendet
        print("[ABBRUCH] Strg+C erkannt")
    finally:
        # Prozesse beenden und Ressourcen freigeben
        discovery_proc.terminate()
        receiver_proc.terminate()
        network_proc.terminate()

        discovery_proc.join()
        receiver_proc.join()
        network_proc.join()
        print("[ENDE] Prozesse gestoppt.")

if __name__ == "__main__":
    """
    @brief Startpunkt

    Führt main Funktion aus

    """
    main()
