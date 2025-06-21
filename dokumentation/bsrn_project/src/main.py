Doxygen-Regeln (für alle)
Pflicht für jede Funktion/Klasse:

python
def beispiel(a: int) -> bool:
    """Kurzbeschreibung (wird automatisch @brief).
    
    Args:
        a (int): Beschreibung des Parameters.
        
    Returns:
        bool: Beschreibung des Rückgabewerts.
        
    @note Wichtige Hinweise hier.
    @todo #42 Offene Aufgabe verlinken.
    """
Args/Returns: Immer angeben.

@note: Für Hinweise, @warning für kritische Infos.

(TOML-Konfig dokumentieren:

In Code (@param) und separater CONFIG.md.)
 

Workflow: Code/Dokumentation aktualisieren
Für Entwickler (code):
Lokal ändern:

git pull  # Aktuelle Version holen
# Code schreiben + Doxygen-Kommentare hinzufügen
git add src/mein_modul.py
git commit -m "Feature X mit Docs"
git push

(Doku-Verantwortung Fabian):
Doku generieren (lokal):

cd dokumentation/bsrn_project
doxygen doxyfile  # Aktualisiert docs/html/
git add docs/html/
git commit -m "Doku für Feature X"
git push
→ Automatisch online unter:
https://[team].github.io/bsrnChatProjektSS25/dokumentation/bsrn_project/docs/html/index.html
Syntax für die Dokumentation: (JAVA/Python)

Für eine gute Doxygen-Dokumentation solltest du die wichtigsten Kommentarbefehle verwenden, die Doxygen erkennt. Hier sind die 5 gängigsten Syntaxelemente, die du in deinem Code (z. B. in C++, Java oder Python) nutzen kannst: 

JAVA 
1.     /** … */ oder /// 

→ Für Dokumentationskommentare. 

Beispiel:

/** 
* Berechnet die Summe zweier Zahlen. 
* @param a Die erste Zahl. 
* @param b Die zweite Zahl. 
* @return Die Summe von a und b. 
*/ 
int add(int a, int b); 
 

Oder einzeilig: 

/// Diese Funktion gibt "Hallo Welt" aus. 
void hello(); 


Python 

1.     """ … """ (Triple-Quotes) oder # (für einzelne Zeilen) 

def add(a, b): 
    """ 
    Berechnet die Summe zweier Zahlen. 
    @param a: Die erste Zahl. 
    @param b: Die zweite Zahl. 
    @return: Die Summe von a und b. 
    """ 
    return a + b 
  

Oder einzeilig: 

# Diese Funktion gibt "Hallo Welt" aus. 
def hello(): 
    print("Hallo Welt") 

JAVA 
2.     @param 

→ Beschreibt einen Funktionsparameter. 

Beispiel: 

/// @param name Der Name der Person. 
void greet(std::string name); 

 

Python 

Beispiel: 

def greet(name): 
    """ 
    @param name: Der Name der Person. 
    """ 
    print(f"Hallo, {name}!") 
JAVA 

3.     @return 

→ Erklärt den Rückgabewert der Funktion. 

Beispiel: 

/// @return true, wenn die Datei geöffnet wurde. 
bool openFile(std::string filename); 

 Python 

Beispiel: 

def is_even(n): 
    """ 
    Prüft, ob eine Zahl gerade ist. 
    @param n: Die zu prüfende Zahl. 
    @return: True, wenn gerade; sonst False. 
    """ 
    return n % 2 == 0 
 

JAVA 

4.     @brief 

→ Kurze Zusammenfassung (erscheint z. B. in Übersichten). 

Beispiel: 

/** 
* @brief Führt einen Reset aller Werte durch. 
*/ 
void resetAll(); 

Python 

Beispiel: 

def reset_all(): 
    """ 
    @brief Führt einen Reset aller Werte durch. 
    """ 
   JAVA 

5.     @file 

→ Einleitungstext für eine ganze Datei (am Anfang einer Datei platzieren). 

Beispiel: 

/** 
* @file main.cpp 
* @brief Hauptmodul des Projekts mit dem Einstiegspunkt. 
*/ 

 Python 

Beispiel: 

""" 
@file main.py 
@brief Hauptmodul des Projekts mit dem Einstiegspunkt. 
""" 
  

Natürlich! Hier ist die gleiche Erklärung und Beispiele, aber angepasst für Python-Code unter Verwendung der Doxygen-kompatiblen Syntax: 


