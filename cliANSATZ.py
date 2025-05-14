#cliANSATZ
import sys

from discoveryANSATZ import datenAufnehmen, inConfigSchreiben, zeigeConfig, WHO, MSG

from Netzwerk_Kommunikation.empfaenger import netzwerkEmpfMain



def zeige_menue():
    print("\n Menue:")
    print("1: \t WHO - Zeige Teilnehmer")
    print("2: \t MSG - Nachricht senden")
    print("3: \t EXIT - Beenden")
# Funktion zum Navigieren der Funktionen



def startup():
    zeigeConfig()
    login_daten = datenAufnehmen()
    inConfigSchreiben(login_daten)
    zeigeConfig()
# Funktion fuer den Start des Programs mit Login



def main():

    start = input(f"Zum Login y und dann ENTER drücken.   ").strip()

    if start == "y":
        startup()
        netzwerkEmpfMain()

    else:
        print(" -> Programm wird beendet")
        sys.exit()


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





