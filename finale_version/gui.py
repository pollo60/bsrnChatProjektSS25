import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext, filedialog
import threading
import time
import os
from pathlib import Path
from queue import Empty

class ChatGUI:
    def __init__(self, root, config_path, ui_queue, discovery_queue, network_queue):
        self.root = root
        self.config_path = config_path
        self.ui_queue = ui_queue
        self.discovery_queue = discovery_queue
        self.network_queue = network_queue
        
        # Config laden
        import toml
        self.config = toml.load(config_path)
        self.handle = self.config["handle"]
        self.port = self.config["port"]
        self.whoisport = self.config["whoisport"]
        self.imagepath = self.config["imagepath"]

        root.title(f"ICP Chat (SLCP) - {self.handle}")
        root.geometry("1000x800")

        # Textanzeige für Nachrichten
        self.output_box = scrolledtext.ScrolledText(root, height=20, wrap=tk.WORD)
        self.output_box.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.output_box.config(state=tk.DISABLED)

        # Nachrichteneingabe
        self.entry_frame = tk.Frame(root)
        self.entry_frame.pack(fill=tk.X, padx=10)

        self.recipient_var = tk.StringVar()
        self.message_var = tk.StringVar()

        tk.Label(self.entry_frame, text="Empfänger:").pack(side=tk.LEFT)
        self.recipient_entry = tk.Entry(self.entry_frame, textvariable=self.recipient_var, width=15)
        self.recipient_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(self.entry_frame, text="Nachricht:").pack(side=tk.LEFT)
        self.message_entry = tk.Entry(self.entry_frame, textvariable=self.message_var)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.message_entry.bind('<Return>', lambda e: self.send_message())

        self.send_button = tk.Button(self.entry_frame, text="Senden", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=5)

        # Button-Leiste
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(padx=10, pady=5)

        buttons = [
            ("JOIN", self.join_network),
            ("LEAVE", self.leave_network),
            ("WHO", self.send_who),
            ("Kontakte", self.show_contacts),
            ("Bild senden", self.send_image),
            ("Konfig", self.show_config),
            ("Beenden", self.exit_program)
        ]

        for label, command in buttons:
            tk.Button(self.button_frame, text=label, command=command, width=12).pack(side=tk.LEFT, padx=5)

        # Nachrichtenanzeige in eigenem Thread
        self.running = True
        threading.Thread(target=self.update_output, daemon=True).start()

        # Automatisch joinen beim Start
        self.root.after(1000, self.join_network)

    def log(self, text):
        """Nachricht ins Ausgabefenster schreiben"""
        self.output_box.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S")
        self.output_box.insert(tk.END, f"[{timestamp}] {text}\n")
        self.output_box.see(tk.END)
        self.output_box.config(state=tk.DISABLED)

    def update_output(self):
        """Thread für Nachrichtenanzeige"""
        while self.running:
            try:
                message = self.ui_queue.get(timeout=0.5)
                self.log(message)
            except Empty:
                continue

    def join_network(self):
        """Dem Netzwerk beitreten"""
        join_cmd = f"JOIN {self.handle} {self.port}"
        self.discovery_queue.put(join_cmd)
        self.log("🟢 Dem Netzwerk beigetreten")

    def leave_network(self):
        """Netzwerk verlassen"""
        leave_cmd = f"LEAVE {self.handle}"
        self.discovery_queue.put(leave_cmd)
        self.log("🔴 Netzwerk verlassen")

    def send_who(self):
        """WHO-Anfrage senden"""
        self.discovery_queue.put("WHO")
        self.log("🔍 WHO-Anfrage gesendet")

    def show_contacts(self):
        """Kontakte anzeigen"""
        self.discovery_queue.put("KONTAKTE")
        self.log("📋 Kontakte angezeigt")

    def send_message(self):
        """Nachricht senden"""
        empfaenger = self.recipient_var.get().strip()
        text = self.message_var.get().strip()
        
        if not empfaenger or not text:
            messagebox.showwarning("Fehler", "Empfänger und Nachricht dürfen nicht leer sein.")
            return
        
        # Nachricht an network_process senden
        msg_cmd = f"MSG {empfaenger} {text}"
        self.network_queue.put(msg_cmd)
        
        # Eingabefeld leeren
        self.message_var.set("")
        self.log(f"📤 Nachricht an {empfaenger}: {text}")

    def send_image(self):
        """Bild senden"""
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

    def show_config(self):
        """Konfiguration anzeigen"""
        try:
            with open(self.config_path, 'r') as f:
                config_data = f.read()
            self._show_popup("🧩 Konfiguration", config_data)
        except Exception as e:
            messagebox.showerror("Fehler", f"Konfiguration konnte nicht geladen werden:\n{e}")

    def _show_popup(self, title, content):
        """Popup-Fenster anzeigen"""
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("500x400")

        text_area = scrolledtext.ScrolledText(popup, wrap=tk.WORD)
        text_area.insert(tk.END, content)
        text_area.config(state=tk.DISABLED)
        text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        tk.Button(popup, text="Schließen", command=popup.destroy).pack(pady=5)

    def exit_program(self):
        """Programm beenden"""
        self.leave_network()
        self.running = False
        self.log("👋 Anwendung wird beendet")
        self.root.after(1000, self.root.quit)

def start_gui(config_path, ui_queue, discovery_queue, network_queue):
    """GUI starten"""
    root = tk.Tk()
    app = ChatGUI(root, config_path, ui_queue, discovery_queue, network_queue)
    root.mainloop()