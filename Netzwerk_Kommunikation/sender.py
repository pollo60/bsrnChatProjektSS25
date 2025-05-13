
import socket

ZIEL_IP = "127.0.0.1"
ZIEL_PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

nachricht = input("Was moechtest du senden? ")
sock.sendto(nachricht.encode("utf-8"), (ZIEL_IP, ZIEL_PORT))

print(f" Nachricht gesendet an {ZIEL_IP}:{ZIEL_PORT}")