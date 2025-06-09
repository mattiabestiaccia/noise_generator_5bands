#!/usr/bin/env python3
"""
Main Window - Finestra principale dell'interfaccia Noise Generator

Interfaccia tkinter principale che integra selezione file, gestione progetti,
generazione rumore e visualizzazione per immagini multispettrali.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
from pathlib import Path

try:
    # Import relativi (quando usato come modulo)
    from .file_selector import FileSelector
    from .project_manager import ProjectManager
    from .image_viewer import ImageViewer
    from .noise_controls import NoiseControls
except ImportError:
    # Import assoluti (quando eseguito direttamente)
    from file_selector import FileSelector
    from project_manager import ProjectManager
    from image_viewer import ImageViewer
    from noise_controls import NoiseControls

# Import del generatore di rumore
try:
    from ..scripts.add_noise_to_images import NoiseGenerator, load_multiband_image, save_multiband_image
except ImportError:
    try:
        from scripts.add_noise_to_images import NoiseGenerator, load_multiband_image, save_multiband_image
    except ImportError:
        # Fallback se non disponibile
        NoiseGenerator = None
        load_multiband_image = None
        save_multiband_image = None


class MainWindow:
    """Finestra principale dell'applicazione"""
    
    def __init__(self):
        """Inizializza la finestra principale"""
        self.root = tk.Tk()
        self.root.title("Noise Generator - Generazione Rumore Multispettrale")
        self.root.geometry("1400x900")
        
        # Managers
        self.project_manager = ProjectManager()
        if NoiseGenerator:
            self.noise_generator = NoiseGenerator()
        else:
            self.noise_generator = None
            messagebox.showerror("Errore", "Modulo NoiseGenerator non disponibile")
        
        # Stato applicazione
        self.current_project_path = None
        self.generation_active = False
        
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
        left_frame = ttk.Frame(main_paned, width=450)
        main_paned.add(left_frame, weight=1)
        
        # Pannello destro - Visualizzazione
        right_frame = ttk.Frame(main_paned, width=950)
        main_paned.add(right_frame, weight=2)
        
        # === PANNELLO SINISTRO ===
        
        # Selettore file
        self.file_selector = FileSelector(left_frame, self.on_selection_change, self.on_file_double_click)
        
        # Informazioni progetto
        self.setup_project_info(left_frame)
        
        # Controlli generazione rumore
        self.noise_controls = NoiseControls(left_frame, self.on_generate_noise)
        
        # === PANNELLO DESTRO ===
        
        # Visualizzatore immagini
        self.image_viewer = ImageViewer(right_frame, self.on_visualization_saved)
        
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
                  command=self.open_project_folder).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame, text="🎲 Apri Output",
                  command=self.open_noisy_images_folder).pack(side="left")
        
        # Info progetto
        self.project_info_label = ttk.Label(self.project_frame, 
                                           text="Nessun progetto attivo", 
                                           foreground="gray")
        self.project_info_label.pack(anchor="w", pady=(5, 0))
    
    def setup_status_bar(self):
        """Configura la barra di stato"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill="x", side="bottom")
        
        self.status_label = ttk.Label(self.status_frame, text="Pronto")
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
        view_menu.add_command(label="Apri Cartella Immagini Rumorose", command=self.open_noisy_images_folder)
        
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
        info_text += f"Sorgenti: {source_info.get('type', 'N/A')} ({source_info.get('count', 0)})\n"
        info_text += f"📁 Output: {project_name}/noisy_images/"

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

    def open_noisy_images_folder(self):
        """Apre la cartella delle immagini rumorose generate"""
        if not self.current_project_path:
            messagebox.showwarning("Attenzione", "Nessun progetto attivo")
            return

        project_paths = self.project_manager.get_project_paths()
        noisy_images_dir = project_paths.get("noisy_images")

        if not noisy_images_dir or not os.path.exists(noisy_images_dir):
            messagebox.showwarning("Attenzione",
                                 "Cartella immagini rumorose non trovata.\n"
                                 "Genera prima alcune immagini rumorose.")
            return

        try:
            os.startfile(noisy_images_dir)  # Windows
        except AttributeError:
            os.system(f"xdg-open '{noisy_images_dir}'")  # Linux

    def on_generate_noise(self, generation_params):
        """Gestisce la richiesta di generazione rumore"""
        if not self.file_selector.has_selection():
            messagebox.showwarning("Attenzione", "Seleziona prima file o cartella")
            return
        
        if not self.current_project_path:
            messagebox.showwarning("Attenzione", "Crea prima un progetto")
            return
        
        if not self.noise_generator:
            messagebox.showerror("Errore", "Generatore di rumore non disponibile")
            return
        
        # Avvia generazione in thread separato
        self.generation_active = True
        
        thread = threading.Thread(target=self.generate_noise_thread, args=(generation_params,))
        thread.daemon = True
        thread.start()

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

    def on_visualization_saved(self, file_path, visualization_type):
        """Chiamato quando viene salvata una visualizzazione"""
        if self.project_manager.current_project:
            self.project_manager.add_visualization(file_path, visualization_type)
            self.log(f"💾 Visualizzazione salvata: {os.path.basename(file_path)}")
    
    def generate_noise_thread(self, generation_params):
        """Thread per generazione rumore"""
        try:
            # Cartella output
            project_paths = self.project_manager.get_project_paths()
            output_dir = Path(project_paths["noisy_images"])

            self.log("🎲 Avvio generazione rumore...")
            self.log(f"📁 Output: {output_dir}")

            # Ottieni file da elaborare
            selected_paths, selection_type = self.file_selector.get_selection()

            # Determina file da processare
            files_to_process = []
            if selection_type == "single_file":
                files_to_process = selected_paths
            elif selection_type == "multiple_files":
                files_to_process = selected_paths
            elif selection_type == "folder":
                # Trova tutti i file TIFF nella cartella
                tiff_files = self.file_selector._find_tiff_files(selected_paths[0])
                files_to_process = tiff_files

            if not files_to_process:
                self.log("❌ Nessun file da processare")
                return

            # Parametri generazione
            noise_types = generation_params["noise_types"]
            levels = generation_params["levels"]

            # Calcola totale operazioni
            total_operations = len(files_to_process) * len(noise_types) * levels
            current_operation = 0

            # Processa ogni file
            for file_path in files_to_process:
                if not self.generation_active:
                    break

                self.log(f"📷 Processando: {os.path.basename(file_path)}")

                try:
                    # Carica immagine
                    image_data = load_multiband_image(file_path)
                    base_name = os.path.splitext(os.path.basename(file_path))[0]

                    # Genera rumore per ogni tipo
                    for noise_type in noise_types:
                        if not self.generation_active:
                            break

                        # Crea cartella per tipo di rumore
                        noise_output_dir = output_dir / noise_type
                        noise_output_dir.mkdir(exist_ok=True)

                        # Genera livelli di rumore
                        for level in range(1, levels + 1):
                            if not self.generation_active:
                                break

                            current_operation += 1
                            progress = (current_operation / total_operations) * 100

                            # Aggiorna progress
                            self.root.after(0, lambda p=progress: self.noise_controls.update_progress(
                                p, f"Generando {noise_type} livello {level}"))

                            # Applica rumore
                            noisy_image = self.noise_generator.apply_noise(image_data, noise_type, level)

                            # Salva immagine rumorosa
                            output_filename = f"{base_name}_{noise_type}_level_{level:02d}.tif"
                            output_path = noise_output_dir / output_filename

                            success = save_multiband_image(noisy_image, str(output_path), file_path)

                            if success:
                                self.log(f"✅ Salvato: {output_filename}")
                            else:
                                self.log(f"❌ Errore salvando: {output_filename}")

                    # Carica il primo risultato nel visualizzatore (solo per il primo file)
                    if file_path == files_to_process[0] and noise_types:
                        first_noise_type = noise_types[0]
                        first_result_path = output_dir / first_noise_type / f"{base_name}_{first_noise_type}_level_01.tif"
                        if first_result_path.exists():
                            self.root.after(0, lambda: self.load_generated_result(str(first_result_path)))

                except Exception as e:
                    self.log(f"❌ Errore processando {os.path.basename(file_path)}: {e}")

            # Registra operazione nel progetto
            self.project_manager.add_processing_record("noise_generation", {
                "noise_types": noise_types,
                "levels": levels,
                "files_processed": len(files_to_process),
                "total_images_generated": current_operation,
                "output_directory": str(output_dir)
            })

            self.log("🎉 Generazione rumore completata!")
            self.log(f"📁 {current_operation} immagini salvate in: {output_dir}")
            self.log(f"📂 Apri cartella progetto per vedere i risultati")
            self.root.after(0, lambda: self.noise_controls.update_progress(100, "Completato"))

        except Exception as e:
            self.log(f"❌ Errore generazione rumore: {e}")
        finally:
            # Ripristina UI
            self.root.after(0, self.generation_finished)

    def generation_finished(self):
        """Chiamato al termine della generazione"""
        self.generation_active = False
        self.noise_controls._generation_finished()

    def load_generated_result(self, output_file):
        """Carica un risultato generato nel visualizzatore"""
        try:
            if os.path.exists(output_file):
                success = self.image_viewer.load_image(output_file)
                if success:
                    self.log(f"🖼️ Risultato caricato nel visualizzatore: {os.path.basename(output_file)}")
                else:
                    self.log(f"❌ Impossibile visualizzare: {os.path.basename(output_file)}")
        except Exception as e:
            self.log(f"❌ Errore caricamento risultato: {e}")

    def log(self, message):
        """Aggiunge messaggio al log (placeholder - implementare se necessario)"""
        print(f"[GUI] {message}")
        self.root.update_idletasks()

    def show_about(self):
        """Mostra informazioni sull'applicazione"""
        about_text = """Noise Generator v1.0

Generazione avanzata di rumore su immagini multispettrali
per test di algoritmi di denoising.

Supporta fotocamere MicaSense RedEdge con
8 tipi di rumore diversi e livelli configurabili."""

        messagebox.showinfo("Informazioni", about_text)

    def on_closing(self):
        """Gestisce la chiusura dell'applicazione"""
        if self.generation_active:
            if not messagebox.askokcancel("Generazione in corso",
                                         "Generazione in corso. Vuoi davvero uscire?"):
                return

        # Pulizia progetto vuoto
        if self.project_manager.current_project:
            self.project_manager.cleanup_empty_project()

        self.root.destroy()

    def run(self):
        """Avvia l'applicazione"""
        self.root.mainloop()


def launch_gui():
    """Lancia l'interfaccia grafica"""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    launch_gui()
