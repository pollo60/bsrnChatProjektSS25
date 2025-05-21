import toml
from filelock import FileLock
import os

class ConfigHandler:
    def __init__(self, config_path="config_project.toml"):
        self.config_path = config_path
        # Erstelle leere Konfiguration, falls nicht existiert
        if not os.path.exists(self.config_path):
            self.write_config({
                "handle": "default_user",
                "port": 12345,
                "whoisport": 12346,
                "autoreply": True,
                "imagepath": "./images"
            })

    def read_config(self):
        """Liest die TOML-Konfigurationsdatei."""
        with FileLock(self.config_path + ".lock"):
            with open(self.config_path, "r") as file:
                return toml.load(file)

    def write_config(self, data):
        """Schreibt in die TOML-Konfigurationsdatei."""
        with FileLock(self.config_path + ".lock"):
            with open(self.config_path, "w") as file:
                toml.dump(data, file)

    def update

      def update_config(self, key, value):
        """Aktualisiert einen bestimmten Wert in der Konfigurationsdatei."""
        with FileLock(self.config_path + ".lock"):
            config = self.read_config()
            config[key] = value
            self.write_config(config)
