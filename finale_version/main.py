# Standard-Module importieren
import multiprocessing  # Für parallele Prozesse und Queues
import sys              # Für Zugriff auf Kommandozeilenargumente
import toml             # Für Laden der Konfigurationsdatei

# Eigene Module (Prozess-Logik)
from discovery_process import discovery_process
from network_process import network_process
from ui_process import ui_process

# Nur ausführen, wenn direkt gestartet (nicht importiert)
if __name__ == "__main__":
    # Windows braucht 'spawn' als Startmethode für multiprocessing
    multiprocessing.set_start_method("spawn")  # Alternativ: 'fork' auf Unix-Systemen

    # Konfigurationspfad aus Argument übergeben oder Standard verwenden
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.toml"

    # Gemeinsame Datenstruktur (wird von mehreren Prozessen genutzt)
    manager = multiprocessing.Manager()
    kontakte = manager.dict()  # Kontaktliste für Discovery + Netzwerk

    # Queues für die Interprozesskommunikation (Message-Passing zwischen Prozessen)
    ui_queue = multiprocessing.Queue()     # Von Discovery/Netzwerk zur UI (Ausgaben)
    disc_queue = multiprocessing.Queue()   # Von UI zu Discovery (JOIN, WHO, LEAVE)
    net_queue = multiprocessing.Queue()    # Von UI zu Netzwerk (MSG, IMG_SEND)

    # Discovery-Prozess starten (JOIN, WHO, LEAVE per UDP)
    p1 = multiprocessing.Process(
        target=discovery_process,
        args=(ui_queue, disc_queue, config_path, kontakte)
    )

    # Netzwerkprozess starten (persönliche Nachrichten und Bilder per TCP)
    p2 = multiprocessing.Process(
        target=network_process,
        args=(ui_queue, net_queue, config_path, kontakte)
    )

    # Prozesse starten (laufen unabhängig im Hintergrund)
    p1.start()
    p2.start()

    # CLI/UI läuft im Hauptprozess (besonders wichtig unter Windows wegen Eingabeaufforderung)
    try:
        ui_process(ui_queue, disc_queue, net_queue, config_path)
    except KeyboardInterrupt:
        print("Programm beendet")

    # Nach Beenden der UI-Prozess-Schleife: Kindprozesse beenden und aufräumen
    p1.terminate()
    p2.terminate()
    p1.join()
    p2.join()
