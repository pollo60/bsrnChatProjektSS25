## \file ui.py
## \brief Command Line Interface (CLI) zur Steuerung der Netzwerkinteraktionen.
##
## Dieses Modul stellt dem Benutzer eine einfache Textoberfläche zur Verfügung,
## um Nachichten zu verschicken, zu empfangen und Kontakte zu erhalten.

from config_utility import kontaktAnlegen, kontakteZeigen
import time
from config_utility import check_for_contact_list


def start_cli(auto=False, handle="", port=5000, whoisport=54321, config_path="", contacts_path=""):
    """
    Startet das CLI für den Nutzer.
    Im Automodus (auto=True) wird automatisch JOIN und WHO gesendet.
    """
    # Automatischer Modus: Sende JOIN und WHO und beende dann das CLI
    if auto:
        print(f"[AUTO] Sende JOIN für {handle}:{port}")
        send_udp_broadcast(f"JOIN {handle} {port}", whoisport)  # JOIN-Nachricht an Netzwerk senden
        time.sleep(1)  # Kurze Pause
        print(f"[AUTO] Sende WHO")
        send_udp_broadcast("WHO", whoisport) # WHO-Anfrage senden, um Teilnehmer zu ermitteln
        time.sleep(3)  # Warten auf Antworten
        return

    # Manueller Modus: Zeige Menü mit Optionen an
    print("Discovery Test CLI:") 
    print("1 - JOIN") # Netzwerkbeitritt
    print("2 - LEAVE") # Netzwerk verlassen
    print("3 - WHO") # Liste der Teilnehmer abrufen
    print("4 - Kontakt anlegen") # Neuen Kontakt zur Kontaktliste hinzufügen
    print("5 - MSG")  # Nachricht an Kontakt senden
    print("6 - KOntakte anzeigen") # Alle gespeicherten Kontakte anzeigen
    print("q - Quit")  # CLI beenden

    while True:
        choice = input("Eingabe: ").strip()
        if choice == "1":
            # Sende JOIN-Nachricht mit Handle(Name) und Port
            send_udp_broadcast(f"JOIN {handle} {port}", whoisport)

        elif choice == "2":
             # Sende LEAVE-Nachricht mit Handle(Name)
            send_udp_broadcast(f"LEAVE {handle}", whoisport)

        elif choice == "3":
            # Sende WHO-Anfrage mit Handle, um Teilnehmerliste anzufordern
            send_udp_broadcast(f"WHO {handle}", whoisport)

        elif choice == "4":
            # Neuen Kontakt anlegen: Frage nach Name und leite weiter
            check_for_contact_list(contacts_path)

            empfaenger = input("Name des Kontakts:")

            kontaktAnlegen(empfaenger, config_path)
            # Nachricht senden (interaktive Funktion in nachrichtSenden)
        elif choice == "5":

            nachrichtSenden(config_path)
            # Zeige alle gespeicherten Kontakte an
        elif choice == "6":

            kontakteZeigen(config_path)
            # Beende die CLI-Schleife
            kontaktAnlegen(empfaenger, contacts_path)
        elif choice == "5":
            nachrichtSenden(contacts_path)
        elif choice == "6":
            check_for_contact_list(contacts_path)
            kontakteZeigen(contacts_path)

        elif choice.lower() == "q":

            break
        else:
            print("Ungültige Eingabe.")
        time.sleep(1) # Kurze Pause vor der nächsten Eingabe
