import socket
import toml
import os


def network_process(ui_queue, net_queue, config_path, kontakte):
    config = toml.load(config_path)
    tcp_port = config["port"]
    handle = config["handle"]

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("", tcp_port))
    server.listen()
    server.settimeout(0.5)

    ui_queue.put(f"[NETWORK] TCP listening on port {tcp_port}")

    while True:
        try:
            conn, addr = server.accept()
            header = conn.recv(512).decode("utf-8").strip()
            if header.startswith("IMG"):
                try:
                    _, filename, size_str = header.split()
                    size = int(size_str)
                    conn.sendall(b"READY")
                    image_data = b""
                    while len(image_data) < size:
                        chunk = conn.recv(min(4096, size - len(image_data)))
                        if not chunk:
                            break
                        image_data += chunk
                    pfad = os.path.join(config["imagepath"], filename)
                    with open(pfad, "wb") as f:
                        f.write(image_data)
                    ui_queue.put(f"[BILD] Empfangen: {filename} gespeichert unter {pfad}")
                except Exception as e:
                    ui_queue.put(f"[FEHLER] Bildempfang fehlgeschlagen: {e}")
            else:
                ui_queue.put(f"[MESSAGE from {addr}] {header}")
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
                            sock.close()
                            ui_queue.put(f"[NETWORK] Nachricht an {empfaenger} gesendet: {nachricht}")
                        except Exception as e:
                            ui_queue.put(f"[NETWORK ERROR] Senden an {empfaenger} fehlgeschlagen: {e}")
                    else:
                        ui_queue.put(f"[NETWORK] Empfänger {empfaenger} unbekannt. Bitte WHO ausführen.")

            elif cmd.startswith("IMG_SEND"):
                parts = cmd.split(" ", 1)[1].split("::")
                header, pfad = parts
                empfaenger, filename, size = header.split()[:3]
                size = int(size)
                ip_port = kontakte.get(empfaenger)
                if ip_port:
                    try:
                        ip, port = ip_port
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect((ip, port))
                        sock.sendall(f"IMG {filename} {size}\n".encode("utf-8"))
                        ack = sock.recv(16)
                        if ack == b"READY":
                            with open(pfad, "rb") as f:
                                sock.sendall(f.read())
                            ui_queue.put(f"[NETWORK] Bild an {empfaenger} gesendet: {filename}")
                        sock.close()
                    except Exception as e:
                        ui_queue.put(f"[NETWORK ERROR] Bildversand an {empfaenger} fehlgeschlagen: {e}")
                else:
                    ui_queue.put(f"[NETWORK] Empfänger {empfaenger} unbekannt. Bitte WHO ausführen.")
