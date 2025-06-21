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

    while True:
        conn, addr = server.accept()
        data = conn.recv(512)
        message = data.decode("utf-8")
        ui_queue.put(f"[MESSAGE from {addr}] {message}")
        conn.close()
