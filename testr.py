#client test2.py und cli.py kombiniert
import sys
import toml

from Altays_Ansatz.discoveryANSATZ import datenAufnehmen, inConfigSchreiben, zeigeConfig, WHO, MSG, nachrichtSenden
from Netzwerk_Kommunikation.empfaenger import netzwerkEmpfMain, discoveryWHO


class ChatClient:
    def __init__(self, server_address, handle):
        self.server_address = server_address
        self.handle = handle
        self.users = ["Alice", "Bob", "Charlie"]  # Dummy

    def get_users(self):
        return self.users

    def send_message(self, empfaenger, nachricht):
        print(f"Nachricht an {empfaenger}: {nachricht}")

    def send_image(self, pfad):
        print(f"Bild gesendet: {pfad}")

    def set_handle(self, neuer_name):
        self.handle = neuer_name
        print(f"Benutzername geändert zu {neuer_name}")


class ChatCLI:
    def __init__(self):
        self.client = None
        self.running = True

    def setup(self):
        print("⚙️  Chat-Client Setup")

        zeigeConfig()
        login_daten = datenAufnehmen()
        inConfigSchreiben(login_daten)
        zeigeConfig()

        server = input("⚠️ Server-Adresse eingeben (z.B. 127.0.0.1:1234): ").strip()
        while not server:
            print("Server-Adresse darf nicht leer sein.")
            server = input("⚠️ Server-Adresse eingeben: ").strip()

        benutzername = input("Benutzername wählen: ").strip()
        while not benutzername:
            print("⚠️ Benutzername darf nicht leer sein.")
            benutzername = input("Benutzername wählen: ").strip()

        self.client = ChatClient(server_address=server, handle=benutzername)
        print(f"✅ Verbunden mit {server} als {benutzername}")

        discoveryWHO()
        netzwerkEmpfMain()

    def anzeigen_menue(self):
        print("\n=== Chat-Client Menü ===")
        print(" who      - Zeige alle verbundenen Benutzer")
        print(" msg      - Sende Nachricht")
        print(" sendimg  - Sende Bild")
        print(" config   - Benutzername ändern")
        print(" kontakt  - Kontakt anlegen")
        print(" who-net  - Teilnehmer im Netz anzeigen")
        print(" msg-net  - Nachricht im Netz senden")
        print(" exit     - Beenden")

    def kontaktAnlegen(self):
        try:
            with open('configANSATZ.toml', 'r') as f:
                config = toml.load(f)
        except FileNotFoundError:
            config = {}

        name = input("Gib den Namen ein: ").strip()
        port = input("Gib die Portnummer ein: ").strip()
        ip = input("Gib die IP ein: ").strip()

        config[name] = {
            'ziel_name': name,
            'ziel_port': port,
            'ziel_ip': ip
        }

        with open('configANSATZ.toml', 'w') as f:
            toml.dump(config, f)

        print("✅ Config-Datei wurde aktualisiert:")
        print(config[name]['ziel_name'])
        print(config[name]['ziel_port'])
        print(config[name]['ziel_ip'])

    def verarbeite_befehl(self, befehl):
        if befehl == "who":
            try:
                nutzer = self.client.get_users()
                print("Online: ", ", ".join(nutzer))
            except Exception as e:
                print(f"[Fehler bei 'who']: {e}")

        elif befehl == "msg":
            empfaenger = input("An wen? ").strip()
            nachricht = input("Nachricht: ").strip()
            if empfaenger and nachricht:
                try:
                    self.client.send_message(empfaenger, nachricht)
                    print("✅ Nachricht gesendet.")
                except Exception as e:
                    print(f"[Fehler beim Senden]: {e}")
            else:
                print("⚠️ Empfänger oder Nachricht darf nicht leer sein.")

        elif befehl == "sendimg":
            pfad = input("Pfad zum Bild: ").strip()
            try:
                self.client.send_image(pfad)
                print("🖼️ Bild wurde gesendet.")
            except Exception as e:
                print(f"[Fehler beim Bildsenden]: {e}")

        elif befehl == "config":
            neuer_name = input("Neuer Benutzername: ").strip()
            if neuer_name:
                try:
                    self.client.set_handle(neuer_name)
                    print(f"🆗 Name geändert zu: {neuer_name}")
                except Exception as e:
                    print(f"[Fehler bei Änderung]: {e}")
            else:
                print("⚠️ Benutzername darf nicht leer sein.")

        elif befehl == "kontakt":
            self.kontaktAnlegen()

        elif befehl == "who-net":
            try:
                WHO()
            except Exception as e:
                print(f"[Fehler bei WHO-Net]: {e}")

        elif befehl == "msg-net":
            try:
                nachrichtSenden()
            except Exception as e:
                print(f"[Fehler beim Senden im Netz]: {e}")

        elif befehl == "exit":
            print("👋 Verbindung wird beendet.")
            self.running = False

        else:
            print("❌ Unbekannter Befehl. Bitte versuch es erneut.")

    def starten(self):
        self.setup()
        print("🔌 Chat-Client gestartet.")
        while self.running:
            self.anzeigen_menue()
            befehl = input(">> Befehl eingeben: ").strip().lower()
            self.verarbeite_befehl(befehl)


if __name__ == "__main__":
    cli = ChatCLI()
    cli.starten()
