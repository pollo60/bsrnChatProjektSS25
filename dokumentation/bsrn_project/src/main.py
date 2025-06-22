## @file
#Main.py

#@brief Hauptprogramm, steuert das gesamte Projekt mit mehreren Pozessen 

# Aufgaben:

#1. Startet 3 Prozesse:

# - Discovery => Sucht und verwaltet User im Netzwerk
# - listen for messages => Lauscht nach Nachrichten im Netzwerk
# - send broadcast => Sendet Broadcast Nachrichten an alle User im Netz

# 2. Initialisiert Konfig Daten

# 3. Sorgt für die Reihenfolge/Warteschlangen für alle Nutzer

# 4. Startet das Nutzerinterface

# 5. Beendet alle Prozesse, falls das Programm mit Strg C abgebrochen wird

import multiprocessing  # Für mehrere Prozesse
import sys              # Zugriff auf die Komandozeile
import os               # Für Dateipfade und die Prüfung dieser

from discovery_process import discovery_process # Importiert Discovery Funktionen
from network_process import network_process     # Importiert Netzwerk Funktionen
from ui_process import ui_process               # Importiert ui Funktionen

if __name__ == "__main__":
    # Windows braucht spawn für mehrere Prozesse
    multiprocessing.set_start_method("spawn")  

    # Script-Verzeichnis wird ermittelt
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ermittelt ob eine config Datei Datei angegeben wurde
    if len(sys.argv) > 1:
        cfg_filename = sys.argv[1]
        # Wenn nur der Dateiname angegeben wird, im Script-Verzeichnis suchen
        if not os.path.dirname(cfg_filename):
            cfg_path = os.path.join(script_dir, cfg_filename)
        else:
            # falls der gesamte Pfad angegeben wurde
            cfg_path = cfg_filename
    else:
        # Standard config.toml - Standard für das Config Verzeichnis
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

    # Shared data zwischen processes mit Hilfe eines Managers
    mgr = multiprocessing.Manager()
    contact_list = mgr.dict()  

    # Inter-process communication queues - Warteschlange für mehrere Prozesse
    ui_msg_queue = multiprocessing.Queue()     # discovery/network -> ui
    discovery_cmd_queue = multiprocessing.Queue()   # ui -> discovery
    network_cmd_queue = multiprocessing.Queue()    # ui -> network

    # Der discovery process erkennt andere Nutzer im Netzwerk
    disc_proc = multiprocessing.Process(
        target=discovery_process,
        args=(ui_msg_queue, discovery_cmd_queue, cfg_path, contact_list)
    )

    # Network process (für Nachichten)
    net_proc = multiprocessing.Process(
        target=network_process,
        args=(ui_msg_queue, network_cmd_queue, cfg_path, contact_list)
    )

    # Start background processes (Started discovery und network im Hintergrund)
    disc_proc.start()
    net_proc.start()

    # Started den ui Prozess
    try:
        ui_process(ui_msg_queue, discovery_cmd_queue, network_cmd_queue, cfg_path)
    except KeyboardInterrupt:
        print("Programm wird beendet...")


    # Beendet alle Prozesse
    disc_proc.terminate()
    net_proc.terminate()
    disc_proc.join()
    net_proc.join()
