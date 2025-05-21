import toml
import socket
import threading

def send_udp_broadcast(CONFIG_PATH, message):
    with open(CONFIG_PATH, 'r') as f:
        config = toml.load(f)
    
    PORT = int(config['login_daten']['port'])
    IPNETZ = config['login_daten']['ipnetz']

    addr = (IPNETZ, PORT)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    try:
        sock.sendto(message.encode("utf-8"), addr)
        print(f"[Network] Broadcast gesendet: {message}")
    except Exception as e:
        print(f"[Network] Fehler beim Senden: {e}")
    finally:
        sock.close()

def MSG(empfaenger, CONFIG_PATH):
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
    except FileNotFoundError:
        print("Konfigurationsdatei nicht gefunden.")
        return

    gesucht = empfaenger.strip().lower()
    key = next((k for k in config if k.lower() == gesucht), None)
    if key is None or key == 'login_daten':
        print(f"Empfänger '{empfaenger}' nicht gefunden. Verfügbare Kontakte: {[k for k in config if k!='login_daten']}")
        return

    data = config[key]
    ZIEL_IP = data['ziel_ip'].strip()
    ZIEL_PORT = int(str(data['ziel_port']).strip())

    nachricht = input("Nachricht: ").strip()

    print(f"[DEBUG] Sende Nachricht an {key} -> IP={ZIEL_IP}, Port={ZIEL_PORT}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(nachricht.encode("utf-8"), (ZIEL_IP, ZIEL_PORT))
        print(f"Nachricht an {ZIEL_IP}:{ZIEL_PORT} gesendet.")
    except Exception as e:
        print("Send-Error:", e)
    finally:
        sock.close()

def ermittle_ip_und_broadcast():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    broadcast = ip.rsplit('.', 1)[0] + '.255'
    return ip, broadcast

def netzwerkEmpfaenger(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = toml.load(f)
        
        login = config['login_daten']
        PORT = int(login['port'])
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', PORT))
        
        print(f"[Network] Empfange auf Port {PORT}...")
        
        while True:
            daten, addr = sock.recvfrom(1024)
            nachricht = daten.decode("utf-8")
            
            print(f"\nNachricht von {addr[0]}:{addr[1]}: {nachricht}")
            
            if nachricht == "WHO":
                try:
                    name = login['name']
                    ip = login['ip']
                    port = login['port']
                    antwort = f"{name}|{ip}|{port}"
                    sock.sendto(antwort.encode(), addr)
                    print(f"WHO-Antwort gesendet: {antwort}")
                except Exception as e:
                    print(f"Fehler beim Senden der WHO-Antwort: {e}")
                    
    except Exception as e:
        print(f"[Network] Fehler im Empfaenger: {e}")
    finally:
        sock.close()

def netzwerkEmpfMain(CONFIG_PATH):
    t = threading.Thread(target=netzwerkEmpfaenger, args=(CONFIG_PATH,), daemon=True)
    t.start()
    print("[Network] Empfänger-Thread gestartet")
    return t