from network import send_slcp_broadcast, slcp_MSG
from config_utility import kontaktAnlegen, kontakteZeigen
import time
from config_utility import check_for_contact_list


def start_cli(auto=False, handle="", port=0000, whoisport=1111, config_path="", contacts_path=""):
    """
    Startet das CLI für den Nutzer.
    Im Automodus (auto=True) wird automatisch JOIN und WHO gesendet.
    """
    # Automatischer Modus: Sende JOIN und WHO und beende dann das CLI
    if auto:
        print(f"los geht's! {handle} tritt dem Netzwerk bei über Port {port}🚀")  
        send_slcp_broadcast("JOIN", handle, f"Port {port}") #JOIN nachricht senden
        time.sleep(1)  # Kurze Pause
        print(f"Wer ist aktuell im Netzwerk unterwegs?📡")
        send_slcp_broadcast("WHOIS", handle) #WHOIS anfrage senden
        time.sleep(3)  # Warten auf Antworten
        return

    # Manueller Modus: Zeige Menü mit Optionen an
    print("--------------------------------------")
    print("Waehle eine der folgenden Optionen 👀|")
    print("--------------------------------------")
    print("1 - Netzwerk beitreten 🌐")
    print("2 - Netzwerk verlassen ❌")
    print("3 - WHOIS-Anfrage senden 🕵️")  # WHO → WHOIS
    print("4 - Kontakt anlegen ➕")
    print("5 - Nachricht senden ✉️")
    print("6 - Kontakte anzeigen 📇")
    print("q - Programm beenden 👋")

    while True:
        choice = input("Eingabe: ").strip()
        
        if choice == "1":
            # JOIN nachricht senden
            send_slcp_broadcast("JOIN", handle, f"Port {port} ist angemeldet ✅")

        elif choice == "2":
            # LEAVE nachricht senden
            send_slcp_broadcast("LEAVE", handle, "ist abgemeldet ❎")

        elif choice == "3":
            # WHOIS anfrage senden
            send_slcp_broadcast("WHOIS", handle, "fordert Teilnehmerliste an 🔍")

        elif choice == "4":
            # Neuen kontakt anlegen
            try:
                check_for_contact_list(contacts_path)
                empfaenger = input("Name des Kontakts🆕: ").strip()
                if empfaenger:  # prüfen ob nicht leer
                    kontaktAnlegen(empfaenger, contacts_path)
                else:
                    print("Ungültiger Name ⚠️")
            except Exception as e:
                print(f"Fehler beim Anlegen des Kontakts: {e}")

        elif choice == "5":
            # Nachricht senden
            nachrichtSenden(contacts_path, handle)

        elif choice == "6":
            # Kontakte anzeigen
            try:
                check_for_contact_list(contacts_path)
                kontakteZeigen(contacts_path)
            except Exception as e:
                print(f"Fehler beim Anzeigen der Kontakte: {e}")

        elif choice.lower() == "q":
            # Programm beenden mit LEAVE nachricht
            print("Verlasse das Netzwerk...")
            send_slcp_broadcast("LEAVE", handle, "verlässt das Netzwerk")
            break
            
        else:
            print("Ungültige Eingabe ⚠️ Bitte erneut versuchen.")
            
        time.sleep(1)  # Kurze Pause vor der nächsten Eingabe


def nachrichtSenden(contacts_path, handle):
    """Nachricht an kontakt senden"""
    try:
        empfaenger = input("Empfaenger: ").strip()
        if not empfaenger: #prüfen ob leer
            print("Empfänger darf nicht leer sein ⚠️")
            return
            
        nachricht = input("Nachricht: ").strip()
        if not nachricht: #prüfen ob leer
            print("Nachricht darf nicht leer sein ⚠️")
            return
            
        success = slcp_MSG(empfaenger, nachricht, contacts_path, handle) #nachricht senden
        if not success:
            print("Nachricht konnte nicht gesendet werden ❌")
        else:
            print("Nachricht erfolgreich gesendet ✅")
            
    except Exception as e:
        print(f"Fehler beim Senden der Nachricht: {e}")