import time
import toml

import threading

def ui_process(ui_queue, disc_queue, net_queue, config_path):
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

    def live_output():
        while True:
            while not ui_queue.empty():
                msg = ui_queue.get()
                print(msg)
            time.sleep(0.1)

    threading.Thread(target=live_output, daemon=True).start()

    while True:
        # UI wird nun live durch Thread aktualisiert

        time.sleep(0.1)  # Ermöglicht UI-Aktualisierung ohne Eingabe

        cmd = input("Auswahl: ").strip()

        if cmd == "1":
            config = toml.load(config_path)
            handle = config["handle"]
            port = config["port"]
            disc_queue.put(f"JOIN {handle} {port}")

        elif cmd == "2":
            disc_queue.put("WHO")

        elif cmd == "3":
            empfaenger = input("Empfänger: ").strip()
            text = input("Nachricht: ").strip()
            net_queue.put(f"MSG {empfaenger} {text}")

        elif cmd == "4":
            config = toml.load(config_path)
            handle = config["handle"]
            disc_queue.put(f"LEAVE {handle}")

        elif cmd == "5":
            disc_queue.put("KONTAKTE")

        elif cmd == "6":
            config = toml.load(config_path)
            print("[KONFIGURATION]")
            for k, v in config.items():
                print(f"{k} = {v}")

        elif cmd == "7":
            empfaenger = input("Empfänger: ").strip()
            pfad = input("Pfad zur Bilddatei: ").strip()
            import os
            if os.path.exists(pfad):
                from pathlib import Path
                with open(pfad, "rb") as f:
                    data = f.read()
                filename = Path(pfad).name
                size = len(data)
                net_queue.put(f"IMG_SEND {empfaenger} {filename} {size}::{pfad}")
            else:
                print("[FEHLER] Bilddatei nicht gefunden.")

        
        elif cmd == "9":
            print("Beende Anwendung...")
            break

        else:
            print("Ungültiger Befehl.")

        time.sleep(0.1)