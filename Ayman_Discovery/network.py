import socket

def send_udp_broadcast(message, port):
    """
    Sendet eine UDP-Broadcast-Nachricht.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(message.encode(), ('255.255.255.255', port))
        print(f"[Network] Broadcast gesendet: {message}")
