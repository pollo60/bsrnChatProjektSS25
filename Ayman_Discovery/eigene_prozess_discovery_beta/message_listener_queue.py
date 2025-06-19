# message_listener_queue.py
import socket
from network_process import NetworkMessage

BUFFER_SIZE = 2048

def listen_for_messages(port, output_queue):
    """
@brief Lauscht auf UDP Nachichten auf Port und gibt diese an Queue weiter

@param UDP Port zum Empfangen
@param Queue outputzur Ausgabe von Nachichten oder Fehlermeldungen

"""

#Erstelle UDP Socket
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Socket wird an Interface gebunden
    sock.bind(('', port))
    #output_queue.put(f"[Receiver] Lausche auf Port {port}...")


    while True:
        try:
            #Empfangen von Daten innerhalb von Buffergröße
            data, addr = sock.recvfrom(BUFFER_SIZE)
            message = NetworkMessage.back_to_message(data)
            if message and message.validate():
                # schreibt formatierte Nachichten in Ausgabe Queue um
                output_queue.put(f"📩 Nachricht von {message.handle}@{addr[0]}: {message.content}")
            else:
                # Fehlerausgabe bei ungültiger Nachicht
                output_queue.put(f"Ungültige Nachricht von {addr}")
        except Exception as e:
            output_queue.put(f"Fehler: {e}")
