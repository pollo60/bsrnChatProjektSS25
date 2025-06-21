## ui_process.py
import time
import toml

def ui_process(ui_queue, disc_queue, net_queue, config_path):
    config = toml.load(config_path)
    handle = config["handle"]
    port = config["port"]

    menu = (
        "\n[Menü] Wähle eine Option:\n"
        "1 - JOIN senden\n"
        "2 - WHO senden\n"
        "3 - MSG senden\n"
        "4 - LEAVE senden\n"
        "5 - Kontakte anzeigen\n"
        "6 - Konfiguration anzeigen\n"
        "9 - Beenden\n"
    )

    print("Willkommen zum Chat (CLI).")

    while True:
        while not ui_queue.empty():
            print(ui_queue.get(), flush=True)

        print(menu)
        try:
            cmd = input("> Auswahl: ").strip()
            if cmd == "1":
                disc_queue.put(f"JOIN {handle} {port}")

            elif cmd == "2":
                disc_queue.put("WHO")

            elif cmd == "3":
                empfaenger = input("Empfänger (Handle): ").strip()
                nachricht = input("Nachricht: ").strip()
                net_queue.put(f"MSG {empfaenger} {nachricht}")

            elif cmd == "4":
                disc_queue.put(f"LEAVE {handle}")

            elif cmd == "5":
                disc_queue.put("KONTAKTE")

            elif cmd == "6":
                print("[CONFIG] Aktuelle Konfiguration:")
                for key, value in config.items():
                    print(f"  {key}: {value}")

            elif cmd == "9":
                print("Beende Chat-Client.")
                break

        except EOFError:
            break

        time.sleep(0.1)
