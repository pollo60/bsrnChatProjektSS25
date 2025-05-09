import socket 
# Import das socket-Modul, um Netzwerkverbindungen zu ermöglichen (vergleichbar mit java.net.DatagramSocket in Java) 

PORT = 4000
BUFFER_SIZE = 1024
teilnehmer = {} # handle -> (ip, port)
# PORT: Der Port, der auf dem Dienst lauscht.
# BUFFER_SIZE: Max Anzahl an Bytes, die wir pro Nachricht empfangen
# teilnehmer: Ein Woerternbuch (Dictonary) - speichert bekannte Teilnehmer:
#             - Schluessel: Handle (z.B.: "Alice")
#             - Wert: ein Tupel aus IP und Port


sock =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', PORT))
# Erstellt einen UDP-Socket
# bind(('', PORT)): Wir binden den Socket an alle IP-Adressen ('') 
# und den gewählten Port (4000).



print(f"Discovery-Dienst lauscht auf PORT {PORT}...")
# Ausgabe zur Kontrolle: Der Dienst läuft und wartet.

while True:
    daten, addr = sock.recvfrom(BUFFER_SIZE)
    # Endlose Schleife: Warte auf eingehende Nachrichten
    # recvfrom(...) ist wie socket.receive(...) in Java: Liest Daten und gibt auch den Absender zurück (addr = (IP, Port)).

    nachricht = daten.decode('utf-8').strip()
    absender_ip, absender-port = addr
    # daten.decode(...): Wandelt die empfangenen Bytes in Text (UTF-8) um.
    # strip() entfernt Leerzeichen oder Zeilenumbrüche.
    # addr ist ein Tupel (IP, Port) → wir speichern IP und Port getrennt.

    print(f"Empfangen von {absender_ip} : {absender_port} -> {nachricht}")
    # Zeigt an, was empfangen wurde und von wem.

    teile = nachricht.split()
    if not teile:
        continue
    # Zerlegt den Text in Wörter (z. B. "JOIN Alice 5001" → ["JOIN", "Alice", "5001"])
    # Wenn die Nachricht leer ist, wird sie ignoriert

    befehl = teile[0]

    if befehl == "JOIN" and len(teile) == 3:
        handle = teile[1]
        port = teile [2]
        teilnehmer[handle] = (absender_ip, port)
        print(f" {handle} wurde hinzugefuegt: {absender_ip} : {port}")
    # JOIN ist der Befehl.
    # Der Client meldet sich an mit JOIN <Name> <Port>.
    # Wir speichern ihn im teilnehmer-Wörterbuch.

    elif befehl == "LEAVE" and len(teile) == 2:
        handle = teile[1]
        if handle in teilnehmer:
            del teilnehmer [handle]
            print(f" {handle} hat den Chat verlassen.")
    # Entfernt einen Client aus der Liste, wenn er sich abmeldet.

    elif befehl == "WHO":
        if teilnehmer:
            antwortteile = [f"{h} {ip} {port}" for h, (ip, port) in teilnehmer.items()]
            antwort = "KNOWNUSERS" + ",".join(antwortteile)
        else:
            antwort = "KNOWNUSERS"
        # Wenn ein Client WHO sendet, antworten wir mit KNOWNUSERS ...
        # Alle bekannten Teilnehmer werden aufgelistet: 
        # z. B. KNOWNUSERS Alice 192.168.0.5 5001, Bob ...

        sock.sendto(antwort.encode('utf-8'), addr)
        print(f"Antwort gesendet an {addr[0]} : {addr[1]} -> {antwort}")
        # Die Antwort wird zurück an den Absender geschickt.