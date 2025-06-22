import socket     # Für TCP-Verbindungen
import toml       # Zum Laden der Konfigurationsdatei
import os         # Für Dateioperationen (z. B. Bilder speichern)

# Netzwerkprozess zur Verarbeitung eingehender/ausgehender Nachrichten und Bilder
def network_process(ui_queue, net_queue, config_path, kontakte):
    # Konfiguration einlesen
    config = toml.load(config_path)
    tcp_port = config["port"]          # Lokaler Port für TCP-Verbindungen
    handle = config["handle"]          # Eigenes Handle (Benutzername)

    # TCP-Server-Socket erstellen und starten
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("", tcp_port))        # Bind an alle IPs auf diesem Port
    server.listen()                    # Eingehende Verbindungen annehmen
    server.settimeout(0.5)             # Timeout, damit wir nicht blockieren

    # Ausgabe an UI: Port bereit
    ui_queue.put(f"[NETWORK] TCP listening on port {tcp_port}")

    # Endlosschleife für eingehende Verbindungen und Befehle von der UI
    while True:
        # Eingehende Verbindung prüfen
        try:
            conn, addr = server.accept()
            header = conn.recv(512).decode("utf-8").strip()

            # Prüfen, ob es sich um einen Bildversand handelt
            if header.startswith("IMG"):
                try:
                    # Header parsen: IMG <filename> <size>
                    _, filename, size_str = header.split()
                    size = int(size_str)

                    # Bestätigung senden, dass Client senden darf
                    conn.sendall(b"READY")

                    # Binärdaten empfangen
                    image_data = b""
                    while len(image_data) < size:
                        chunk = conn.recv(min(4096, size - len(image_data)))
                        if not chunk:
                            break
                        image_data += chunk

                    # Bild lokal speichern
                    pfad = os.path.join(config["imagepath"], filename)
                    with open(pfad, "wb") as f:
                        f.write(image_data)

                    # Erfolgreich empfangen
                    ui_queue.put(f"[BILD] Empfangen: {filename} gespeichert unter {pfad}")

                except Exception as e:
                    ui_queue.put(f"[FEHLER] Bildempfang fehlgeschlagen: {e}")

            else:
                # Textnachricht empfangen (z. B. MSG)
                ui_queue.put(f"[MESSAGE from {addr}] {header}")

            conn.close()

        except socket.timeout:
            # Keine Verbindung -> einfach weitermachen
            pass

        # Eingehende Kommandos aus der UI bearbeiten
        while not net_queue.empty():
            cmd = net_queue.get()

            # Nachricht versenden: MSG <Handle> <Text>
            if cmd.startswith("MSG"):
                parts = cmd.split(" ", 2)
                if len(parts) == 3:
                    _, empfaenger, nachricht = parts
                    ip_port = kontakte.get(empfaenger)
                    if ip_port:
                        try:
                            ip, port = ip_port
                            # TCP-Verbindung zum Empfänger aufbauen
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

            # Bild senden: IMG_SEND <handle> <filename> <size> :: <pfad>
            elif cmd.startswith("IMG_SEND"):
                parts = cmd.split(" ", 1)[1].split("::")
                header, pfad = parts
                empfaenger, filename, size = header.split()[:3]
                size = int(size)
                ip_port = kontakte.get(empfaenger)

                if ip_port:
                    try:
                        ip, port = ip_port
                        # TCP-Verbindung öffnen
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect((ip, port))

                        # Header senden: z. B. IMG bild.png 20480
                        sock.sendall(f"IMG {filename} {size}\n".encode("utf-8"))

                        # Bestätigung vom Empfänger abwarten
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
