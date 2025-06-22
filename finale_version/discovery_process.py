import socket       # Für Netzwerkkommunikation (UDP-Sockets)
import toml         # Für das Einlesen der Konfigurationsdatei
import time         # Für kleine Wartezeiten (z. B. nach WHO-Anfrage)
import os           # (nicht verwendet, aber wird evtl. später gebraucht)

# Hauptfunktion des Discovery-Prozesses
def discovery_process(ui_queue, disc_queue, config_path, kontakte):
    # Konfiguration aus .toml-Datei laden
    config = toml.load(config_path)
    handle = config["handle"]            # Eigener Nutzername
    udp_port = config["whoisport"]       # Port für WHO-/JOIN-/LEAVE-Kommunikation
    local_port = config["port"]          # Eigener TCP-Port für direkte Kommunikation

    # Eigene IP-Adresse ermitteln und ausgeben
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    ui_queue.put(f"[DEBUG] Eigene IP-Adresse: {local_ip}")

    # Lokalen Nutzer zu Kontakt- und Userliste hinzufügen
    users = {handle: (local_ip, local_port)}
    kontakte[handle] = (local_ip, local_port)

    # Status-Flag, ob der Nutzer dem Chat beigetreten ist
    beigetreten = False

    # UDP-Socket für Broadcast öffnen
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", udp_port))         # Auf allen Schnittstellen lauschen
    sock.setblocking(False)           # Nicht blockierend – sofort weiterarbeiten

    # Endlosschleife zum Verarbeiten von eingehenden UDP-Nachrichten und Befehlen aus CLI
    while True:
        # Eingehende UDP-Nachrichten verarbeiten
        try:
            data, addr = sock.recvfrom(512)
            message = data.decode("utf-8").strip()
            ui_queue.put(f"[DEBUG] UDP empfangen: {message} von {addr}")

            # JOIN-Nachricht: neuer Nutzer möchte dem Chat beitreten
            if message.startswith("JOIN"):
                _, name, port = message.split()
                if name == handle:
                    continue  # Eigene JOIN-Nachricht ignorieren
                users[name] = (addr[0], int(port))
                kontakte[name] = (addr[0], int(port))
                ui_queue.put(f"[DISCOVERY] {name} joined from {addr[0]}:{port}")
                if name != handle and beigetreten:
                    ui_queue.put(f"[INFO] Neuer Teilnehmer entdeckt: {name} ist dem Chat beigetreten.")

            # WHO-Anfrage erhalten – andere Clients möchten wissen, wer online ist
            elif message == "WHO":
                ui_queue.put(f"[DISCOVERY] WHO-Anfrage empfangen von {addr[0]}:{addr[1]}")
                known = ", ".join(f"{n} {ip} {p}" for n, (ip, p) in users.items())
                response = f"KNOWNUSERS {known}"
                sock.sendto(response.encode("utf-8"), addr)

            # LEAVE-Nachricht – jemand verlässt den Chat
            elif message.startswith("LEAVE"):
                _, name = message.split()
                users.pop(name, None)
                kontakte.pop(name, None)
                ui_queue.put(f"[DISCOVERY] {name} left the chat")

        except BlockingIOError:
            pass  # Kein Datenpaket erhalten → einfach weitermachen

        # CLI-Kommandos aus disc_queue verarbeiten (JOIN, WHO, LEAVE, KONTAKTE)
        try:
            while not disc_queue.empty():
                cmd = disc_queue.get()

                # WHO-Anfrage ausgehend: wir wollen wissen, wer im Netzwerk aktiv ist
                if cmd == "WHO":
                    sock.sendto(b"WHO", ("255.255.255.255", udp_port))  # WHO an alle
                    ui_queue.put("[DISCOVERY] WHO-Anfrage gesendet.")
                    time.sleep(1.0)  # Warten, um Antworten zu sammeln
                    kontakte.clear()
                    for name, (ip, port) in users.items():
                        kontakte[name] = (ip, port)
                    if kontakte:
                        ui_queue.put("[DISCOVERY] Bekannte Nutzer:")
                        for name, (ip, port) in kontakte.items():
                            ui_queue.put(f"  - {name} @ {ip}:{port}")
                    else:
                        ui_queue.put("[DISCOVERY] Keine Nutzer gefunden.")

                # Kontaktliste anzeigen lassen
                elif cmd == "KONTAKTE":
                    if kontakte:
                        ui_queue.put("[KONTAKTE] Aktuell gespeicherte Kontakte:")
                        for name, (ip, port) in kontakte.items():
                            ui_queue.put(f"  - {name} @ {ip}:{port}")
                    else:
                        ui_queue.put("[KONTAKTE] Noch keine Kontakte gespeichert. Bitte WHO ausführen.")

                # JOIN-Befehl senden (wenn Nutzer dem Netzwerk beitritt)
                elif cmd.startswith("JOIN"):
                    sock.sendto(cmd.encode("utf-8"), ("255.255.255.255", udp_port))
                    ui_queue.put("[DISCOVERY] JOIN-Nachricht gesendet.")
                    beigetreten = True

                # LEAVE-Befehl senden (wenn Nutzer den Chat verlässt)
                elif cmd.startswith("LEAVE"):
                    sock.sendto(cmd.encode("utf-8"), ("255.255.255.255", udp_port))
                    ui_queue.put("[DISCOVERY] LEAVE-Nachricht gesendet.")

        except Exception as e:
            ui_queue.put(f"[DISCOVERY ERROR] {e}")