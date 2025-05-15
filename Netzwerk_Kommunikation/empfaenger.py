# empfaenger.py

import toml
import socket
import threading
from Netzwerk_Kommunikation.sender import discoveryWHO

# kp mehr was das sollte
def bereitmachen():
  with open('configANSATZ.toml', 'r') as f:       # das r steht fuer read
      config = toml.load(f)
  PORT = int(config['login_daten']['port'])  
  IP = config['login_daten']['ip']
  #BUFFER_SIZE = 1024
 

# Hauptfunktion zum Empfang von Nachrichten über UDP
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

# ehrfache Starts verhindern
netzwerkEmpf = False

def netzwerkEmpfMain(): 
  global netzwerkEmpf
  if netzwerkEmpf:
      return
  netzwerkEmpf = True  

  # bereitmachen() 
  discoveryWHO() # Einmaliger WHO-Versand zur Teilnehmer-Suche

  thread = threading.Thread(target=empfangsschleife, daemon=True)
  thread.start()
  print("[Empfaenger-Thread wurde gestartet.]")

def discoveryWHO():
    try:
        with open('configANSATZ.toml', 'r') as f:
            config = toml.load(f)
        PORT = int(config['login_daten']['port'])   
        IPNETZ = config['login_daten']['ipnetz']  

        print("Teilnehmer werden gesucht.")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(3)

        sock.sendto(b"WHO", (IPNETZ, PORT))  # WHO-Befehl senden

        try:
            daten, addr = sock.recvfrom(1024)
            print("Antwort vom Discovery-Dienst: ", daten.decode())
        except socket.timeout:
            print("Keine Teilnehmer vorhanden.")
        finally:
            sock.close()

    except Exception as e:
        print("Fehler bei WHO: ", e)  # Fehlerausgabe
