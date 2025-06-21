## discovery_process.py
import socket
import toml
import time
import os

def discovery_process(ui_queue, disc_queue, config_path, kontakte):
    config = toml.load(config_path)
    handle = config["handle"]
    udp_port = config["whoisport"]
    local_port = config["port"]

    users = {handle: ("localhost", local_port)}  # sich selbst eintragen

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", udp_port))
    sock.setblocking(False)

    while True:
        # Eingehende UDP-Nachrichten behandeln
        try:
            data, addr = sock.recvfrom(512)
            message = data.decode("utf-8").strip()
            if message.startswith("JOIN"):
                _, name, port = message.split()
                users[name] = (addr[0], int(port))
                kontakte[name] = (addr[0], int(port))
                ui_queue.put(f"[DISCOVERY] {name} joined from {addr[0]}:{port}")
                if name != handle:
                    ui_queue.put(f"[INFO] Neuer Teilnehmer entdeckt: {name} ist dem Chat beigetreten.")

            elif message == "WHO":
                ui_queue.put(f"[DISCOVERY] WHO-Anfrage empfangen von {addr[0]}:{addr[1]}")
                known = ", ".join(f"{n} {ip} {p}" for n, (ip, p) in users.items())
                response = f"KNOWNUSERS {known}"
                sock.sendto(response.encode("utf-8"), addr)

            elif message.startswith("LEAVE"):
                _, name = message.split()
                users.pop(name, None)
                kontakte.pop(name, None)
                ui_queue.put(f"[DISCOVERY] {name} left the chat")

        except BlockingIOError:
            pass

        try:
            while not disc_queue.empty():
                cmd = disc_queue.get()
                if cmd == "WHO":
                    sock.sendto(b"WHO", ("255.255.255.255", udp_port))
                    ui_queue.put("[DISCOVERY] WHO-Anfrage gesendet.")
                    time.sleep(1.0)
                    kontakte.clear()
                    for name, (ip, port) in users.items():
                        kontakte[name] = (ip, port)
                    if kontakte:
                        ui_queue.put("[DISCOVERY] Bekannte Nutzer:")
                        for name, (ip, port) in kontakte.items():
                            ui_queue.put(f"  - {name} @ {ip}:{port}")
                    else:
                        ui_queue.put("[DISCOVERY] Keine Nutzer gefunden.")

                elif cmd == "KONTAKTE":
                    if kontakte:
                        ui_queue.put("[KONTAKTE] Aktuell gespeicherte Kontakte:")
                        for name, (ip, port) in kontakte.items():
                            ui_queue.put(f"  - {name} @ {ip}:{port}")
                    else:
                        ui_queue.put("[KONTAKTE] Noch keine Kontakte gespeichert. Bitte WHO ausführen.")

                elif cmd.startswith("JOIN"):
                    sock.sendto(cmd.encode("utf-8"), ("255.255.255.255", udp_port))
                    ui_queue.put("[DISCOVERY] JOIN-Nachricht gesendet.")
                elif cmd.startswith("LEAVE"):
                    sock.sendto(cmd.encode("utf-8"), ("255.255.255.255", udp_port))
                    ui_queue.put("[DISCOVERY] LEAVE-Nachricht gesendet.")

        except Exception as e:
            ui_queue.put(f"[DISCOVERY ERROR] {e}")
