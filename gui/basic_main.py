#!/usr/bin/env python3
"""
Basic Main Window - Versione base della finestra principale

Interfaccia tkinter base che usa solo le librerie standard Python,
per testare la struttura della GUI senza dipendenze esterne.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from pathlib import Path

try:
    # Import relativi (quando usato come modulo)
    from .project_manager import ProjectManager
except ImportError:
    # Import assoluti (quando eseguito direttamente)
    from project_manager import ProjectManager


class BasicFileSelector:
    """Selettore file semplificato"""
    
    def __init__(self, parent, on_selection_change=None, on_file_double_click=None):
        self.parent = parent
        self.on_selection_change = on_selection_change
        self.on_file_double_click_callback = on_file_double_click
        self.selected_paths = []
        self.selection_type = "none"
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura l'interfaccia utente"""
        # Frame principale
        self.main_frame = ttk.LabelFrame(self.parent, text="Selezione File/Cartelle", padding=10)
        self.main_frame.pack(fill="x", padx=10, pady=5)
        
        # Bottoni selezione
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(buttons_frame, text="📄 File Singolo", command=self.select_single_file).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame, text="📄📄 File Multipli", command=self.select_multiple_files).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="📁 Cartella", command=self.select_folder).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="🗑️ Pulisci", command=self.clear_selection).pack(side="right")
        
        # Info selezione
        self.info_label = ttk.Label(self.main_frame, text="Nessuna selezione", foreground="gray")
        self.info_label.pack(anchor="w")
        
        # Lista file
        self.files_listbox = tk.Listbox(self.main_frame, height=6)
        self.files_listbox.pack(fill="both", expand=True, pady=(5, 0))
        self.files_listbox.bind("<Double-Button-1>", self.on_file_double_click)
    
    def select_single_file(self):
        """Seleziona un singolo file"""
        file_path = filedialog.askopenfilename(
            title="Seleziona Immagine TIFF",
            filetypes=[("File TIFF", "*.tif *.tiff"), ("Tutti i file", "*.*")]
        )
        if file_path:
            self.selected_paths = [file_path]
            self.selection_type = "single_file"
            self.update_preview()
            self._notify_change()
    
    def select_multiple_files(self):
        """Seleziona file multipli"""
        file_paths = filedialog.askopenfilenames(
            title="Seleziona Immagini TIFF",
            filetypes=[("File TIFF", "*.tif *.tiff"), ("Tutti i file", "*.*")]
        )
        if file_paths:
            self.selected_paths = list(file_paths)
            self.selection_type = "multiple_files"
            self.update_preview()
            self._notify_change()
    
    def select_folder(self):
        """Seleziona una cartella"""
        folder_path = filedialog.askdirectory(title="Seleziona Cartella con Immagini")
        if folder_path:
            self.selected_paths = [folder_path]
            self.selection_type = "folder"
            self.update_preview()
            self._notify_change()
    
    def clear_selection(self):
        """Pulisce la selezione"""
        self.selected_paths = []
        self.selection_type = "none"
        self.update_preview()
        self._notify_change()
    
    def update_preview(self):
        """Aggiorna la preview"""
        self.files_listbox.delete(0, tk.END)
        
        if not self.selected_paths:
            self.info_label.config(text="Nessuna selezione", foreground="gray")
            return
        
        if self.selection_type == "single_file":
            file_path = self.selected_paths[0]
            self.info_label.config(text=f"File: {os.path.basename(file_path)}", foreground="blue")
            self.files_listbox.insert(0, os.path.basename(file_path))
        elif self.selection_type == "multiple_files":
            count = len(self.selected_paths)
            self.info_label.config(text=f"File multipli: {count} selezionati", foreground="green")
            for path in self.selected_paths:
                self.files_listbox.insert(tk.END, os.path.basename(path))
        elif self.selection_type == "folder":
            folder_path = self.selected_paths[0]
            self.info_label.config(text=f"Cartella: {os.path.basename(folder_path)}", foreground="purple")
            self.files_listbox.insert(0, f"📁 {os.path.basename(folder_path)}")
    
    def on_file_double_click(self, event):
        """Gestisce doppio click"""
        selection = self.files_listbox.curselection()
        if not selection:
            return
        
        if self.selection_type == "single_file":
            file_path = self.selected_paths[0]
        elif self.selection_type == "multiple_files":
            index = selection[0]
            if index < len(self.selected_paths):
                file_path = self.selected_paths[index]
            else:
                return
        else:
            return
        
        if self.on_file_double_click_callback:
            self.on_file_double_click_callback(file_path)
    
    def _notify_change(self):
        """Notifica cambio selezione"""
        if self.on_selection_change:
            self.on_selection_change(self.selected_paths, self.selection_type)
    
    def get_selection(self):
        """Restituisce la selezione corrente"""
        return self.selected_paths, self.selection_type
    
    def has_selection(self):
        """Verifica se c'è una selezione"""
        return len(self.selected_paths) > 0


class BasicImageViewer:
    """Visualizzatore immagini base"""
    
    def __init__(self, parent, on_save_callback=None):
        self.parent = parent
        self.on_save_callback = on_save_callback
        self.current_file = None
        self.project_visualizations_dir = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura l'interfaccia"""
        self.main_frame = ttk.LabelFrame(self.parent, text="Visualizzatore (Base)", padding=5)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Controlli
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Button(controls_frame, text="📂 Carica", command=self.load_image_dialog).pack(side="left", padx=2)
        ttk.Button(controls_frame, text="📊 Info", command=self.show_image_info).pack(side="left", padx=2)
        
        # Area info
        self.info_text = tk.Text(self.main_frame, height=15, wrap="word")
        scrollbar = ttk.Scrollbar(self.main_frame, command=self.info_text.yview)
        self.info_text.config(yscrollcommand=scrollbar.set)
        
        self.info_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Messaggio iniziale
        self.info_text.insert("1.0", "Visualizzatore Base\n\n"
                                     "Questa versione mostra solo informazioni testuali\n"
                                     "sulle immagini caricate.\n\n"
                                     "Per visualizzazione completa delle immagini\n"
                                     "installa le dipendenze:\n"
                                     "• pip install matplotlib\n"
                                     "• pip install Pillow\n\n"
                                     "Carica un'immagine TIFF per vedere le informazioni.")
        self.info_text.config(state="disabled")
    
    def set_project_visualizations_dir(self, visualizations_dir):
        """Imposta cartella visualizzazioni"""
        self.project_visualizations_dir = visualizations_dir
    
    def load_image_dialog(self):
        """Dialog caricamento immagine"""
        file_path = filedialog.askopenfilename(
            title="Carica Immagine TIFF",
            filetypes=[("File TIFF", "*.tif *.tiff"), ("Tutti i file", "*.*")]
        )
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, file_path):
        """Carica immagine e mostra info"""
        try:
            import tifffile
            
            # Carica immagine
            image_data = tifffile.imread(file_path)
            self.current_file = file_path
            
            # Mostra informazioni
            self.info_text.config(state="normal")
            self.info_text.delete("1.0", tk.END)
            
            info = f"IMMAGINE CARICATA\n{'='*50}\n\n"
            info += f"File: {os.path.basename(file_path)}\n"
            info += f"Percorso: {file_path}\n\n"
            info += f"Dimensioni: {image_data.shape}\n"
            info += f"Tipo dati: {image_data.dtype}\n"
            
            if len(image_data.shape) == 3:
                info += f"Bande: {image_data.shape[0]}\n"
                info += f"Altezza: {image_data.shape[1]} pixel\n"
                info += f"Larghezza: {image_data.shape[2]} pixel\n\n"
                
                info += "STATISTICHE PER BANDA:\n"
                info += "-" * 30 + "\n"
                
                band_names = ["Blue (475nm)", "Green (560nm)", "Red (668nm)", 
                             "Red Edge (717nm)", "Near-IR (840nm)"]
                
                for i in range(min(image_data.shape[0], 5)):
                    band_data = image_data[i]
                    band_name = band_names[i] if i < len(band_names) else f"Banda {i+1}"
                    
                    info += f"\nBanda {i+1} - {band_name}:\n"
                    info += f"  Min: {band_data.min()}\n"
                    info += f"  Max: {band_data.max()}\n"
                    info += f"  Media: {band_data.mean():.2f}\n"
                    info += f"  Std Dev: {band_data.std():.2f}\n"
            else:
                info += f"Altezza: {image_data.shape[0]} pixel\n"
                info += f"Larghezza: {image_data.shape[1]} pixel\n\n"
                info += "STATISTICHE:\n"
                info += f"Min: {image_data.min()}\n"
                info += f"Max: {image_data.max()}\n"
                info += f"Media: {image_data.mean():.2f}\n"
            
            info += f"\n\nDimensione file: {os.path.getsize(file_path):,} bytes\n"
            
            self.info_text.insert("1.0", info)
            self.info_text.config(state="disabled")
            
            return True
            
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare l'immagine:\n{e}")
            return False
    
    def show_image_info(self):
        """Mostra info immagine"""
        if not self.current_file:
            messagebox.showwarning("Attenzione", "Nessuna immagine caricata")
        else:
            messagebox.showinfo("Info", f"Immagine corrente:\n{os.path.basename(self.current_file)}")


class BasicMainWindow:
    """Finestra principale base"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Noise Generator - Versione Base")
        self.root.geometry("1000x700")
        
        # Managers
        self.project_manager = ProjectManager()
        self.current_project_path = None
        
        self.setup_ui()
        self.setup_menu()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Configura UI"""
        # Pannelli
        main_paned = ttk.PanedWindow(self.root, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        left_frame = ttk.Frame(main_paned, width=350)
        main_paned.add(left_frame, weight=1)
        
        right_frame = ttk.Frame(main_paned, width=650)
        main_paned.add(right_frame, weight=2)
        
        # Componenti
        self.file_selector = BasicFileSelector(left_frame, self.on_selection_change, self.on_file_double_click)
        self.setup_project_info(left_frame)
        self.setup_demo_controls(left_frame)
        
        self.image_viewer = BasicImageViewer(right_frame)
        
        self.setup_status_bar()
    
    def setup_project_info(self, parent):
        """Info progetto"""
        self.project_frame = ttk.LabelFrame(parent, text="Progetto", padding=10)
        self.project_frame.pack(fill="x", padx=10, pady=5)
        
        name_frame = ttk.Frame(self.project_frame)
        name_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(name_frame, text="Nome:").pack(side="left")
        self.project_name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.project_name_var).pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        buttons_frame = ttk.Frame(self.project_frame)
        buttons_frame.pack(fill="x")
        
        ttk.Button(buttons_frame, text="📁 Nuovo", command=self.create_new_project).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame, text="📂 Apri", command=self.open_project_folder).pack(side="left")
        
        self.project_info_label = ttk.Label(self.project_frame, text="Nessun progetto", foreground="gray")
        self.project_info_label.pack(anchor="w", pady=(5, 0))
    
    def setup_demo_controls(self, parent):
        """Controlli demo"""
        demo_frame = ttk.LabelFrame(parent, text="Demo Funzionalità", padding=10)
        demo_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(demo_frame, text="Versione base per test struttura GUI", 
                 foreground="blue", justify="center").pack(pady=5)
        
        ttk.Button(demo_frame, text="🎲 Demo Rumore", command=self.demo_noise).pack(pady=2)
        ttk.Button(demo_frame, text="📊 Demo Analisi", command=self.demo_analysis).pack(pady=2)
    
    def setup_status_bar(self):
        """Barra stato"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill="x", side="bottom")
        
        self.status_label = ttk.Label(self.status_frame, text="Pronto (Versione Base)")
        self.status_label.pack(side="left", padx=5)
        
        self.project_status_label = ttk.Label(self.status_frame, text="Nessun progetto")
        self.project_status_label.pack(side="right", padx=5)
    
    def setup_menu(self):
        """Menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Nuovo Progetto", command=self.create_new_project)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.on_closing)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aiuto", menu=help_menu)
        help_menu.add_command(label="Info", command=self.show_about)
    
    def on_selection_change(self, selected_paths, selection_type):
        """Cambio selezione"""
        print(f"Selezione: {selection_type} - {len(selected_paths)} elementi")
        if selected_paths and not self.current_project_path:
            self.create_new_project()
    
    def on_file_double_click(self, file_path):
        """Doppio click file"""
        self.image_viewer.load_image(file_path)
    
    def create_new_project(self):
        """Nuovo progetto"""
        try:
            selected_paths, _ = self.file_selector.get_selection()
            project_name = self.project_name_var.get().strip() or None
            
            project_path = self.project_manager.create_project(project_name, selected_paths)
            self.current_project_path = project_path
            
            project_paths = self.project_manager.get_project_paths()
            if "visualizations" in project_paths:
                self.image_viewer.set_project_visualizations_dir(project_paths["visualizations"])
            
            self.update_project_info()
            print(f"✅ Progetto creato: {os.path.basename(project_path)}")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile creare progetto:\n{e}")
    
    def update_project_info(self):
        """Aggiorna info progetto"""
        if not self.current_project_path:
            self.project_info_label.config(text="Nessun progetto", foreground="gray")
            self.project_status_label.config(text="Nessun progetto")
            return
        
        project_name = os.path.basename(self.current_project_path)
        source_info = self.project_manager.get_source_info()
        
        info_text = f"Cartella: {project_name}\nSorgenti: {source_info.get('type', 'N/A')} ({source_info.get('count', 0)})"
        
        self.project_info_label.config(text=info_text, foreground="blue")
        self.project_status_label.config(text=f"Progetto: {project_name}")
    
    def open_project_folder(self):
        """Apri cartella progetto"""
        if not self.current_project_path:
            messagebox.showwarning("Attenzione", "Nessun progetto attivo")
            return
        
        try:
            os.startfile(self.current_project_path)  # Windows
        except AttributeError:
            os.system(f"xdg-open '{self.current_project_path}'")  # Linux
    
    def demo_noise(self):
        """Demo rumore"""
        messagebox.showinfo("Demo Rumore", 
                           "Demo generazione rumore:\n\n"
                           "• 8 tipi di rumore disponibili\n"
                           "• Livelli configurabili 1-20\n"
                           "• Elaborazione batch\n"
                           "• Output organizzato per tipo\n\n"
                           "Installa dipendenze per versione completa:\n"
                           "pip install matplotlib opencv-python")
    
    def demo_analysis(self):
        """Demo analisi"""
        messagebox.showinfo("Demo Analisi", 
                           "Demo analisi immagini:\n\n"
                           "• Visualizzazione multispettrale\n"
                           "• Calcolo NDVI\n"
                           "• Composizioni RGB\n"
                           "• Statistiche per banda\n\n"
                           "Funzionalità base disponibile anche\n"
                           "in questa versione!")
    
    def show_about(self):
        """Info applicazione"""
        about_text = """Noise Generator v1.0 - Versione Base

Versione base per test della struttura GUI
usando solo librerie standard Python.

Funzionalità disponibili:
• Gestione progetti
• Selezione file/cartelle  
• Informazioni immagini TIFF
• Struttura GUI completa

Per funzionalità complete installa:
pip install matplotlib opencv-python Pillow"""
        
        messagebox.showinfo("Informazioni", about_text)
    
    def on_closing(self):
        """Chiusura"""
        if self.project_manager.current_project:
            self.project_manager.cleanup_empty_project()
        self.root.destroy()
    
    def run(self):
        """Avvia applicazione"""
        self.root.mainloop()


def launch_basic_gui():
    """Lancia GUI base"""
    app = BasicMainWindow()
    app.run()


if __name__ == "__main__":
    launch_basic_gui()
