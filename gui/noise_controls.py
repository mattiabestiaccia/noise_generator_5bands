#!/usr/bin/env python3
"""
Noise Controls - Controlli per la generazione di rumore

Widget tkinter per configurare e controllare la generazione di rumore
su immagini multispettrali.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from pathlib import Path
from typing import Dict, List, Callable, Optional


class NoiseControls:
    """Widget per controlli di generazione rumore"""

    def __init__(self, parent, on_generate_callback: Callable = None):
        """
        Inizializza i controlli rumore
        
        Args:
            parent: Widget parent tkinter
            on_generate_callback: Callback per avviare generazione rumore
        """
        self.parent = parent
        self.on_generate_callback = on_generate_callback
        
        # Configurazione rumore (caricata da file JSON)
        self.noise_config = self._load_noise_config()
        
        # Stato controlli
        self.selected_noise_types = []
        self.noise_levels = 5  # Default
        self.generation_active = False
        
        self.setup_ui()
    
    def _load_noise_config(self) -> Dict:
        """Carica configurazione rumore da file JSON"""
        try:
            # Cerca il file di configurazione
            script_dir = Path(__file__).parent.parent
            config_file = script_dir / "configs" / "noise_config.json"
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Configurazione di fallback
                return self._get_default_config()
                
        except Exception as e:
            print(f"⚠ Errore caricando configurazione rumore: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Configurazione di fallback se il file JSON non è disponibile"""
        return {
            "noise_types": {
                "gaussian": {
                    "description": "Rumore gaussiano (termico del sensore)",
                    "parameter_name": "sigma",
                    "parameter_range": [5, 50]
                },
                "salt_pepper": {
                    "description": "Rumore salt and pepper (pixel difettosi)",
                    "parameter_name": "probability", 
                    "parameter_range": [0.001, 0.01]
                },
                "poisson": {
                    "description": "Rumore di Poisson (shot noise)",
                    "parameter_name": "scale",
                    "parameter_range": [0.1, 1.0]
                },
                "speckle": {
                    "description": "Rumore speckle (moltiplicativo)",
                    "parameter_name": "variance",
                    "parameter_range": [0.05, 0.5]
                },
                "motion_blur": {
                    "description": "Motion blur (sfocatura da movimento)",
                    "parameter_name": "kernel_size",
                    "parameter_range": [3, 21]
                },
                "atmospheric": {
                    "description": "Effetti atmosferici (foschia, vapore)",
                    "parameter_name": "haze_intensity",
                    "parameter_range": [0.1, 1.0]
                },
                "compression": {
                    "description": "Artefatti di compressione JPEG",
                    "parameter_name": "quality",
                    "parameter_range": [50, 95]
                },
                "iso_noise": {
                    "description": "Rumore ad alto ISO",
                    "parameter_name": "iso_level",
                    "parameter_range": [1, 10]
                }
            },
            "generation_parameters": {
                "default_levels": 10
            }
        }
    
    def setup_ui(self):
        """Configura l'interfaccia utente"""
        # Frame principale
        self.main_frame = ttk.LabelFrame(self.parent, text="Generazione Rumore", padding=10)
        self.main_frame.pack(fill="x", padx=10, pady=5)
        
        # Selezione tipi di rumore
        self.setup_noise_types_selection()
        
        # Configurazione livelli
        self.setup_levels_configuration()
        
        # Controlli generazione
        self.setup_generation_controls()
    
    def setup_noise_types_selection(self):
        """Configura la selezione dei tipi di rumore"""
        types_frame = ttk.LabelFrame(self.main_frame, text="Tipi di Rumore", padding=5)
        types_frame.pack(fill="x", pady=(0, 10))
        
        # Frame per checkboxes (scrollable se necessario)
        canvas = tk.Canvas(types_frame, height=120)
        scrollbar = ttk.Scrollbar(types_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Checkboxes per tipi di rumore
        self.noise_type_vars = {}
        noise_types = self.noise_config.get("noise_types", {})
        
        row = 0
        for noise_type, config in noise_types.items():
            var = tk.BooleanVar()
            self.noise_type_vars[noise_type] = var
            
            # Checkbox
            cb = ttk.Checkbutton(
                scrollable_frame,
                text=noise_type.replace("_", " ").title(),
                variable=var,
                command=self._on_noise_type_change
            )
            cb.grid(row=row, column=0, sticky="w", padx=5, pady=2)
            
            # Descrizione
            desc_label = ttk.Label(
                scrollable_frame,
                text=config.get("description", ""),
                foreground="gray",
                font=("TkDefaultFont", 8)
            )
            desc_label.grid(row=row, column=1, sticky="w", padx=(10, 5), pady=2)
            
            row += 1
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bottoni selezione rapida
        quick_frame = ttk.Frame(types_frame)
        quick_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Button(quick_frame, text="Seleziona Tutti", 
                  command=self._select_all_noise_types).pack(side="left", padx=(0, 5))
        ttk.Button(quick_frame, text="Deseleziona Tutti", 
                  command=self._deselect_all_noise_types).pack(side="left", padx=5)
        ttk.Button(quick_frame, text="Realistici Drone", 
                  command=self._select_realistic_noise).pack(side="left", padx=5)
    
    def setup_levels_configuration(self):
        """Configura i livelli di rumore"""
        levels_frame = ttk.LabelFrame(self.main_frame, text="Configurazione Livelli", padding=5)
        levels_frame.pack(fill="x", pady=(0, 10))
        
        # Numero di livelli
        levels_config_frame = ttk.Frame(levels_frame)
        levels_config_frame.pack(fill="x")
        
        ttk.Label(levels_config_frame, text="Numero livelli:").pack(side="left")
        
        self.levels_var = tk.IntVar(value=self.noise_config.get("generation_parameters", {}).get("default_levels", 5))
        levels_spinbox = ttk.Spinbox(
            levels_config_frame,
            from_=1, to=20,
            textvariable=self.levels_var,
            width=5
        )
        levels_spinbox.pack(side="left", padx=(5, 10))
        
        # Info livelli
        info_label = ttk.Label(
            levels_config_frame,
            text="(1=minimo rumore, valore max=massimo rumore)",
            foreground="gray",
            font=("TkDefaultFont", 8)
        )
        info_label.pack(side="left")
    
    def setup_generation_controls(self):
        """Configura i controlli di generazione"""
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.pack(fill="x")
        
        # Bottone generazione principale
        self.generate_button = ttk.Button(
            controls_frame,
            text="🎲 Genera Immagini Rumorose",
            command=self._start_generation
        )
        self.generate_button.pack(side="left", padx=(0, 10))
        
        # Bottone stop
        self.stop_button = ttk.Button(
            controls_frame,
            text="⏹️ Stop",
            command=self._stop_generation,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            controls_frame,
            variable=self.progress_var,
            mode="determinate",
            length=200
        )
        self.progress_bar.pack(side="right")
        
        # Label stato
        self.status_label = ttk.Label(controls_frame, text="Pronto", foreground="green")
        self.status_label.pack(side="right", padx=(0, 10))
    
    def _on_noise_type_change(self):
        """Gestisce il cambio di selezione tipi di rumore"""
        self.selected_noise_types = [
            noise_type for noise_type, var in self.noise_type_vars.items()
            if var.get()
        ]
        
        # Abilita/disabilita bottone generazione
        self.generate_button.config(
            state="normal" if self.selected_noise_types else "disabled"
        )
    
    def _select_all_noise_types(self):
        """Seleziona tutti i tipi di rumore"""
        for var in self.noise_type_vars.values():
            var.set(True)
        self._on_noise_type_change()
    
    def _deselect_all_noise_types(self):
        """Deseleziona tutti i tipi di rumore"""
        for var in self.noise_type_vars.values():
            var.set(False)
        self._on_noise_type_change()
    
    def _select_realistic_noise(self):
        """Seleziona tipi di rumore realistici per drone"""
        # Deseleziona tutti
        self._deselect_all_noise_types()
        
        # Seleziona solo quelli realistici
        realistic_types = ["gaussian", "iso_noise", "atmospheric"]
        for noise_type in realistic_types:
            if noise_type in self.noise_type_vars:
                self.noise_type_vars[noise_type].set(True)
        
        self._on_noise_type_change()
    
    def _start_generation(self):
        """Avvia la generazione di rumore"""
        if not self.selected_noise_types:
            messagebox.showwarning("Attenzione", "Seleziona almeno un tipo di rumore")
            return
        
        # Prepara parametri generazione
        generation_params = {
            "noise_types": self.selected_noise_types,
            "levels": self.levels_var.get(),
            "config": self.noise_config
        }
        
        # Aggiorna UI
        self.generation_active = True
        self.generate_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_label.config(text="Generazione in corso...", foreground="orange")
        self.progress_var.set(0)
        
        # Chiama callback
        if self.on_generate_callback:
            self.on_generate_callback(generation_params)
    
    def _stop_generation(self):
        """Ferma la generazione di rumore"""
        self.generation_active = False
        self._generation_finished()
    
    def _generation_finished(self):
        """Chiamato al termine della generazione"""
        self.generation_active = False
        self.generate_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="Pronto", foreground="green")
        self.progress_var.set(0)
    
    def update_progress(self, progress: float, status: str = None):
        """Aggiorna la progress bar e lo stato"""
        self.progress_var.set(progress)
        if status:
            self.status_label.config(text=status)
    
    def get_generation_params(self) -> Dict:
        """Restituisce i parametri di generazione correnti"""
        return {
            "noise_types": self.selected_noise_types,
            "levels": self.levels_var.get(),
            "config": self.noise_config
        }
    
    def is_generation_active(self) -> bool:
        """Verifica se la generazione è attiva"""
        return self.generation_active
