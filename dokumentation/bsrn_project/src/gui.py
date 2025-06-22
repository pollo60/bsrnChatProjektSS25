##
# @file gui.py
#
# @brief Grafische Benutzeroberfläche des Chatprogrammes
#
# Aufgaben: 
# 1. Sendet Bilder und Testnachrichten
# 2. Verarbeitet Chat Befehle wie JOIN
# 3. Ziegt TOML Userdaten und Kontakte an
# 4. Benutzer Betritt bei start automatisch den Chat
#
# Das GUI  dient als Interface for den Nutzer. 
# Es kümmert sich um, dass Einsehen von User und Kontaktdaten
# Des weiteren ermöglicht es, dass versendet es Nachichten und Bilder zwischen den Nutzern und
# kommuniziert mit discovery für Warteschlangen
#


import tkinter as tk #GUI tool
from tkinter import simpledialog, messagebox, scrolledtext, filedialog # Eingabefenster und Dialoge
import threading # für meherer Prozesse
import time # Timer
import os # Betriebssystem
from pathlib import Path # Ermöglicht/erleichtert das Datei finden
from queue import Empty # Verarbeitet Fehler bei Leeren Warteschlangen

class ChatGUI:
    """
    @brief Erzeugt GUI 
    @param root - Hauptfenster
    @param config path - TOML Konfig Pfad
    @param ui queue - Warteschlange für GUI
    @param discovery queue - Warteschlange für discovery Prozesse
    @param network queue - Wartechlange für network
    
    """
    def __init__(self, root, config_path, ui_queue, discovery_queue, network_queue):
        self.root = root # root auf das Hauptfenster
        self.config_path = config_path # TOML konfig Speicherort
        self.ui_queue = ui_queue 
        self.discovery_queue = discovery_queue 
        self.network_queue = network_queue
        
        # Config laden (TOML Userdaten)
        import toml
        self.config = toml.load(config_path)
        self.handle = self.config["handle"]
        self.port = self.config["port"]
        self.whoisport = self.config["whoisport"]
        self.imagepath = self.config["imagepath"]

        # Konfigueiert die Überschrift und Größe
        root.title(f"ICP Chat (SLCP) - {self.handle}")
        root.geometry("1000x800") # Pixel Anzahl

        # Textanzeige für Nachrichten
        self.output_box = scrolledtext.ScrolledText(root, height=20, wrap=tk.WORD)
        self.output_box.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.output_box.config(state=tk.DISABLED) #Output box als Eingabe deaktiviert

        # Nachrichteneingabe
        self.entry_frame = tk.Frame(root) # Feld für Empfänger
        self.entry_frame.pack(fill=tk.X, padx=10) # Feld für Nachrichten 

        self.recipient_var = tk.StringVar()
        self.message_var = tk.StringVar()

        tk.Label(self.entry_frame, text="Empfänger:").pack(side=tk.LEFT)
        self.recipient_entry = tk.Entry(self.entry_frame, textvariable=self.recipient_var, width=15)
        self.recipient_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(self.entry_frame, text="Nachricht:").pack(side=tk.LEFT)
        self.message_entry = tk.Entry(self.entry_frame, textvariable=self.message_var)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.message_entry.bind('<Return>', lambda e: self.send_message()) # Sendet Nachricht weiter bei Enter

        self.send_button = tk.Button(self.entry_frame, text="Senden", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=5)

        # Button-Leiste für Input Nachrichten wie JOIN oder WHO
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(padx=10, pady=5)
 
        # Liste von allen buttons mit Funktion
        buttons = [
            ("JOIN", self.join_network),
            ("LEAVE", self.leave_network),
            ("WHO", self.send_who),
            ("Kontakte", self.show_contacts),
            ("Bild senden", self.send_image),
            ("Konfig", self.show_config),
            ("Beenden", self.exit_program)
        ]
        #Erzeugt buttons
        for label, command in buttons:
            tk.Button(self.button_frame, text=label, command=command, width=12).pack(side=tk.LEFT, padx=5)

        # Nachrichtenanzeige in eigenem Thread
        self.running = True
        threading.Thread(target=self.update_output, daemon=True).start()

        # Automatisch joinen beim Start (1 Sekunde Verzögerung)
        self.root.after(1000, self.join_network)

    def log(self, text):
        """@brief Nachricht ins Ausgabefenster schreiben
           @param Nachrichten Text
        """
        self.output_box.config(state=tk.NORMAL) # entsperrt Ausgabe Feld
        timestamp = time.strftime("%H:%M:%S") # Zeigt Uhrzeit an
        self.output_box.insert(tk.END, f"[{timestamp}] {text}\n") # Fügt Nachricht hinzu
        self.output_box.see(tk.END) # Scrollt nach unten
        self.output_box.config(state=tk.DISABLED) # Out put erneut sperren

    def update_output(self):
        """@brief Thread für Nachrichtenanzeige"""
        while self.running:
            try:
                message = self.ui_queue.get(timeout=0.5) # Wartet auf Warteschlange
                self.log(message)
            except Empty:
                continue # Macht weiter wenn keine Nachricht in der Warteschlange ist

    def join_network(self):
        """@brief Dem Netzwerk beitreten"""
        join_cmd = f"JOIN {self.handle} {self.port}"
        self.discovery_queue.put(join_cmd)
        self.log("🟢 Dem Netzwerk beigetreten")

    def leave_network(self):
        """@brief Netzwerk verlassen"""
        leave_cmd = f"LEAVE {self.handle}"
        self.discovery_queue.put(leave_cmd)
        self.log("🔴 Netzwerk verlassen")

    def send_who(self):
        """@brief WHO-Anfrage senden"""
        self.discovery_queue.put("WHO")
        self.log("🔍 WHO-Anfrage gesendet")

    def show_contacts(self):
        """@brief Kontakte anzeigen"""
        self.discovery_queue.put("KONTAKTE")
        self.log("📋 Kontakte angezeigt")

    def send_message(self):
        """@brief Nachricht senden in die Warteschlange """
        empfaenger = self.recipient_var.get().strip()
        text = self.message_var.get().strip()
        
        if not empfaenger or not text:
            messagebox.showwarning("Fehler", "Empfänger und Nachricht dürfen nicht leer sein.")
            return
        
        # Nachricht an network_process/in wie Warteschlange senden
        msg_cmd = f"MSG {empfaenger} {text}"
        self.network_queue.put(msg_cmd) 
        
        # Eingabefeld leeren
        self.message_var.set("")
        self.log(f"📤 Nachricht an {empfaenger}: {text}")

    def send_image(self):
        """@brief Öffnet das Eingabefenster und verschickt Bilder """
        empfaenger = self.recipient_var.get().strip()
        if not empfaenger:
            empfaenger = simpledialog.askstring("Empfänger", "An wen soll das Bild gesendet werden?")
        
        if not empfaenger:
            return
        
        # Bilddatei auswählen
        file_path = filedialog.askopenfilename(
            title="Bild auswählen",
            filetypes=[
                ("Bilder", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("Alle Dateien", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        # Prüfen ob Datei existiert
        if not os.path.exists(file_path):
            messagebox.showerror("Fehler", "Datei nicht gefunden!")
            return
        
        try:
            # Dateigröße ermitteln
            file_size = os.path.getsize(file_path)
            filename = Path(file_path).name
            
            # Command für network_process erstellen
            img_cmd = f"IMG_SEND {empfaenger} {filename} {file_size}::{file_path}"
            self.network_queue.put(img_cmd)
            
            self.log(f"🖼️ Bild '{filename}' wird an {empfaenger} gesendet...")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Senden des Bildes:\n{e}")
            self.log(f"❌ Fehler beim Bildsenden: {e}")

    """@brief Ziegt den Inhalt der TOML konfig Dateien an"""
        
    def show_config(self):
        
        try:
            with open(self.config_path, 'r') as f:
                config_data = f.read()
            self._show_popup("🧩 Konfiguration", config_data)
        except Exception as e:
            messagebox.showerror("Fehler", f"Konfiguration konnte nicht geladen werden:\n{e}")
    """@brief Erstellt Eingabe Fenster
       @param title - Festnter Titel
       @param content - Zeigt den Text an
      """
    def _show_popup(self, title, content):
        
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("500x400")

        text_area = scrolledtext.ScrolledText(popup, wrap=tk.WORD)
        text_area.insert(tk.END, content)
        text_area.config(state=tk.DISABLED)
        text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        tk.Button(popup, text="Schließen", command=popup.destroy).pack(pady=5)
    """ @brief Beendet das Programm bei LEAVE"""
    def exit_program(self):
        
        self.leave_network()
        self.running = False
        self.log("👋 Anwendung wird beendet")
        self.root.after(1000, self.root.quit)

"""@brief GUI wird gestartet
    @param config path -Pfad für TOML kofig Dateien
    @param ui queue - Warteschlange für UI
    @param discovery queue - Warteschlange für discovery
    @param network queue - Warteschlange für network
    """
def start_gui(config_path, ui_queue, discovery_queue, network_queue):
    """GUI starten"""
    root = tk.Tk()
    app = ChatGUI(root, config_path, ui_queue, discovery_queue, network_queue)
    root.mainloop()

