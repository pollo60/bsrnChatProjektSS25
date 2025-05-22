from network import send_udp_broadcast, nachrichtSenden
from config_utility import kontaktAnlegen, kontakteZeigen
import time


def start_cli(auto=False, handle="", port=5000, whoisport=54321, config_path=""):
    """
    Startet das CLI für den Nutzer.
    Im Automodus (auto=True) wird automatisch JOIN und WHO gesendet.
    """

    if auto:
        print(f"[AUTO] Sende JOIN für {handle}:{port}")
        send_udp_broadcast(f"JOIN {handle} {port}", whoisport)
        time.sleep(1)
        print(f"[AUTO] Sende WHO")
        send_udp_broadcast("WHO", whoisport)
        time.sleep(3)
        return

    # Manueller Modus
    print("Discovery Test CLI:")
    print("1 - JOIN")
    print("2 - LEAVE")
    print("3 - WHO")
    print("4 - Kontakt anlegen")
    print("5 - MSG")
    print("6 - KOntakte anzeigen")
    print("q - Quit")

    while True:
        choice = input(">> ").strip()
        if choice == "1":
            send_udp_broadcast(f"JOIN {handle} {port}", whoisport)
        elif choice == "2":
            send_udp_broadcast(f"LEAVE {handle}", whoisport)
        elif choice == "3":
            send_udp_broadcast("WHO", whoisport)
        elif choice == "4":
            empfaenger = input("Name des Kontakts:")
            kontaktAnlegen(empfaenger, config_path)
        elif choice == "5":
            nachrichtSenden(config_path)
        elif choice == "6":
            kontakteZeigen(config_path)
        elif choice.lower() == "q":
            break
        else:
            print("Ungültige Eingabe.")
        time.sleep(1)
