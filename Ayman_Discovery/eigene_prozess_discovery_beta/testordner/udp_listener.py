# udp_listener.py
import socket

def udp_listener(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    print(f"[UDP-LISTENER] Warte auf Nachrichten auf Port {port} ...")

    while True:
        data, addr = sock.recvfrom(2048)
        print(f"[EMPFANGEN] Von {addr}: {data.decode().strip()}")

if __name__ == "__main__":
    port = int(input("Port zum Lauschen eingeben (z. B. 5002): "))
    udp_listener(port)
