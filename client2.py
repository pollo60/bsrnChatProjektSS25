import toml

def add_contact(config_path):
    try:
        with open(config_path, "r") as f:
            config = toml.load(f)
    except Exception as e:
        print(f"❌ Fehler beim Laden der Konfiguration: {e}")
        return

    handle = input("🆕 Kontakt-Handle: ").strip()
    ip = input("🌐 IP-Adresse des Kontakts: ").strip()
    port = input("🔢 Port des Kontakts: ").strip()

    if not handle or not ip or not port.isdigit():
        print("❌ Ungültige Eingaben. Kontakt wurde nicht gespeichert.")
        return

    if "contacts" not in config:
        config["contacts"] = {}

    config["contacts"][handle] = {"ip": ip, "port": int(port)}

    try:
        with open(config_path, "w") as f:
            toml.dump(config, f)
        print(f"✅ Kontakt '{handle}' wurde erfolgreich hinzugefügt.")
    except Exception as e:
        print(f"❌ Fehler beim Speichern der Konfiguration: {e}")

        ################################################################
        
def start_cli(auto, handle, port, whoisport, config_path):
    while True:
        print("\n📋 Menü:")
        print("1️⃣  Nachricht senden (Demo)")
        print("2️⃣  Kontakte anzeigen (Demo)")
        print("3️⃣  📇 Kontakt anlegen")
        print("4️⃣  🚪 Beenden")

        auswahl = input("👉 Auswahl (1–4): ").strip()

        if auswahl == "1":
            print("✉️ Nachricht senden – Funktion noch nicht implementiert.")
        elif auswahl == "2":
            print("📖 Kontakte anzeigen – Funktion noch nicht implementiert.")
        elif auswahl == "3":
            add_contact(config_path)
        elif auswahl == "4":
            print("👋 Beende das Programm.")
            break
        else:
            print("❌ Ungültige Eingabe, bitte 1–4 wählen.")
