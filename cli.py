#cliANSATZ
import sys

from discoveryANSATZ import datenAufnehmen, inConfigSchreiben, zeigeConfig, WHO, MSG, nachrichtSenden

from Netzwerk_Kommunikation.empfaenger import netzwerkEmpfMain



def zeige_menue():
    print("\n Menue:")
    print("1: \t WHO - Zeige Teilnehmer")
    print("2: \t MSG - Nachricht senden")
    print("3: \t EXIT - Beenden")
    print("4: \t Kontakt anlegen")

# Funktion zum Navigieren der Funktionen



def startup():
    zeigeConfig()
    login_daten = datenAufnehmen()
    inConfigSchreiben(login_daten)
    zeigeConfig()
# Funktion fuer den Start des Programs mit Login


def kontaktAnlegen(empfaenger):
    empfaenger = {} # Eine Hashmap mit allen login daten

    empfaenger['name']   = input("Gib den Namen ein:").strip() 
    empfaenger['port']   = input("Gib die Portnummer ein:").strip()
    empfaenger['ip']     = input("Gib die IP ein:").strip() #platzhaler - kann spaeter durch socket ersetzt werden
    #Abfrage der Benutzerdaten zum Befüllen der Hashmap

    inConfigSchreiben(empfaenger)
    zeigeConfig()






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
        wahl = input("Gib eine Zahl ein (1-4): ").strip()

        if wahl == "1":
            WHO()
        elif wahl == "2":
            nachrichtSenden()
        elif wahl == "3":
            print(" -> Programm wird beendet")
            sys.exit()
        elif wahl == "4":
            empfaenger = input("Name des Kontakts: ")
            kontaktAnlegen(empfaenger)
        else:
            print("Ungueltige eingabe. Bitte 1, 2, 3 oder 4 eingeben.")




if __name__ == "__main__":
    main()


