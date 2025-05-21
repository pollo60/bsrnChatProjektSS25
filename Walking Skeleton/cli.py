import sys
import getpass
import os
import toml

# Pfad zur benutzerspezifischen Konfigurationsdatei definieren
# Im Ordner/.bsrnchat wird für jeden client eine individuelle Konfiguarationsdatei erstellt
def get_config_path():
    username = getpass.getuser()    # Mit den Funktionen aus getpass wird der Benutzer identifiziert
    config_dir = os.path.expanduser("~/.bsrnchat")  # Pfadangabe der Datei
    os.makedirs(config_dir, exist_ok=True)  # Erstellen des Verzeichnis falls noch nicht vorhanden
    return os.path.join(config_dir, f"config_{username}.toml")  # Ausgeben des Dateipfades

CONFIG_PATH = get_config_path() # Aufrufen der Funktion um den Dateipfad weiterverbinden zukönnen