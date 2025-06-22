import time           # Für Pausen, z. B. bei Wartezyklen
import toml           # Zum Einlesen der Konfigurationsdatei
import threading      # Für parallelen Live-Ausgabe-Thread

# Hauptfunktion für die Benutzeroberfläche (läuft im Hauptprozess)
def ui_process(ui_queue, disc_queue, net_queue, config_path):
    # Menü anzeigen
    print("Willkommen zum Chat (CLI).\n")
    print("[Menü] Wähle eine Option:")
    print("1 - JOIN senden")
    print("2 - WHO senden")
    print("3 - MSG senden")
    print("4 - LEAVE senden")
    print("5 - Kontakte anzeigen")
    print("6 - Konfiguration anzeigen")
    print("7 - Bild senden")
    print("9 - Beenden")

    # Funktion für parallele Anzeige von Ausgaben aus anderen Prozessen
    def live_output():
        while True:
            while not ui_queue.empty():
                msg = ui_queue.get()   # Nachricht aus UI-Queue holen
                print(msg)             # Auf Konsole ausgeben
            time.sleep(0.1)            # Kurze Pause zwischen den Checks

    # Startet einen Daemon-Thread für Live-Ausgabe (läuft im Hintergrund)
    threading.Thread(target=live_output, daemon=True).start()

    # Hauptschleife: wartet auf Benutzereingaben
    while True:
        time.sleep(0.1)  # Kleiner Delay für reibungslose Darstellung

        # Eingabeaufforderung anzeigen
        cmd = input("Auswahl: ").strip()

        # 1 - JOIN senden
        if cmd == "1":
            config = toml.load(config_path)
            handle = config["handle"]
            port = config["port"]
            disc_queue.put(f"JOIN {handle} {port}")  # an Discovery-Prozess

        # 2 - WHO senden (Broadcast: Wer ist online?)
        elif cmd == "2":
            disc_queue.put("WHO")

        # 3 - MSG senden (Textnachricht an bestimmten Client)
        elif cmd == "3":
            empfaenger = input("Empfänger: ").strip()
            text = input("Nachricht: ").strip()
            net_queue.put(f"MSG {empfaenger} {text}")  # an Network-Prozess

        # 4 - LEAVE senden
        elif cmd == "4":
            config = toml.load(config_path)
            handle = config["handle"]
            disc_queue.put(f"LEAVE {handle}")

        # 5 - Kontakte anzeigen
        elif cmd == "5":
            disc_queue.put("KONTAKTE")

        # 6 - Konfiguration anzeigen (aus config.toml)
        elif cmd == "6":
            config = toml.load(config_path)
            print("[KONFIGURATION]")
            for k, v in config.items():
                print(f"{k} = {v}")

        # 7 - Bild senden
        elif cmd == "7":
            empfaenger = input("Empfänger: ").strip()
            pfad = input("Pfad zur Bilddatei: ").strip()
            import os
            if os.path.exists(pfad):  # Datei vorhanden?
                from pathlib import Path
                with open(pfad, "rb") as f:
                    data = f.read()   # Datei vollständig einlesen
                filename = Path(pfad).name
                size = len(data)
                # Sende-Befehl an network_process
                net_queue.put(f"IMG_SEND {empfaenger} {filename} {size}::{pfad}")
            else:
                print("[FEHLER] Bilddatei nicht gefunden.")

        # 9 - Beenden
        elif cmd == "9":
            print("Beende Anwendung...")
            break

        # Ungültige Eingabe
        else:
            print("Ungültiger Befehl.")

        time.sleep(0.1)  # Kleine Pause, damit alles synchron bleibt
