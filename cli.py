
import sys
import socket

PORT = 4000
# Port des Discovery-Dienstes (gleicher wie im Server).

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Wir erstellen einen UDP-Socket

sock.setsockopt(socket.SOL_SOCKET, socket.S0_BROADCAST, 1)
# Aktiviert das Broadcast-Senden an 255.255.255.255.

sock.settimeout(2)
# Warte maximal 2 Sekunden auf Antwort, sonst weiter.




def zeige_menue():
    print("\n Menue:")
    print("1: \t WHO - Zeige Teilnehmer")
    print("2: \t MSG - Nachricht senden")
    print("3: \t EXIT - Beenden")





def WHO():
    print("-> WHO: Teilnehmer werden gesucht....")
    # CODE FUER NETZWERK (Broadcast ect.)
    
    sock.sendto(b"WHO" , ("255.255.255.255", PORT))
    # Wir senden den Befehl WHO als Bytes per UDP-Broadcast an alle.

    try:
        daten, addr = sock.recvfrom(1024)
        # Wartet auf Antwort vom Discovery-Dienst.

        print("Antwort vom Discovery-Dienst:", daten.decode())
        # Wandelt die empfangenen Bytes wieder in Text um.

    except socket.timeout:
        # Wenn keine Antwort kommt, zeigen wir eine Meldung.
        print("X Keine Antwort erhalten")





def MSG():
    empfaenger = input("Empfaenger: ")
    nachricht = input("Nachricht: ")
    print(f"-> Nachricht an {empfaenger}: {nachricht}")
    # Hier wuerde man eine Nachricht versenden



def main():

    print("Wilkommen! Was moechtest Du tun?")


    while True:
        zeige_menue()
        wahl = input("Gib eine Zahl ein (1-3): ").strip()

        if wahl == "1":
            WHO()
        elif wahl == "2":
            MSG()
        elif wahl == "3":
            print(" -> Programm wird beendet")
            sys.exit()
        else:
            print("Ungueltige eingabe. Bitte 1, 2 oder 3 eingeben.")




if __name__ == "__main__":
    main()





