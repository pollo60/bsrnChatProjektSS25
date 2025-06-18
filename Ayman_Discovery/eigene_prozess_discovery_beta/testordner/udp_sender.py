# udp_sender.py
import socket

def udp_sender(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), (ip, port))
    print(f"[GESENDET] An {ip}:{port} → {message}")

if __name__ == "__main__":
    ip = input("Ziel-IP eingeben (z. B. 192.168.0.11): ").strip()
    port = int(input("Ziel-Port eingeben (z. B. 5002): ").strip())
    message = input("Nachricht: ").strip()
    udp_sender(ip, port, message)
