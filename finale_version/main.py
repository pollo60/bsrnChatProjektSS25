import multiprocessing  
import sys              
import toml             
import os

from discovery_process import discovery_process
from network_process import network_process
from ui_process import ui_process

if __name__ == "__main__":
    # Windows braucht spawn
    multiprocessing.set_start_method("spawn")  

    # Script-Verzeichnis ermitteln
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Config file aus args oder default
    if len(sys.argv) > 1:
        cfg_filename = sys.argv[1]
        # Wenn nur der Dateiname angegeben wird, im Script-Verzeichnis suchen
        if not os.path.dirname(cfg_filename):
            cfg_path = os.path.join(script_dir, cfg_filename)
        else:
            # Vollständiger Pfad wurde angegeben
            cfg_path = cfg_filename
    else:
        # Standard config.toml 
        cfg_path = os.path.join(script_dir, "config.toml")
    
    # Prüfen ob Config-Datei existiert
    if not os.path.exists(cfg_path):
        print(f"FEHLER: Config-Datei '{cfg_path}' nicht gefunden!")
        print("Verfügbare Config-Dateien im Script-Verzeichnis:")
        for file in os.listdir(script_dir):
            if file.endswith('.toml'):
                print(f"  - {file}")
        print(f"\nVerwendung: python {sys.argv[0]} [config-datei]")
        print("Hinweis: Wenn nur der Dateiname angegeben wird, wird im Script-Verzeichnis gesucht.")
        sys.exit(1)

    print(f"Verwende Config: {cfg_path}")

    # Shared data zwischen processes
    mgr = multiprocessing.Manager()
    contact_list = mgr.dict()  

    # Inter-process communication queues 
    ui_msg_queue = multiprocessing.Queue()     # discovery/network -> ui
    discovery_cmd_queue = multiprocessing.Queue()   # ui -> discovery
    network_cmd_queue = multiprocessing.Queue()    # ui -> network

    # Discovery process (UDP)
    disc_proc = multiprocessing.Process(
        target=discovery_process,
        args=(ui_msg_queue, discovery_cmd_queue, cfg_path, contact_list)
    )

    # Network process (TCP messaging)
    net_proc = multiprocessing.Process(
        target=network_process,
        args=(ui_msg_queue, network_cmd_queue, cfg_path, contact_list)
    )

    # Start background processes
    disc_proc.start()
    net_proc.start()

    # UI runs in main process (windows needs this)
    try:
        ui_process(ui_msg_queue, discovery_cmd_queue, network_cmd_queue, cfg_path)
    except KeyboardInterrupt:
        print("Programm wird beendet...")

    # cleanup
    disc_proc.terminate()
    net_proc.terminate()
    disc_proc.join()
    net_proc.join()