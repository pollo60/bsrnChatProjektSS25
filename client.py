class ChatCLI:
    def __init__(self):
        self.client = None
        self.running = True

    def setup(self):
        print("⚙️  Chat-Client Setup")
        server = input("⚠️ Server-Adresse eingeben (z.B. 127.0.0.1:1234): ").strip()
        while not server:
            print("Server-Adresse darf nicht leer sein.")
            server = input("⚠️ Server-Adresse eingeben: ").strip()

        benutzername = input("Benutzername wählen: ").strip()
        while not benutzername:
            print("⚠️ Benutzername darf nicht leer sein.")
            benutzername = input("Benutzername wählen: ").strip()

        try:
            # Annahme: ChatClient nimmt Serveradresse und Benutzernamen im Konstruktor oder Setup
            self.client = ChatClient(server_address=server, handle=benutzername)
            print(f"✅ Verbunden mit {server} als {benutzername}")
        except Exception as e:
            print(f"[Fehler beim Verbinden]: {e}")
            exit(1)

    def anzeigen_menue(self):
        print("\n=== Chat-Client Menü ===")
        print(" who      - Zeige alle verbundenen Benutzer")
        print(" msg      - Sende Nachricht")
        print(" sendimg  - Sende Bild")
        print(" config   - Benutzername ändern")
        print(" exit     - Beenden")

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