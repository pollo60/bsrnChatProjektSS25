## network_process.py
import socket
import toml

def network_process(ui_queue, net_queue, config_path, kontakte):
    config = toml.load(config_path)
    tcp_port = config["port"]
    handle = config["handle"]

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("", tcp_port))
    server.listen()

    ui_queue.put(f"[NETWORK] TCP listening on port {tcp_port}")

    server.settimeout(0.5)

    while True:
        try:
            conn, addr = server.accept()
            data = conn.recv(512)
            message = data.decode("utf-8")
            ui_queue.put(f"[MESSAGE from {addr}] {message}")
            conn.close()
        except socket.timeout:
            pass

        while not net_queue.empty():
            cmd = net_queue.get()
            if cmd.startswith("MSG"):
                parts = cmd.split(" ", 2)
                if len(parts) == 3:
                    _, empfaenger, nachricht = parts
                    ip_port = kontakte.get(empfaenger)
                    if ip_port:
                        try:
                            ip, port = ip_port
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.connect((ip, port))
                            nachricht_mit_name = f"{handle}: {nachricht}"
                            sock.sendall(nachricht_mit_name.encode("utf-8"))
                            ui_queue.put(f"[DEBUG] TCP gesendet an {ip}:{port} -> {nachricht_mit_name}")
                            sock.close()
                            ui_queue.put(f"[NETWORK] Nachricht an {empfaenger} gesendet: {nachricht}")
                        except Exception as e:
                            ui_queue.put(f"[NETWORK ERROR] Senden an {empfaenger} fehlgeschlagen: {e}")
                    else:
                        ui_queue.put(f"[NETWORK] Empfänger {empfaenger} unbekannt. Bitte WHO ausführen.")
