#!/usr/bin/env python3
"""
Simple Main Window - Versione semplificata della finestra principale

Interfaccia tkinter semplificata che non richiede matplotlib,
per testare le funzionalità base della GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from pathlib import Path

try:
    # Import relativi (quando usato come modulo)
    from .file_selector import FileSelector
    from .project_manager import ProjectManager
    from .simple_viewer import SimpleImageViewer
    from .noise_controls import NoiseControls
except ImportError:
    # Import assoluti (quando eseguito direttamente)
    from file_selector import FileSelector
    from project_manager import ProjectManager
    from simple_viewer import SimpleImageViewer
    from noise_controls import NoiseControls


class SimpleMainWindow:
    """Finestra principale semplificata dell'applicazione"""
    
    def __init__(self):
        """Inizializza la finestra principale"""
        self.root = tk.Tk()
        self.root.title("Noise Generator - Versione Semplificata")
        self.root.geometry("1200x800")
        
        # Managers
        self.project_manager = ProjectManager()
        
        # Stato applicazione
        self.current_project_path = None
        
        self.setup_ui()
        self.setup_menu()
        
        # Gestione chiusura finestra
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Configura l'interfaccia utente"""
        # Frame principale con pannelli
        main_paned = ttk.PanedWindow(self.root, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Pannello sinistro - Controlli
        left_frame = ttk.Frame(main_paned, width=400)
        main_paned.add(left_frame, weight=1)
        
        # Pannello destro - Visualizzazione
        right_frame = ttk.Frame(main_paned, width=800)
        main_paned.add(right_frame, weight=2)
        
        # === PANNELLO SINISTRO ===
        
        # Selettore file
        self.file_selector = FileSelector(left_frame, self.on_selection_change, self.on_file_double_click)
        
        # Informazioni progetto
        self.setup_project_info(left_frame)
        
        # Controlli generazione rumore (semplificati)
        self.setup_simple_noise_controls(left_frame)
        
        # === PANNELLO DESTRO ===
        
        # Visualizzatore immagini semplificato
        self.image_viewer = SimpleImageViewer(right_frame)
        
        # Barra di stato
        self.setup_status_bar()
    
    def setup_project_info(self, parent):
        """Configura il pannello informazioni progetto"""
        self.project_frame = ttk.LabelFrame(parent, text="Progetto Corrente", padding=10)
        self.project_frame.pack(fill="x", padx=10, pady=5)
        
        # Nome progetto
        name_frame = ttk.Frame(self.project_frame)
        name_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(name_frame, text="Nome:").pack(side="left")
        self.project_name_var = tk.StringVar()
        self.project_name_entry = ttk.Entry(name_frame, textvariable=self.project_name_var)
        self.project_name_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Bottoni progetto
        buttons_frame = ttk.Frame(self.project_frame)
        buttons_frame.pack(fill="x")
        
        ttk.Button(buttons_frame, text="📁 Nuovo Progetto", 
                  command=self.create_new_project).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame, text="📂 Apri Cartella", 
                  command=self.open_project_folder).pack(side="left")
        
        # Info progetto
        self.project_info_label = ttk.Label(self.project_frame, 
                                           text="Nessun progetto attivo", 
                                           foreground="gray")
        self.project_info_label.pack(anchor="w", pady=(5, 0))
    
    def setup_simple_noise_controls(self, parent):
        """Configura controlli rumore semplificati"""
        noise_frame = ttk.LabelFrame(parent, text="Generazione Rumore (Demo)", padding=10)
        noise_frame.pack(fill="x", padx=10, pady=5)
        
        # Info
        info_label = ttk.Label(noise_frame, 
                              text="Funzionalità di generazione rumore\nnon disponibile in modalità semplificata.\n\nInstalla matplotlib per la versione completa.",
                              foreground="orange",
                              justify="center")
        info_label.pack(pady=10)
        
        # Bottone demo
        demo_button = ttk.Button(noise_frame, text="🎲 Demo Generazione", 
                                command=self.demo_noise_generation)
        demo_button.pack()
    
    def setup_status_bar(self):
        """Configura la barra di stato"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill="x", side="bottom")
        
        self.status_label = ttk.Label(self.status_frame, text="Pronto (Modalità Semplificata)")
        self.status_label.pack(side="left", padx=5)
        
        # Indicatore progetto
        self.project_status_label = ttk.Label(self.status_frame, text="Nessun progetto")
        self.project_status_label.pack(side="right", padx=5)
    
    def setup_menu(self):
        """Configura il menu principale"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Nuovo Progetto", command=self.create_new_project)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.on_closing)
        
        # Menu Visualizza
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualizza", menu=view_menu)
        view_menu.add_command(label="Apri Cartella Progetto", command=self.open_project_folder)
        
        # Menu Aiuto
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aiuto", menu=help_menu)
        help_menu.add_command(label="Info", command=self.show_about)
    
    def on_selection_change(self, selected_paths, selection_type):
        """Gestisce il cambio di selezione file"""
        self.log(f"Selezione: {selection_type} - {len(selected_paths)} elementi")

        # Se c'è una selezione e nessun progetto, crea automaticamente
        if selected_paths and not self.current_project_path:
            self.create_new_project()

        # Carica automaticamente la prima immagine nel visualizzatore
        self.load_first_image_in_viewer(selected_paths, selection_type)

    def load_first_image_in_viewer(self, selected_paths, selection_type):
        """Carica la prima immagine disponibile nel visualizzatore"""
        if not selected_paths:
            return

        try:
            first_image_path = None

            if selection_type == "single_file":
                first_image_path = selected_paths[0]
            elif selection_type == "multiple_files":
                first_image_path = selected_paths[0]
            elif selection_type == "folder":
                # Trova il primo file TIFF nella cartella
                tiff_files = self.file_selector._find_tiff_files(selected_paths[0])
                if tiff_files:
                    first_image_path = tiff_files[0]

            if first_image_path and os.path.exists(first_image_path):
                success = self.image_viewer.load_image(first_image_path)
                if success:
                    self.log(f"📷 Immagine caricata: {os.path.basename(first_image_path)}")
                else:
                    self.log(f"❌ Impossibile caricare: {os.path.basename(first_image_path)}")

        except Exception as e:
            self.log(f"❌ Errore caricamento immagine: {e}")

    def create_new_project(self):
        """Crea un nuovo progetto"""
        # Ottieni selezione corrente
        selected_paths, selection_type = self.file_selector.get_selection()
        
        # Nome progetto
        project_name = self.project_name_var.get().strip()
        if not project_name:
            project_name = None  # Auto-generato
        
        # Crea progetto
        try:
            project_path = self.project_manager.create_project(project_name, selected_paths)
            self.current_project_path = project_path

            # Imposta cartella visualizzazioni nel visualizzatore
            project_paths = self.project_manager.get_project_paths()
            if "visualizations" in project_paths:
                self.image_viewer.set_project_visualizations_dir(project_paths["visualizations"])

            # Aggiorna UI
            self.update_project_info()
            self.log(f"✅ Progetto creato: {os.path.basename(project_path)}")

        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile creare progetto:\n{e}")
    
    def update_project_info(self):
        """Aggiorna le informazioni del progetto"""
        if not self.current_project_path:
            self.project_info_label.config(text="Nessun progetto attivo", foreground="gray")
            self.project_status_label.config(text="Nessun progetto")
            return
        
        project_name = os.path.basename(self.current_project_path)
        source_info = self.project_manager.get_source_info()
        
        info_text = f"Cartella: {project_name}\n"
        info_text += f"Sorgenti: {source_info.get('type', 'N/A')} ({source_info.get('count', 0)})"
        
        self.project_info_label.config(text=info_text, foreground="blue")
        self.project_status_label.config(text=f"Progetto: {project_name}")
    
    def open_project_folder(self):
        """Apre la cartella del progetto corrente"""
        if not self.current_project_path:
            messagebox.showwarning("Attenzione", "Nessun progetto attivo")
            return
        
        try:
            os.startfile(self.current_project_path)  # Windows
        except AttributeError:
            os.system(f"xdg-open '{self.current_project_path}'")  # Linux

    def demo_noise_generation(self):
        """Demo della generazione rumore"""
        messagebox.showinfo("Demo Generazione Rumore", 
                           "Questa è una demo della funzionalità di generazione rumore.\n\n"
                           "Per utilizzare la versione completa:\n"
                           "1. Installa matplotlib: pip install matplotlib\n"
                           "2. Avvia con: python run_gui.py\n\n"
                           "La versione completa include:\n"
                           "• 8 tipi di rumore diversi\n"
                           "• Livelli configurabili\n"
                           "• Visualizzazioni avanzate (NDVI, RGB, etc.)\n"
                           "• Elaborazione batch")

    def on_file_double_click(self, file_path):
        """Gestisce doppio click su file per caricarlo nel visualizzatore"""
        try:
            success = self.image_viewer.load_image(file_path)
            if success:
                self.log(f"🖼️ Immagine caricata: {os.path.basename(file_path)}")
            else:
                self.log(f"❌ Impossibile caricare: {os.path.basename(file_path)}")
        except Exception as e:
            self.log(f"❌ Errore caricamento: {e}")
    
    def log(self, message):
        """Aggiunge messaggio al log"""
        print(f"[GUI Simple] {message}")
        self.root.update_idletasks()
    
    def show_about(self):
        """Mostra informazioni sull'applicazione"""
        about_text = """Noise Generator v1.0 - Modalità Semplificata
        
Versione semplificata per test delle funzionalità base
senza dipendenze avanzate come matplotlib.

Funzionalità disponibili:
• Caricamento immagini TIFF multispettrali
• Visualizzazione bande singole e RGB
• Gestione progetti
• Selezione file/cartelle

Per la versione completa installa matplotlib."""
        
        messagebox.showinfo("Informazioni", about_text)
    
    def on_closing(self):
        """Gestisce la chiusura dell'applicazione"""
        # Pulizia progetto vuoto
        if self.project_manager.current_project:
            self.project_manager.cleanup_empty_project()
        
        self.root.destroy()
    
    def run(self):
        """Avvia l'applicazione"""
        self.root.mainloop()


def launch_simple_gui():
    """Lancia l'interfaccia grafica semplificata"""
    app = SimpleMainWindow()
    app.run()


if __name__ == "__main__":
    launch_simple_gui()
