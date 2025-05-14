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
