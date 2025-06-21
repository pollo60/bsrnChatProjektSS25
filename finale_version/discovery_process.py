## discovery_process.py
import socket
import toml

def discovery_process(ui_queue, disc_queue, config_path):
    config = toml.load(config_path)
    handle = config["handle"]
    udp_port = config["whoisport"]

    users = {}

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", udp_port))

    while True:
        try:
            data, addr = sock.recvfrom(512)
            message = data.decode("utf-8").strip()
            if message.startswith("JOIN"):
                _, name, port = message.split()
                users[name] = (addr[0], int(port))
                ui_queue.put(f"[DISCOVERY] {name} joined from {addr[0]}:{port}")

            elif message == "WHO":
                known = ", ".join(f"{n} {ip} {p}" for n, (ip, p) in users.items())
                response = f"KNOWNUSERS {known}"
                sock.sendto(response.encode("utf-8"), addr)

            elif message.startswith("LEAVE"):
                _, name = message.split()
                users.pop(name, None)
                ui_queue.put(f"[DISCOVERY] {name} left the chat")

        except Exception as e:
            ui_queue.put(f"[DISCOVERY ERROR] {e}")
