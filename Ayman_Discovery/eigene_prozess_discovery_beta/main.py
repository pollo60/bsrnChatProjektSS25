# main.py
from multiprocessing import Process, Queue
from config_utility import config_startup, get_contacts_path
from ui import start_cli
from discovery_daemon_queue import run_discovery
from message_listener_queue import listen_for_messages

def main():
    config_path, auto_mode, handle, port, whoisport, ip, broadcast_ip = config_startup()
    contacts_path = get_contacts_path()

    queue = Queue()

    discovery_proc = Process(target=run_discovery, args=(config_path, queue))
    receiver_proc = Process(target=listen_for_messages, args=(port, queue))
    discovery_proc.start()
    receiver_proc.start()

    print("[DEBUG] Prozesse gestartet")

    try:
        start_cli(
            auto=auto_mode,
            handle=handle,
            port=port,
            whoisport=whoisport,
            config_path=config_path,
            contacts_path=contacts_path,
            broadcast_ip=broadcast_ip,
            message_queue=queue
        )
    except KeyboardInterrupt:
        print("[ABBRUCH] Strg+C erkannt")
    finally:
        discovery_proc.terminate()
        receiver_proc.terminate()
        discovery_proc.join()
        receiver_proc.join()
        print("[ENDE] Prozesse gestoppt.")

if __name__ == "__main__":
    main()
