import time
from network import send_slcp_broadcast, slcp_MSG
from config_utility import (
    kontaktAnlegen,
    kontakteZeigen,
    check_for_contact_list,
    configAnzeigen
)

def start_cli(auto=False, handle="", port=0, whoisport=1111, config_path="", contacts_path="", broadcast_ip="255.255.255.255"):
    """Startet das CLI. Im Automodus wird direkt JOIN + WHO gesendet."""
    if auto:
        print(f"[AUTO] {handle} tritt dem Netzwerk bei über Port {port} 🚀")
        send_slcp_broadcast("JOIN", handle, str(port), port=whoisport, broadcast_ip=broadcast_ip)
        time.sleep(1)
        print("[AUTO] WHO-Anfrage wird gesendet...")
        send_slcp_broadcast("WHO", handle, "", port=whoisport, broadcast_ip=broadcast_ip)
        time.sleep(3)
        return

    print("""
--------------------------------------
Waehle eine der folgenden Optionen 👀|
--------------------------------------
1 - Netzwerk beitreten 🌐
2 - Netzwerk verlassen ❌
3 - WHO-Anfrage senden 🕵️
4 - Kontakt anlegen ➕
5 - Nachricht senden ✉️
6 - Kontakte anzeigen 📗
7 - Konfigurationsdatei anzeigen 🧩
q - Programm beenden 👋
""")

    while True:
        choice = input("Eingabe: ").strip()

        if choice == "1":
            send_slcp_broadcast("JOIN", handle, str(port), port=whoisport, broadcast_ip=broadcast_ip)
        elif choice == "2":
            send_slcp_broadcast("LEAVE", handle, "", port=whoisport, broadcast_ip=broadcast_ip)
        elif choice == "3":
            send_slcp_broadcast("WHO", handle, "", port=whoisport, broadcast_ip=broadcast_ip)
        elif choice == "4":
            try:
                check_for_contact_list(contacts_path)
                empfaenger = input("Name des Kontakts🆕: ").strip()
                if empfaenger:
                    kontaktAnlegen(empfaenger, contacts_path)
                else:
                    print("Ungültiger Name ⚠️")
            except Exception as e:
                print(f"[FEHLER] Kontakt konnte nicht erstellt werden: {e}")
        elif choice == "5":
            nachrichtSenden(contacts_path, handle)
        elif choice == "6":
            try:
                check_for_contact_list(contacts_path)
                kontakteZeigen(contacts_path)
            except Exception as e:
                print(f"[FEHLER] Kontakte konnten nicht angezeigt werden: {e}")
        elif choice == "7":
            try:
                configAnzeigen(config_path)
            except Exception as e:
                print(f"[FEHLER] Konfiguration konnte nicht angezeigt werden: {e}")
        elif choice.lower() == "q":
            print("Verlasse das Netzwerk...")
            send_slcp_broadcast("LEAVE", handle, "", port=whoisport, broadcast_ip=broadcast_ip)
            break
        else:
            print("Ungültige Eingabe ⚠️ Bitte erneut versuchen.")

        time.sleep(1)

    print("[DEBUG] CLI wurde beendet.")

def nachrichtSenden(contacts_path, handle):
    """Fragt Empfänger + Nachricht ab und sendet per SLCP."""
    try:
        empfaenger = input("Empfänger: ").strip()
        if not empfaenger:
            print("Empfänger darf nicht leer sein ⚠️")
            return

        nachricht = input("Nachricht: ").strip()
        if not nachricht:
            print("Nachricht darf nicht leer sein ⚠️")
            return

        success = slcp_MSG(empfaenger, nachricht, contacts_path, handle)
        if success:
            print("Nachricht erfolgreich gesendet ✅")
        else:
            print("Nachricht konnte nicht gesendet werden ❌")

    except Exception as e:
        print(f"[FEHLER] Nachricht konnte nicht gesendet werden: {e}")
