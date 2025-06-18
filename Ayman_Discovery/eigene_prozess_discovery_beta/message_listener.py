# message_listener.py
import socket
import toml
from network_process import NetworkMessage
import threading

BUFFER_SIZE = 2048

def listen_for_messages(port):
    print(f"[Receiver] Warte auf Nachrichten auf Port {port} ...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))

    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            message = NetworkMessage.back_to_message(data)
            if message and message.validate():
                print(f"\n📩 Nachricht von {message.handle}@{addr[0]}: {message.content}")
            else:
                print(f"[WARNUNG] Ungültige oder fehlerhafte Nachricht von {addr}")
        except Exception as e:
            print(f"[Receiver] Fehler beim Empfang: {e}")
