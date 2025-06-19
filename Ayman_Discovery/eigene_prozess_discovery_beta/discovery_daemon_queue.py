# discovery_daemon_queue.py
import socket # Für Netzwerk-Kommunikation mit UDP
import toml # Liest TOML Datein ein
import time # Zeitfunktion (noch nicht im gebrauch ?)
import json # Zum speichern der Teilnehmer Listen in JSON Format
import os # Für Dateioperationen

BUFFER_SIZE = 1024 # Puffergröße der eigehenden UDP-Nachichten
COMM_FILE = "discovery_output.json" # Datei zum Speichern der aktives Clients

def run_discovery(config_path, output_queue):
    """
    @brief Startet Discovery Dienst zur Verwaltung von Teilnehmern

    Funktion läd Konfig aus TOML Dateien (Nutzer daten),- und öffnet UDP Socket um auf
    Discovery Nachichten zu lauschen. 
    Verarbeitet außerdem join, leave und who Nachichten und aktualiesiert die client Dienste + 
    return per Queue.

    @param config path zur Konfig TOML Datei
    @param output que zur kommunikation

    """
    # Lade Konfig Datei
    with open(config_path, 'r', encoding="utf-8") as f:
        config = toml.load(f)

    # Extrahiere Login Daten aus Konfig
    login = config['login_daten']
    whoisport = int(login['whoisport'])
    my_handle = login['name']
    my_port = int(login['port'])

    # Erstellt und konfiguriert UDP Socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", whoisport))

    # print(f"[DISCOVERY] Lausche auf Port {whoisport}...")
    # Verwaltung der Clients
    clients = {}

    while True:
        try:
            # Warte auf UDP Packete
            data, addr = sock.recvfrom(BUFFER_SIZE)
            msg = data.decode().strip() # Dekodiert Nachichten
            print(f"Von {addr}: {msg}") # Debug Ausgabe
            parts = msg.split()
            if not parts:
                continue # Leere Nachichten ignorieren

            cmd = parts[0].upper() # Initialisiere Befehle join, leave und who
            if cmd == "JOIN" and len(parts) == 3:
                # Neuer Client tritt bei
                h, p = parts[1], int(parts[2])
                clients[h] = (addr[0], p) # IP Adresse wird angezeigt
                save_clients(clients)
                output_queue.put(f"{h} ist beigetreten ({addr[0]}:{p})")

            elif cmd == "LEAVE" and len(parts) == 2:
                # Ein Client verlässt das Netzwerrk
                h = parts[1]
                clients.pop(h, None) # Entferne Client
                save_clients(clients)
                output_queue.put(f"{h} hat das Netzwerk verlassen.")

            elif cmd == "WHO":
                # Who Anfrage beantworten
                response = f"JOIN {my_handle} {my_port}"
                sock.sendto(response.encode(), addr)

        except Exception as e:
            # Fehler an die Hauptanwendung senden
            output_queue.put(f"Fehler: {e}")

def save_clients(clients):

    """
    @brief Speichert Liste aller Cleients in JSON Datei
    
    Datei zeigt aktive Benutzer an

    @param erstellt eine Liste mit zugehörigen Handles und IP Port

    """
    try:
        with open(COMM_FILE, 'w') as f:
            json.dump(clients, f)
    except Exception as e:
        print("Fehler beim Speichern:", e)
