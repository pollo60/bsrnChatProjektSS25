# discovery_process.py
import socket       
import toml         
import time         
import os           

def find_available_port(start_port, max_attempts=100):
    """Findet den nächsten verfügbaren Port ab start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            # Test ob Port verfügbar ist
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            test_sock.bind(("", port))
            test_sock.close()
            return port
        except OSError:
            continue
    return None

def discovery_process(ui_queue, disc_queue, config_path, kontakte):
    # Config laden
    config = toml.load(config_path)
    my_handle = config["handle"]            
    broadcast_port = config["whoisport"]       
    configured_tcp_port = config["port"]          

    # Automatisch verfügbaren Port finden
    my_tcp_port = find_available_port(configured_tcp_port)
    if my_tcp_port is None:
        ui_queue.put(f"[ERROR] Kein verfügbarer Port ab {configured_tcp_port} gefunden!")
        return
    
    if my_tcp_port != configured_tcp_port:
        ui_queue.put(f"[INFO] Port {configured_tcp_port} belegt - verwende stattdessen Port {my_tcp_port}")

    # IP rausfinden
    hostname = socket.gethostname()
    my_ip = socket.gethostbyname(hostname)
    ui_queue.put(f"[DEBUG] Meine IP: {my_ip}, Port: {my_tcp_port}")

    # Mich selbst zur Liste hinzufügen
    active_users = {my_handle: (my_ip, my_tcp_port)}
    kontakte[my_handle] = (my_ip, my_tcp_port)

    # Flag ob ich dem Chat beigetreten bin
    joined_chat = False

    # UDP Socket aufmachen für Broadcasts
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_sock.bind(("", broadcast_port))         
    udp_sock.setblocking(False)           

    # Main loop
    while True:
        # Schauen ob UDP Nachrichten da sind
        try:
            data, sender_addr = udp_sock.recvfrom(512)
            msg = data.decode("utf-8").strip()
            ui_queue.put(f"[DEBUG] UDP bekommen: {msg} von {sender_addr}")

            # Jemand will joinen
            if msg.startswith("JOIN"):
                _, username, port_str = msg.split()
                if username == my_handle:
                    continue  # meine eigene JOIN msg ignorieren
                active_users[username] = (sender_addr[0], int(port_str))
                kontakte[username] = (sender_addr[0], int(port_str))
                ui_queue.put(f"[DISCOVERY] {username} joined from {sender_addr[0]}:{port_str}")
                if username != my_handle and joined_chat:
                    ui_queue.put(f"[INFO] Neuer User online: {username} ist beigetreten.")

            # WHO Anfrage - jemand will wissen wer online ist
            elif msg == "WHO":
                ui_queue.put(f"[DISCOVERY] WHO request von {sender_addr[0]}:{sender_addr[1]}")
                user_list = ", ".join(f"{name} {ip} {port}" for name, (ip, port) in active_users.items())
                reply = f"KNOWNUSERS {user_list}"
                udp_sock.sendto(reply.encode("utf-8"), sender_addr)

            # Jemand verlässt den Chat
            elif msg.startswith("LEAVE"):
                _, leaving_user = msg.split()
                active_users.pop(leaving_user, None)
                kontakte.pop(leaving_user, None)
                ui_queue.put(f"[DISCOVERY] {leaving_user} hat den Chat verlassen")

        except BlockingIOError:
            pass  # nix da, weitermachen

        # Commands von der UI abarbeiten
        try:
            while not disc_queue.empty():
                command = disc_queue.get()

                # WHO broadcast senden
                if command == "WHO":
                    udp_sock.sendto(b"WHO", ("255.255.255.255", broadcast_port))  
                    ui_queue.put("[DISCOVERY] WHO broadcast gesendet.")
                    time.sleep(1.0)  # bisschen warten für antworten
                    kontakte.clear()
                    for name, (ip, port) in active_users.items():
                        kontakte[name] = (ip, port)
                    if kontakte:
                        ui_queue.put("[DISCOVERY] Online users:")
                        for name, (ip, port) in kontakte.items():
                            ui_queue.put(f"  - {name} @ {ip}:{port}")
                    else:
                        ui_queue.put("[DISCOVERY] Keiner online gefunden.")

                # Kontakte anzeigen
                elif command == "KONTAKTE":
                    if kontakte:
                        ui_queue.put("[KONTAKTE] Gespeicherte Kontakte:")
                        for name, (ip, port) in kontakte.items():
                            ui_queue.put(f"  - {name} @ {ip}:{port}")
                    else:
                        ui_queue.put("[KONTAKTE] Keine Kontakte da. Erst WHO machen.")

                # JOIN broadcast - mit automatisch gefundenem Port
                elif command.startswith("JOIN"):
                    # Original command format: "JOIN username port"
                    # Wir überschreiben den Port mit unserem automatisch gefundenen
                    cmd_parts = command.split()
                    username = cmd_parts[1]
                    join_msg = f"JOIN {username} {my_tcp_port}"
                    udp_sock.sendto(join_msg.encode("utf-8"), ("255.255.255.255", broadcast_port))
                    ui_queue.put(f"[DISCOVERY] JOIN broadcast gesendet mit Port {my_tcp_port}.")
                    joined_chat = True

                # LEAVE broadcast
                elif command.startswith("LEAVE"):
                    udp_sock.sendto(command.encode("utf-8"), ("255.255.255.255", broadcast_port))
                    ui_queue.put("[DISCOVERY] LEAVE broadcast gesendet.")

        except Exception as e:
            ui_queue.put(f"[DISCOVERY FEHLER] {e}")