# empfaenger.py


import socket

PORT = 5000

BUFFER_SIZE = 1024


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind("0.0.0.0", PORT)


print(f"Dein Port ist: {PORT}. Warte auf Nachrichten...")

while True:
    daten, addr = socket.recvfrom(BUFFER_SIZE)
    nachricht = daten.decode("utf-8")
    print(f"Nachricht von {addr[0]}:{addr[1]} -> {nachricht}")
