# cli.py
# Diese Klasse simuliert einen einfachen Chat-Client mit Dummy-Daten
class ChatClient:
    def __init__(self, server_address, handle):
        # Initialisierung mit Server-Adresse und Benutzername
        self.server_address = server_address
        self.handle = handle
        self.users = ["Alice", "Bob", "Charlie"]  # Liste von verbundenen Benutzern (simuliert)

    def get_users(self):
        # Gibt die Liste aller bekannten Benutzer zurück
        return self.users

    def send_message(self, empfaenger, nachricht):
        # Gibt eine Bestätigung über das Senden einer Nachricht aus
        print(f"Nachricht an {empfaenger}: {nachricht}")

    def send_image(self, pfad):
        # Gibt eine Bestätigung über das Senden einer Nachricht aus
        print(f"Bild gesendet: {pfad}")

    def set_handle(self, neuer_name):
        # Ändert den Benutzernamen
        self.handle = neuer_name
        print(f"Benutzername geändert zu {neuer_name}")

# Hauptklasse für die Kommandozeilen-Oberfläche
class ChatCLI:
    def __init__(self):
        self.client = None # Hier wird später die ChatClient-Instanz gespeichert
        self.running = True  # Steuert die Hauptschleife des Programms

    def setup(self):
         # Führt die Benutzerabfrage beim Start durch (Serveradresse und Benutzername)
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
            # Erzeugt ein neues ChatClient-Objekt mit eingegebenen Daten
            # Annahme: ChatClient nimmt Serveradresse und Benutzernamen im Konstruktor oder Setup
            self.client = ChatClient(server_address=server, handle=benutzername)
            print(f"✅ Verbunden mit {server} als {benutzername}")
        except Exception as e:
            print(f"[Fehler beim Verbinden]: {e}")
            exit(1)

    def anzeigen_menue(self):
         # Zeigt die Auswahlmöglichkeiten für den Benutzer an
        print("\n=== Chat-Client Menü ===")
        print(" who      - Zeige alle verbundenen Benutzer")
        print(" msg      - Sende Nachricht")
        print(" sendimg  - Sende Bild")
        print(" config   - Benutzername ändern")
        print(" exit     - Beenden")

    def verarbeite_befehl(self, befehl):
        # Verarbeitet den eingegebenen Befehl
        if befehl == "who":
            try:
                nutzer = self.client.get_users()
                print("Online: ", ", ".join(nutzer))
            except Exception as e:
                print(f"[Fehler bei 'who']: {e}")

        elif befehl == "msg":
            # Nachricht an bestimmten Nutzer senden
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
             # Bild senden (nur simuliert)
            pfad = input("Pfad zum Bild: ").strip()
            try:
                self.client.send_image(pfad)
                print("🖼️ Bild wurde gesendet.")
            except Exception as e:
                print(f"[Fehler beim Bildsenden]: {e}")

        elif befehl == "config":
            # Benutzername ändern
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
            # Beendet das Programm
            print("👋 Verbindung wird beendet.")
            self.running = False

        else:
            # Unbekannter Befehl
            print("❌ Unbekannter Befehl. Bitte versuch es erneut.")

    def starten(self):
        # Startpunkt des Programms
        self.setup() # Verbindungsdaten abfragen
        print("🔌 Chat-Client gestartet.")
        while self.running:
            self.anzeigen_menue()  # Menü anzeigen
            befehl = input(">> Befehl eingeben: ").strip().lower()
            self.verarbeite_befehl(befehl)


# Startet das Programm, wenn es direkt ausgeführt wird
if __name__ == "__main__":
    cli = ChatCLI()
    cli.starten()
