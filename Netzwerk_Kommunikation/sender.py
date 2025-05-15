
import socket
import toml


def MSG(empfaenger):

    with open('configANSATZ.toml', 'r') as f:
        config = toml.load(f)


    ZIEL_IP =  print(config['empfaenger)']['ziel_ip'])
    ZIEL_PORT = print(config['empfaenger']['ziel_port'])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    nachricht = input("Was moechtest du senden? ")
    sock.sendto(nachricht.encode("utf-8"), (ZIEL_IP, ZIEL_PORT))

    print(f" Nachricht gesendet an {ZIEL_IP}:{ZIEL_PORT}")





def discoveryWHO():
# CODE FUER NETZWERK (Broadcast ect.)

    try:

        with open('configANSATZ.toml', 'r') as f:
            config = toml.load(f)
        PORT = int(config['login_daten']['port'])   
        IPNETZ = int(config['login_daten']['ipnetz'])  
        # PORT und IP aus Konfigurationsdatei lesen 

        print("Teilnehmer werden gesucht.")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(3)



        sock.sendto(b"WHO" , (IPNETZ, PORT))
        # Wir senden den Befehl WHO als Bytes per UDP-Broadcast an alle.

        try:
            daten, addr = sock.receivefrom(1024)
            print("Antwort vom Discovery-Dienst: " , daten.decode())
        except socket.timeout:
            print("Keine Teilnehmer vorhanden.")
        finally:
            sock.close()

    except Exception as e:
        print("Fehler bei WHO: ", e)
        # e ist der Variablenname der Exception