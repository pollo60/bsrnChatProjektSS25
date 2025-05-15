# empfaenger.py

import toml
import socket
import threading
from Netzwerk_Kommunikation.sender import discoveryWHO




def bereitmachen():

    with open('configANSATZ.toml', 'r') as f:       # das r steht fuer read
      config = toml.load(f)
    PORT = int(config['login_daten']['port'])  
    IP = config['login_daten']['ip']


    BUFFER_SIZE = 1024


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))


    print(f"Dein Port ist: {PORT}.")





def empfangsschleife():
  
  with open('configANSATZ.toml', 'r') as f:
    config = toml.load(f)

  PORT = int(config['login_daten']['port'])
  IP = config['login_daten']['ip']
  BUFFER_SIZE = 1024

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind((IP, PORT))

  print(" Warte auf Nachrichten...")

  while True:
    daten, addr = sock.recvfrom(BUFFER_SIZE)
    nachricht = daten.decode("utf-8")
    print(f"Nachricht von {addr[0]}:{addr[1]} -> {nachricht}")



def netzwerkEmpfMain():   
  while True:
    bereitmachen() 
    discoveryWHO()
    thread = threading.Thread(target=empfangsschleife, daemon=True)
    thread.start()