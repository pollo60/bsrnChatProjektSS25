
## @file ui.py
## @brief Command Line Interface (CLI) zur Steuerung der Netzwerkinteraktionen.

#Aufgaben:
#
# 1. Started die Benutzeroberfläche - GUI falls dies nicht gelingt, die CLI
# 2. Regelt Warteschlangen von Prozessen
# 3. Interface bietet den User Optionen für die weitere Vorgehensweise

## Dieses Modul stellt dem Benutzer eine einfache Textoberfläche zur Verfügung,
## um Nachichten zu verschicken, zu empfangen und Kontakte zu erhalten.
# Das Userinterface bietet Optionen:
# 1. JOIN - Beitritt zum Netzwerk
# 2. WHO  - Benutzer abfragen
# 3. MSG  - Nachichten versenden
# 4. LEAVE - Chat verlassem
# 5. Kontakte anzeigen
# 6. Config anzeigen
# 7. Bilder verschicken
# 8. Programm beenden

# Das User interface ist verantwortlich für alle Kommunikationen zwischen Usern.
# Kommuniziert mit discovery und network und managed Warteschlangen.



import time           # Zeitfunktion für Cooldowns
import toml           # Liest Userdaten aus TOML Dateien ein
import threading      # Zur ausführung meherer Dateien
from gui import start_gui # Importiert die start gui Funktion

def ui_process(ui_queue, disc_queue, net_queue, config_path):
    """
    @brief UI Process - startet die GUI statt CLI

    @param ui queue - Warteschlangen für das User Interface
    @param disc queue - Warteschlangen für Kommunikation mit discovery
    @param net queue - Warteschlangen für Kommunikation mit network
    @param config path - Pfad für die TOML Userdateien

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
    @brief CLI Fallback falls GUI nicht funktioniert

    @param ui queue - Warteschlangen für das User Interface
    @param disc queue - Warteschlangen für Kommunikation mit discovery
    @param net queue - Warteschlangen für Kommunikation mit network
    @param config path - Pfad für die TOML Userdateien

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
    print("8 - Programm beenden")

    # Background thread für live output
    def output_handler():
        while True:
            while not ui_queue.empty():     # Wiederholt Nachricht aus der Warteschlange
                output_msg = ui_queue.get() # Zeit diese an
                print(output_msg)           # Kurze Pause um Abstürze zu vermeiden
            time.sleep(0.1)            

    # Hintergrund thread starten
    threading.Thread(target=output_handler, daemon=True).start()

    # Main input loop des UI
    while True:
        time.sleep(0.1)  # Zeitliche Pause um Abstürze zu vermeiden

        user_input = input("Option wählen: ").strip() # Benutzereingabe 

        # JOIN senden
        if user_input == "1":
            cfg = toml.load(config_path) # läd konfig
            username = cfg["handle"]     # Username
            port_num = cfg["port"]       # Portnummer
            disc_queue.put(f"JOIN {username} {port_num}")  # JOIN

        # WHO broadcast
        elif user_input == "2": # Fragt ob jemand online ist
            disc_queue.put("WHO") # Sendet WHO Befehl in die Warteschlange

        # Message senden
        elif user_input == "3":
            recipient = input("Empfänger: ").strip() # Ziel Benutzer der Nachricht
            msg_text = input("Nachricht: ").strip()  # Benutzername
            net_queue.put(f"MSG {recipient} {msg_text}")  # Nachricht für die Warteschlange

        # LEAVE
        elif user_input == "4": 
            cfg = toml.load(config_path) # läd konfig
            username = cfg["handle"] # Benutzername
            disc_queue.put(f"LEAVE {username}") # Sendet Leave an Warteschlange

        # Kontakte anzeigen
        elif user_input == "5":
            disc_queue.put("KONTAKTE")  # Schickt Kontaktliste in die Warteschlange

        # Config anzeigen
        elif user_input == "6":
            cfg = toml.load(config_path) # läd konfig
            print("[AKTUELLE CONFIG]")   
            for key, value in cfg.items(): # Geht durch alle Schlüsselwerte der Konfig Datei
                print(f"{key} = {value}") # Zeigt jedes Konfig Element an

        # Bild senden
        elif user_input == "7":
            recipient = input("Empfänger: ").strip()       # Ziel User
            image_path = input("Pfad zum Bild: ").strip()  # Pfad zur Bilddatei
            import os
            if os.path.exists(image_path):  # Prüft ob die Bilddatei existiert
                from pathlib import Path
                with open(image_path, "rb") as f:
                    file_data = f.read()             # Versendet Bild
                img_filename = Path(image_path).name  # Zeigt Datei(Bild)-Namen an
                img_size = len(file_data)             # Dateigröße
                # Sendet Nachricht(Bild) an die Warteschlange
                net_queue.put(f"IMG_SEND {recipient} {img_filename} {img_size}::{image_path}") 
            else:
                print("[FEHLER] Bilddatei nicht vorhanden.")

        # Beendet das Programm 
        elif user_input == "8":
            print("Tschüss!")
            break

        # ungültige Eingabe
        else:
            print("Unbekannte Option.")

        time.sleep(0.1) # Erneute Pause um einen Absturz zu vermeiden 




