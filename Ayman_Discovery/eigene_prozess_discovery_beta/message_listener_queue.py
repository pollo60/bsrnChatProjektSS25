# message_listener_queue.py
import socket
from network_process import NetworkMessage

BUFFER_SIZE = 2048

def listen_for_messages(port, output_queue):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    output_queue.put(f"[Receiver] Lausche auf Port {port}...")

    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            message = NetworkMessage.back_to_message(data)
            if message and message.validate():
                output_queue.put(f"📩 Nachricht von {message.handle}@{addr[0]}: {message.content}")
            else:
                output_queue.put(f"[WARNUNG] Ungültige Nachricht von {addr}")
        except Exception as e:
            output_queue.put(f"[Receiver] Fehler: {e}")
