## network_process.py
import socket
import toml

def network_process(ui_queue, net_queue, config_path):
    config = toml.load(config_path)
    tcp_port = config["port"]
    handle = config["handle"]

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("", tcp_port))
    server.listen()

    ui_queue.put(f"[NETWORK] TCP listening on port {tcp_port}")

    server.setblocking(False)

    while True:
        try:
            conn, addr = server.accept()
            data = conn.recv(512)
            message = data.decode("utf-8")
            ui_queue.put(f"[MESSAGE from {addr}] {message}")
            conn.close()
        except BlockingIOError:
            pass

        while not net_queue.empty():
            cmd = net_queue.get()
            if cmd.startswith("MSG"):
                parts = cmd.split(" ", 2)
                if len(parts) == 3:
                    _, empfaenger, nachricht = parts
                    # Hier sollte später IP/Port des Empfängers aufgelöst werden
                    ui_queue.put(f"[NETWORK] Nachricht an {empfaenger} gesendet: {nachricht}")