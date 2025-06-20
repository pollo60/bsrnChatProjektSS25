# ui.py
import time
from network_process import send_slcp_broadcast, slcp_MSG
from config_utility import kontaktAnlegen, kontakteZeigen, check_for_contact_list, configAnzeigen
import json
def start_cli(auto=False, handle="", port=0, whoisport=4000, config_path="", contacts_path="", broadcast_ip="255.255.255.255",input_queue=None, message_queue=None):
    """
    @brief Startet die Kommandozeile

    @param JOIN und WHO werden gesendet
    @param handle Benutzername
    @param port Eigener Port
    @param whoisport Port für WHO-Anfragen
    @param config_path Pfad zur Konfigurationsdatei
    @param contacts path Pfad zur Kontaktliste
    @param broadcast_ip Broadcast-IP-Adresse
    @param input queue Queue für ausgehende Befehle
    @param message queue Queue für eingehende Nachrichten
    """
    if auto:
        send_slcp_broadcast("JOIN", handle, str(port), port=whoisport, broadcast_ip=broadcast_ip)
        time.sleep(1)
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

        # Nachrichten anzeigen
        while message_queue and not message_queue.empty():
            print(message_queue.get())

        choice = input("Eingabe: ").strip()

        if choice == "1":
            input_queue.put(("JOIN", handle, str(port)))
        elif choice == "2":
            input_queue.put(("LEAVE", handle, ""))
        elif choice == "3":
            input_queue.put(("WHO", handle, ""))
        elif choice == "4":
            check_for_contact_list(contacts_path)
            empfaenger = input("Name des Kontakts🆕: ").strip()
            if empfaenger:
                kontaktAnlegen(empfaenger, contacts_path)
        elif choice == "5":
            nachrichtSenden(contacts_path, handle, input_queue)
        elif choice == "6":
            kontakteZeigen(contacts_path)
        elif choice == "7":
            configAnzeigen(config_path)
        elif choice.lower() == "q":
            input_queue.put(("LEAVE", handle, ""))
            break
        else:
            print("Ungültige Eingabe ⚠️")

        time.sleep(0.5)

def nachrichtSenden(contacts_path, handle, input_queue):
    """@brief Liest Empänger und Nachihcten ein
    @param contacts path zur Kontaktliste
    @param handle Benutzername
    @param input queue für Befehle
    """
    empfaenger = input("Empfänger: ").strip()
    if not empfaenger:
        print("Empfänger darf nicht leer sein ⚠️")
        return
    nachricht = input("Nachricht: ").strip()
    if not nachricht:
        print("Nachricht darf nicht leer sein ⚠️")
        return
    #Bis hier her erstmal die Nachricht eingeben
    input_queue.put(("CHAT", handle, json.dumps({"empfaenger": empfaenger, "nachricht": nachricht, "contacts_path": contacts_path})))
