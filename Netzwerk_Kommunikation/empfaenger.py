# empfaenger.py

import toml
import socket



def bereitmachen():

    with open('configANSATZ.toml', 'r') as f:       # das r steht fuer read
                config = toml.load(f)
    PORT = config['port']
    IP = config['ip']


    BUFFER_SIZE = 1024


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(IP, PORT)


    print(f"Dein Port ist: {PORT}. Warte auf Nachrichten...")

    while True:
        daten, addr = socket.recvfrom(BUFFER_SIZE)
        nachricht = daten.decode("utf-8")
        print(f"Nachricht von {addr[0]}:{addr[1]} -> {nachricht}")
  
        return IP, PORT


def netzwerkEmpfMain():
       
       while True:
         bereitmachen() 
         sende_who()




def sende_who(port = PORT, timeout = 2):
      