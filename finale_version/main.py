## main.py
import multiprocessing
import sys
import toml
from discovery_process import discovery_process
from network_process import network_process
from ui_process import ui_process

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")  # Wichtig für Windows

    # Konfigurationsdatei aus Argumenten lesen oder Standard verwenden
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.toml"

    manager = multiprocessing.Manager()
    kontakte = manager.dict()

    ui_queue = multiprocessing.Queue()
    disc_queue = multiprocessing.Queue()
    net_queue = multiprocessing.Queue()

    p1 = multiprocessing.Process(target=discovery_process, args=(ui_queue, disc_queue, config_path, kontakte))
    p2 = multiprocessing.Process(target=network_process, args=(ui_queue, net_queue, config_path, kontakte))

    p1.start()
    p2.start()

    # UI läuft im Hauptprozess (für stdin-Kompatibilität unter Windows)
    try:
        ui_process(ui_queue, disc_queue, net_queue, config_path)
    except KeyboardInterrupt:
        print("Programm beendet")

    p1.terminate()
    p2.terminate()
    p1.join()
    p2.join()