#!/usr/bin/env python3
"""
Simple Image Viewer - Visualizzatore semplificato senza matplotlib

Visualizzatore tkinter base per immagini multispettrali che non richiede matplotlib.
Usa PIL/Pillow per la visualizzazione delle immagini.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
from PIL import Image, ImageTk
import tifffile
from typing import Optional, Callable
import os


class SimpleImageViewer:
    """Visualizzatore semplificato per immagini multispettrali"""
    
    def __init__(self, parent, on_save_callback: Callable = None):
        """
        Inizializza il visualizzatore
        
        Args:
            parent: Widget parent tkinter
            on_save_callback: Callback per salvare visualizzazioni
        """
        self.parent = parent
        self.on_save_callback = on_save_callback
        
        # Dati immagine
        self.bands_data = None
        self.current_file = None
        self.current_band = 0
        self.view_mode = "bands"  # "bands", "rgb"
        self.project_visualizations_dir = None
        
        # Nomi bande MicaSense
        self.band_names = [
            "Banda 1 - Blue (475nm)",
            "Banda 2 - Green (560nm)", 
            "Banda 3 - Red (668nm)",
            "Banda 4 - Red Edge (717nm)",
            "Banda 5 - Near-IR (840nm)"
        ]
        
        # Variabili per display
        self.display_image = None
        self.photo_image = None
        
        self.setup_ui()

    def set_project_visualizations_dir(self, visualizations_dir: str):
        """Imposta la cartella visualizzazioni del progetto"""
        self.project_visualizations_dir = visualizations_dir

    def setup_ui(self):
        """Configura l'interfaccia utente"""
        # Frame principale
        self.main_frame = ttk.LabelFrame(self.parent, text="Visualizzatore Immagini (Semplificato)", padding=5)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Frame controlli
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.pack(fill="x", pady=(0, 5))
        
        # Modalità visualizzazione
        mode_frame = ttk.LabelFrame(controls_frame, text="Modalità", padding=5)
        mode_frame.pack(side="left", padx=(0, 10))

        # Radio buttons per modalità
        self.mode_var = tk.StringVar(value="bands")
        
        ttk.Radiobutton(mode_frame, text="Bande Singole", 
                       variable=self.mode_var, value="bands",
                       command=self.change_view_mode).pack(side="left", padx=5)
        
        ttk.Radiobutton(mode_frame, text="RGB (3,2,1)", 
                       variable=self.mode_var, value="rgb",
                       command=self.change_view_mode).pack(side="left", padx=5)
        
        # Controlli banda (solo per modalità bande)
        self.band_frame = ttk.LabelFrame(controls_frame, text="Banda", padding=5)
        self.band_frame.pack(side="left", padx=(0, 10))
        
        ttk.Button(self.band_frame, text="◀", command=self.prev_band, width=3).pack(side="left")
        self.band_label = ttk.Label(self.band_frame, text="1/5", width=6)
        self.band_label.pack(side="left", padx=5)
        ttk.Button(self.band_frame, text="▶", command=self.next_band, width=3).pack(side="left")
        
        # Bottoni azione
        action_frame = ttk.Frame(controls_frame)
        action_frame.pack(side="right")

        ttk.Button(action_frame, text="📂 Carica", command=self.load_image_dialog).pack(side="left", padx=2)
        ttk.Button(action_frame, text="📊 Info", command=self.show_image_info).pack(side="left", padx=2)
        
        # Area immagine
        self.setup_image_area()
        
        # Inizialmente disabilita controlli
        self.set_controls_enabled(False)
    
    def setup_image_area(self):
        """Configura l'area di visualizzazione immagine"""
        # Frame per immagine con scrollbar
        image_frame = ttk.Frame(self.main_frame)
        image_frame.pack(fill="both", expand=True)
        
        # Canvas per immagine
        self.canvas = tk.Canvas(image_frame, bg="white")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(image_frame, orient="vertical", command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(image_frame, orient="horizontal", command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars e canvas
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Messaggio iniziale
        self.canvas.create_text(400, 300, text="Nessuna immagine caricata", 
                               font=("Arial", 14), fill="gray", tags="message")

    def load_image_dialog(self):
        """Apre dialog per caricare un'immagine"""
        file_path = filedialog.askopenfilename(
            title="Carica Immagine TIFF",
            filetypes=[
                ("File TIFF", "*.tif *.tiff"),
                ("Tutti i file", "*.*")
            ]
        )

        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path: str) -> bool:
        """
        Carica un'immagine multispettrale
        
        Args:
            file_path: Percorso del file TIFF
            
        Returns:
            True se caricamento riuscito
        """
        try:
            # Carica immagine
            self.bands_data = tifffile.imread(file_path)
            self.current_file = file_path
            
            # Verifica formato
            if len(self.bands_data.shape) != 3:
                messagebox.showerror("Errore", "Il file deve essere un TIFF multibanda")
                return False
            
            if self.bands_data.shape[0] != 5:
                messagebox.showwarning("Attenzione", 
                    f"Immagine con {self.bands_data.shape[0]} bande (attese 5)")
            
            # Reset visualizzazione
            self.current_band = 0
            self.view_mode = "bands"
            self.mode_var.set("bands")
            
            # Abilita controlli
            self.set_controls_enabled(True)
            
            # Aggiorna visualizzazione
            self.update_display()
            
            return True
            
        except Exception as e:
            messagebox.showerror("Errore Caricamento", f"Impossibile caricare l'immagine:\n{e}")
            return False
    
    def set_controls_enabled(self, enabled: bool):
        """Abilita/disabilita controlli"""
        state = "normal" if enabled else "disabled"
        
        # Controlli banda
        for child in self.band_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state=state)

    def change_view_mode(self):
        """Cambia modalità di visualizzazione"""
        self.view_mode = self.mode_var.get()
        self.update_band_controls_visibility()
        self.update_display()

    def update_band_controls_visibility(self):
        """Mostra/nasconde controlli banda in base alla modalità"""
        if self.view_mode == "bands":
            # Abilita controlli banda
            for child in self.band_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.config(state="normal")
        else:
            # Disabilita controlli banda
            for child in self.band_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.config(state="disabled")
    
    def prev_band(self):
        """Banda precedente"""
        if self.bands_data is None:
            return
        
        self.current_band = (self.current_band - 1) % self.bands_data.shape[0]
        if self.view_mode == "bands":
            self.update_display()
    
    def next_band(self):
        """Banda successiva"""
        if self.bands_data is None:
            return
        
        self.current_band = (self.current_band + 1) % self.bands_data.shape[0]
        if self.view_mode == "bands":
            self.update_display()
    
    def update_display(self):
        """Aggiorna la visualizzazione"""
        if self.bands_data is None:
            return

        try:
            if self.view_mode == "bands":
                self._display_single_band()
            elif self.view_mode == "rgb":
                self._display_rgb()

        except Exception as e:
            messagebox.showerror("Errore Visualizzazione", f"Errore nella visualizzazione:\n{e}")
    
    def _display_single_band(self):
        """Visualizza singola banda"""
        band_data = self.bands_data[self.current_band]
        normalized = self._normalize_band(band_data)
        
        # Converti in immagine PIL
        img_array = (normalized * 255).astype(np.uint8)
        pil_image = Image.fromarray(img_array, mode='L')
        
        # Ridimensiona se troppo grande
        max_size = 800
        if pil_image.width > max_size or pil_image.height > max_size:
            pil_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Converti per tkinter
        self.photo_image = ImageTk.PhotoImage(pil_image)
        
        # Mostra nel canvas
        self.canvas.delete("all")
        self.canvas.create_image(10, 10, anchor="nw", image=self.photo_image)
        
        # Aggiorna scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Aggiorna label banda
        self.band_label.config(text=f"{self.current_band + 1}/{self.bands_data.shape[0]}")
        
        # Aggiorna titolo frame
        self.main_frame.config(text=f"Visualizzatore - {self.band_names[self.current_band]}")
    
    def _display_rgb(self):
        """Visualizza composizione RGB (bande 3,2,1)"""
        if self.bands_data.shape[0] < 3:
            self.canvas.delete("all")
            self.canvas.create_text(400, 300, text="RGB richiede almeno 3 bande", 
                                   font=("Arial", 14), fill="red")
            return
        
        # RGB naturale: Red(3), Green(2), Blue(1) - indici 2,1,0
        red = self._normalize_band(self.bands_data[2])
        green = self._normalize_band(self.bands_data[1])
        blue = self._normalize_band(self.bands_data[0])
        
        # Combina in RGB
        rgb_array = np.stack([red, green, blue], axis=2)
        img_array = (rgb_array * 255).astype(np.uint8)
        
        # Converti in immagine PIL
        pil_image = Image.fromarray(img_array, mode='RGB')
        
        # Ridimensiona se troppo grande
        max_size = 800
        if pil_image.width > max_size or pil_image.height > max_size:
            pil_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Converti per tkinter
        self.photo_image = ImageTk.PhotoImage(pil_image)
        
        # Mostra nel canvas
        self.canvas.delete("all")
        self.canvas.create_image(10, 10, anchor="nw", image=self.photo_image)
        
        # Aggiorna scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Aggiorna titolo frame
        self.main_frame.config(text="Visualizzatore - RGB Naturale (3,2,1)")
    
    def _normalize_band(self, band_data: np.ndarray) -> np.ndarray:
        """Normalizza banda per visualizzazione"""
        band_min = np.percentile(band_data, 2)
        band_max = np.percentile(band_data, 98)
        
        if band_max > band_min:
            normalized = (band_data - band_min) / (band_max - band_min)
            return np.clip(normalized, 0, 1)
        else:
            return np.zeros_like(band_data)

    def show_image_info(self):
        """Mostra informazioni sull'immagine"""
        if self.bands_data is None:
            messagebox.showwarning("Attenzione", "Nessuna immagine caricata")
            return
        
        info = f"File: {os.path.basename(self.current_file) if self.current_file else 'N/A'}\n"
        info += f"Dimensioni: {self.bands_data.shape[2]} x {self.bands_data.shape[1]} pixel\n"
        info += f"Bande: {self.bands_data.shape[0]}\n"
        info += f"Tipo dati: {self.bands_data.dtype}\n"
        
        if self.view_mode == "bands":
            band_data = self.bands_data[self.current_band]
            info += f"\nBanda corrente: {self.current_band + 1}\n"
            info += f"Min: {band_data.min()}\n"
            info += f"Max: {band_data.max()}\n"
            info += f"Media: {band_data.mean():.2f}\n"
        
        messagebox.showinfo("Informazioni Immagine", info)
