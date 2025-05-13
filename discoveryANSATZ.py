#discoveryANSATZ
import toml



def datenAufnehmen():
    login_daten = {} # Eine Hashmap mit allen login daten

    login_daten['name']   = input("Gib Deinen Namen ein:").strip() 
    login_daten['port']   = input("Gib deine Portnummer ein:").strip()
    login_daten['ip']     = "0.0.0.0" #platzhaler - kann spaeter durch socket ersetzt werden
    login_daten['hallo']  = input("Gib eine Automatische Wilkommensbotschaft fuer den Broadcast ins Netz ein:").strip()
    #Abfrage der Benutzerdaten zum Befüllen der Hashmap

    return login_daten

def inConfigSchreiben(login_daten):
    try:
        with open('config.toml', 'r') as f:       # das r steht fuer read
            config = toml.load(f)
        # Config-Datei laden

        config['login_daten'].update(login_daten)   #Config-Datei Inhalt veraendern

        with open('config.toml', 'w') as f:     # das w steht fuer write
            toml.dump(config, f)
            # in die Config-Datei schreiben
            print("Config-Datei wurde aktualisiert.")
        
    except Exception as e:
        print("Config Datei nicht gefunden!", e)




def zeigeConfig():
    try:
        with open('config.toml', 'r') as f:
            config = toml.load(f)
        # Config-Datei laden
        print(config['login_daten']['name'])
        print(config['login_daten']['port'])  
        print(config['login_daten']['ip']) 
        print(config['login_daten']['hallo'])    
        # Daten der Config Datei abrufen
    except:
        print("Config-Datei nicht gefunden!")



