from discovery import DiscoveryService
from ui import start_cli

if __name__ == "__main__":
    discovery = DiscoveryService("config.toml")
    discovery.start()

    try:
        start_cli()
    except KeyboardInterrupt:
        print("\nBeende...")
    finally:
        discovery.stop()
