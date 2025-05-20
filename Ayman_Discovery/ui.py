import time
from network import send_udp_broadcast

def start_cli():
    """
    Einfache CLI zur Interaktion mit dem Discovery-Dienst.
    """
    print("Discovery Test CLI:")
    print("1 - JOIN")
    print("2 - LEAVE")
    print("3 - WHO")
    print("q - Quit")

    while True:
        choice = input(">> ").strip()
        if choice == "1":
            send_udp_broadcast("JOIN Ayman 5000", 4000)
        elif choice == "2":
            send_udp_broadcast("LEAVE Ayman", 4000)
        elif choice == "3":
            send_udp_broadcast("WHO", 4000)
        elif choice == "q":
            break
        time.sleep(1)
