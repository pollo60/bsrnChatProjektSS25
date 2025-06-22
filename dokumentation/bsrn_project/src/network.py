##
# @file  network_process.py

# Verwaltet jegliche Netzwerkkommunikation des Programmes

# Aufgaben:

# 1. Verschickt und empfängt Nachrichten und Bilder via TCP Verbindungen
# 2. Verwaltet den eigenen Port und Socket
# 3. Leitet Ereignisse an das User Interface weiter
# 4. Läd Konfig Userdaten aus TOML Dateien

# @details Dieses Programm wartet auf eigehende TCP Verbindungen wie Bilder oder Nachichten.
# Des weiteren läd es Userdaten aus den TOML Dateien und interagiert mit den User Interface
# für Befehle und Warteschlangen für andere Prozesse. 

# network_process.py
import socket     # Netzwerkkommunikation
import toml       # Läd TOML Userdaten
import os         # Zur Speicherung von Bildern

def find_available_port(start_port, max_attempts=100):
    """
    Sucht einen Start Port um eine Anfangsnummer zu finden

    @param start port - Startnummer des Ports
    @param max attempts - Maximale Anzahl der zu testenden Ports
    @return Gibt den ersten Port wieder der Gefunden wird, oder nichts
    
    """
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

def network_process(ui_queue, net_queue, config_path, kontakte):

    """
    Hauptfunktion des Netzwerkprozesses

    @param ui queue -für die Warteschlange die mit dem UI kommuniziert wird
    @param net queue -weitere Warteschlange die Infos an das UI weiterleitet
    @param config path -als Pfad für die TOML Userdaten
    @param kontakt -Liste mit bisher bekannten Usern
    
    """
    # Config wird eingelesen
    cfg = toml.load(config_path)
    configured_port = cfg["port"]     # Erst Konfigurierter Port     
    my_username = cfg["handle"]       # Eigener Username 

    # Automatisch verfügbaren Port finden
    listen_port = find_available_port(configured_port)
    if listen_port is None:
        # Sendet Error message an UI falls kein Port vorhanden ist
        ui_queue.put(f"[NETWORK ERROR] Kein verfügbarer Port ab {configured_port} gefunden!")
        return
    
    if listen_port != configured_port:
        # Sendet eine Nachricht an das User interface, dass ein anderer Port bereits benutzt wird
        ui_queue.put(f"[NETWORK INFO] Port {configured_port} belegt - verwende stattdessen Port {listen_port}")

    # erstellt einen TCP Server Socket
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_server.bind(("", listen_port))       # Bindet sich an alle User 
    tcp_server.listen()                      # Lauscht und nimmt Verbindungen an
    tcp_server.settimeout(0.5)               # Timeout timer

    ui_queue.put(f"[NETWORK] TCP Server läuft auf Port {listen_port}")
    
    # Loop für den Netzwerkprozess
    while True:
        # Sucht nach eingehenden Verbindungen
        try:
            client_conn, client_addr = tcp_server.accept()
            incoming_header = client_conn.recv(512).decode("utf-8").strip()

            # Lauscht ob Bilder übertragen wurden
            if incoming_header.startswith("IMG"):
                try:
                    # Regelt die Parameter für die Bilderkennung
                    parts = incoming_header.split()
                    image_filename = parts[1]
                    file_size = int(parts[2])

                    # OK senden wenn etwas Empfangen wurde
                    client_conn.sendall(b"READY")

                    # Bild wurde empfangen
                    received_data = b""
                    bytes_left = file_size
                    while bytes_left > 0:
                        chunk = client_conn.recv(min(4096, bytes_left))
                        if not chunk:
                            break
                        received_data += chunk
                        bytes_left -= len(chunk)

                    # Die Bilddatei wird lokal gespeichert
                    save_path = os.path.join(cfg["imagepath"], image_filename)
                    with open(save_path, "wb") as img_file:
                        img_file.write(received_data)

                    ui_queue.put(f"[BILD] Erhalten: {image_filename} -> {save_path}")

                except Exception as err:
                    ui_queue.put(f"[FEHLER] Bild empfangen ging schief: {err}")

            else:
                # normale text nachricht wird empfangen
                ui_queue.put(f"[NACHRICHT von {client_addr}] {incoming_header}")

            client_conn.close()

        except socket.timeout:
            # timeout ist ok, einfach weitermachen
            pass

        # Befehle aus der Warteschlange werden bearbeitet
        while not net_queue.empty():
            cmd = net_queue.get()

            # Nachricht senden: MSG <empfänger> <text>
            if cmd.startswith("MSG"):
                cmd_parts = cmd.split(" ", 2)
                if len(cmd_parts) == 3:
                    _, target_user, message_text = cmd_parts
                    target_info = kontakte.get(target_user)
                    if target_info:
                        try:
                            target_ip, target_port = target_info
                            # TCP connection zum Epfänger
                            send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            send_sock.connect((target_ip, target_port))
                            full_message = f"{my_username}: {message_text}"
                            send_sock.sendall(full_message.encode("utf-8"))
                            send_sock.close()
                            ui_queue.put(f"[NETWORK] Message an {target_user} gesendet: {message_text}")
                        except Exception as send_err:
                            ui_queue.put(f"[NETWORK ERROR] Senden an {target_user} failed: {send_err}")
                    else:
                        ui_queue.put(f"[NETWORK] {target_user} ist unbekannt. Erst WHO machen.")

            # Bild senden: IMG_SEND <handle> <filename> <size> :: <pfad>
            elif cmd.startswith("IMG_SEND"):
                try:
                    # Teilt header und Dateipfad auf
                    cmd_data = cmd.split(" ", 1)[1]
                    header_part, file_path = cmd_data.split("::")
                    header_tokens = header_part.split()
                    target_user = header_tokens[0]
                    filename = header_tokens[1]
                    filesize = int(header_tokens[2])
                    
                    target_info = kontakte.get(target_user)

                    if target_info:
                        target_ip, target_port = target_info
                        # TCP connection
                        send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        send_sock.connect((target_ip, target_port))

                        # Header senden
                        img_header = f"IMG {filename} {filesize}\n"
                        send_sock.sendall(img_header.encode("utf-8"))

                        # warten auf Bestätigung 
                        ack_response = send_sock.recv(16)
                        if ack_response == b"READY":
                            with open(file_path, "rb") as img_file:
                                send_sock.sendall(img_file.read())
                            ui_queue.put(f"[NETWORK] Bild an {target_user} gesendet: {filename}")
                        send_sock.close()
                    else:
                        ui_queue.put(f"[NETWORK] {target_user} unbekannt. WHO ausführen.")
                except Exception as img_err:
                    ui_queue.put(f"[NETWORK ERROR] Bildversand failed: {img_err}")