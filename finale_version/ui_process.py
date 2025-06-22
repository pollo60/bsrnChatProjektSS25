import time           
import toml           
import threading      
from gui import start_gui

def ui_process(ui_queue, disc_queue, net_queue, config_path):
    """
    UI Process - startet die GUI statt CLI
    """
    try:
        # GUI starten
        start_gui(config_path, ui_queue, disc_queue, net_queue)
    except Exception as e:
        print(f"GUI Fehler: {e}")
        # Fallback auf CLI wenn GUI nicht funktioniert
        cli_fallback(ui_queue, disc_queue, net_queue, config_path)

def cli_fallback(ui_queue, disc_queue, net_queue, config_path):
    """
    CLI Fallback falls GUI nicht funktioniert
    """
    print("GUI konnte nicht gestartet werden. Verwende CLI...")
    print("Chat CLI - Willkommen!\n")
    print("Was möchtest du machen?")
    print("1 - Chat beitreten (JOIN)")
    print("2 - Wer ist online? (WHO)")
    print("3 - Nachricht senden")
    print("4 - Chat verlassen (LEAVE)")
    print("5 - Kontakte zeigen")
    print("6 - Config anzeigen")
    print("7 - Bild verschicken")
    print("9 - Programm beenden")

    # Background thread für live output
    def output_handler():
        while True:
            while not ui_queue.empty():
                output_msg = ui_queue.get()   
                print(output_msg)             
            time.sleep(0.1)            

    # Daemon thread starten
    threading.Thread(target=output_handler, daemon=True).start()

    # Main input loop
    while True:
        time.sleep(0.1)  

        user_input = input("Option wählen: ").strip()

        # JOIN senden
        if user_input == "1":
            cfg = toml.load(config_path)
            username = cfg["handle"]
            port_num = cfg["port"]
            disc_queue.put(f"JOIN {username} {port_num}")  

        # WHO broadcast
        elif user_input == "2":
            disc_queue.put("WHO")

        # Message senden
        elif user_input == "3":
            recipient = input("An wen? ").strip()
            msg_text = input("Nachricht: ").strip()
            net_queue.put(f"MSG {recipient} {msg_text}")  

        # LEAVE
        elif user_input == "4":
            cfg = toml.load(config_path)
            username = cfg["handle"]
            disc_queue.put(f"LEAVE {username}")

        # Kontakte anzeigen
        elif user_input == "5":
            disc_queue.put("KONTAKTE")

        # Config anzeigen
        elif user_input == "6":
            cfg = toml.load(config_path)
            print("[AKTUELLE CONFIG]")
            for key, value in cfg.items():
                print(f"{key} = {value}")

        # Bild senden
        elif user_input == "7":
            recipient = input("Empfänger: ").strip()
            image_path = input("Pfad zum Bild: ").strip()
            import os
            if os.path.exists(image_path):  
                from pathlib import Path
                with open(image_path, "rb") as f:
                    file_data = f.read()   
                img_filename = Path(image_path).name
                img_size = len(file_data)
                net_queue.put(f"IMG_SEND {recipient} {img_filename} {img_size}::{image_path}")
            else:
                print("[FEHLER] Bilddatei nicht vorhanden.")

        # Beenden
        elif user_input == "9":
            print("Tschüss!")
            break

        # ungültige eingabe
        else:
            print("Unbekannte Option.")

        time.sleep(0.1)