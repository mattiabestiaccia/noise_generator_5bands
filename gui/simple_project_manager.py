#!/usr/bin/env python3
"""
Simple Project Manager - Gestione progetti semplificata per visualizzazioni

Gestisce progetti con struttura semplificata:
proj/
├── originals/     # Immagini originali
└── visualizations/ # Visualizzazioni salvate
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any


class SimpleProjectManager:
    """Gestione progetti semplificata per visualizzazioni"""
    
    def __init__(self, base_projects_dir: Optional[str] = None):
        """
        Inizializza il project manager
        
        Args:
            base_projects_dir: Directory base per i progetti (opzionale)
        """
        if base_projects_dir is None:
            # Default: cartella projects nella directory del modulo
            script_dir = Path(__file__).parent.parent
            self.projects_dir = script_dir / "projects"
        else:
            self.projects_dir = Path(base_projects_dir)
        
        self.projects_dir.mkdir(exist_ok=True)
        
        # Progetto corrente
        self.current_project = None
        self.current_project_path = None
        
        # Flags per tracking utilizzo
        self.images_loaded = False
        self.visualizations_saved = False
    
    def create_project(self, project_name: Optional[str] = None, 
                      source_paths: List[str] = None) -> str:
        """
        Crea un nuovo progetto con struttura semplificata
        
        Args:
            project_name: Nome del progetto (auto-generato se None)
            source_paths: Path delle immagini sorgente
            
        Returns:
            Path del progetto creato
        """
        # Auto-genera nome se non fornito
        if not project_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = f"visualization_project_{timestamp}"
        
        # Sanitizza nome progetto
        safe_name = "".join(c for c in project_name if c.isalnum() or c in ('-', '_')).strip()
        if not safe_name:
            safe_name = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        project_path = self.projects_dir / safe_name
        
        # Verifica se esiste già
        if project_path.exists():
            counter = 1
            while (self.projects_dir / f"{safe_name}_{counter}").exists():
                counter += 1
            safe_name = f"{safe_name}_{counter}"
            project_path = self.projects_dir / safe_name
        
        # Crea struttura progetto semplificata
        project_path.mkdir(exist_ok=True)
        
        # Sottocartelle richieste
        folders = [
            "originals",        # Immagini originali
            "visualizations"    # Visualizzazioni salvate
        ]
        
        for folder in folders:
            (project_path / folder).mkdir(exist_ok=True)
        
        # Crea metadata del progetto
        metadata = {
            "project_name": project_name,
            "safe_name": safe_name,
            "description": f"Progetto visualizzazioni multispettrali",
            "created_date": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "version": "1.0",
            "gui_type": "visualization_only",
            "structure": {
                "originals": "Immagini originali caricate",
                "visualizations": "Visualizzazioni salvate dalla GUI"
            },
            "source_info": self._analyze_source_paths(source_paths),
            "visualizations": []
        }
        
        with open(project_path / "project_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Copia file sorgente se forniti
        if source_paths:
            self._copy_source_files(source_paths, project_path / "originals")
            self.images_loaded = True
        
        # Imposta come progetto corrente
        self.current_project = metadata
        self.current_project_path = project_path
        
        return str(project_path)
    
    def _analyze_source_paths(self, source_paths: List[str]) -> Dict[str, Any]:
        """Analizza i path sorgente per creare info metadata"""
        if not source_paths:
            return {"type": "none", "count": 0, "paths": []}
        
        # Determina tipo selezione
        if len(source_paths) == 1:
            path = source_paths[0]
            if os.path.isfile(path):
                return {
                    "type": "single_file",
                    "count": 1,
                    "paths": source_paths,
                    "file_name": os.path.basename(path)
                }
            elif os.path.isdir(path):
                # Conta file TIFF nella cartella
                tiff_files = self._find_tiff_files(path)
                return {
                    "type": "folder",
                    "count": len(tiff_files),
                    "paths": source_paths,
                    "folder_name": os.path.basename(path),
                    "tiff_files": len(tiff_files)
                }
        else:
            # File multipli
            return {
                "type": "multiple_files",
                "count": len(source_paths),
                "paths": source_paths,
                "file_names": [os.path.basename(p) for p in source_paths]
            }
        
        return {"type": "unknown", "count": 0, "paths": source_paths}
    
    def _find_tiff_files(self, folder_path: str) -> List[str]:
        """Trova file TIFF in una cartella"""
        tiff_files = []
        folder = Path(folder_path)
        
        for pattern in ["*.tif", "*.tiff", "*.TIF", "*.TIFF"]:
            tiff_files.extend(folder.glob(pattern))
        
        return [str(f) for f in sorted(tiff_files)]
    
    def _copy_source_files(self, source_paths: List[str], originals_dir: Path):
        """Copia file sorgente nella cartella originals del progetto"""
        try:
            for source_path in source_paths:
                if os.path.isfile(source_path):
                    # Copia file singolo
                    dest_path = originals_dir / os.path.basename(source_path)
                    shutil.copy2(source_path, dest_path)
                elif os.path.isdir(source_path):
                    # Copia file TIFF dalla cartella
                    tiff_files = self._find_tiff_files(source_path)
                    for tiff_file in tiff_files:
                        dest_path = originals_dir / os.path.basename(tiff_file)
                        shutil.copy2(tiff_file, dest_path)
        except Exception as e:
            print(f"⚠ Errore copiando file sorgente: {e}")
    
    def get_project_paths(self) -> Dict[str, str]:
        """Restituisce i path delle cartelle del progetto corrente"""
        if not self.current_project_path:
            return {}
        
        return {
            "project": str(self.current_project_path),
            "originals": str(self.current_project_path / "originals"),
            "visualizations": str(self.current_project_path / "visualizations")
        }
    
    def get_source_info(self) -> Dict[str, Any]:
        """Restituisce informazioni sui file sorgente"""
        if not self.current_project:
            return {}
        
        return self.current_project.get("source_info", {})
    
    def add_visualization(self, file_path: str, visualization_type: str, original_image: str = None):
        """Aggiunge una visualizzazione al progetto"""
        if not self.current_project:
            return
        
        visualization_record = {
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "type": visualization_type,
            "file_name": os.path.basename(file_path),
            "original_image": original_image
        }
        
        if "visualizations" not in self.current_project:
            self.current_project["visualizations"] = []
        
        self.current_project["visualizations"].append(visualization_record)
        self.visualizations_saved = True
        self._save_current_metadata()
    
    def _save_current_metadata(self):
        """Salva i metadata del progetto corrente"""
        if not self.current_project or not self.current_project_path:
            return
        
        self.current_project["last_modified"] = datetime.now().isoformat()
        
        metadata_file = self.current_project_path / "project_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_project, f, indent=2, ensure_ascii=False)
    
    def cleanup_empty_project(self):
        """Pulisce il progetto se vuoto (nessuna immagine caricata e nessuna visualizzazione salvata)"""
        if not self.current_project_path or not self.current_project:
            return
        
        # Verifica se ci sono immagini caricate o visualizzazioni salvate
        should_keep = self.images_loaded or self.visualizations_saved
        
        # Verifica anche fisicamente se ci sono file nelle cartelle
        if not should_keep:
            originals_dir = self.current_project_path / "originals"
            visualizations_dir = self.current_project_path / "visualizations"
            
            has_originals = False
            has_visualizations = False
            
            if originals_dir.exists():
                files = list(originals_dir.rglob("*"))
                has_originals = any(f.is_file() for f in files)
            
            if visualizations_dir.exists():
                files = list(visualizations_dir.rglob("*"))
                has_visualizations = any(f.is_file() for f in files)
            
            should_keep = has_originals or has_visualizations
        
        # Se non ci sono contenuti, rimuovi il progetto
        if not should_keep:
            try:
                shutil.rmtree(self.current_project_path)
                print(f"🗑️ Progetto vuoto rimosso: {self.current_project_path.name}")
            except Exception as e:
                print(f"⚠ Errore rimuovendo progetto vuoto: {e}")
    
    def mark_images_loaded(self):
        """Marca che sono state caricate immagini"""
        self.images_loaded = True
    
    def mark_visualization_saved(self):
        """Marca che è stata salvata una visualizzazione"""
        self.visualizations_saved = True
