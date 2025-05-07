
import sys




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








def zeige_menue():
    print("\n Menue:")
    print("1: \t WHO - Zeige Teilnehmer")
    print("2: \t MSG - Nachricht senden")
    print("3: \t EXIT - Beenden")





def WHO():
    print("-> WHO: Teilnehmer werden gesucht....")
    # CODE FUER NETZWERK (Broadcast ect.)



def MSG():
    empfaenger = input("Empfaenger: ")
    nachricht = input("Nachricht: ")
    print(f"-> Nachricht an {empfaenger}: {nachricht}")
    # Hier wuerde man eine Nachricht versenden