#!/usr/bin/env python3
"""
Project Manager GUI - Gestione progetti per la GUI del noise generator

Adatta il project manager esistente per l'uso con l'interfaccia grafica,
mantenendo compatibilità con la struttura esistente.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

# Import del project manager esistente
try:
    from ..scripts.project_manager import NoiseProjectManager
except ImportError:
    try:
        from scripts.project_manager import NoiseProjectManager
    except ImportError:
        # Fallback se non disponibile
        NoiseProjectManager = None


class ProjectManager:
    """Gestione progetti per la GUI del noise generator"""
    
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
        
        # Inizializza il project manager backend se disponibile
        if NoiseProjectManager:
            self.backend_manager = NoiseProjectManager(str(self.projects_dir))
        else:
            self.backend_manager = None
    
    def create_project(self, project_name: Optional[str] = None, 
                      source_paths: List[str] = None) -> str:
        """
        Crea un nuovo progetto
        
        Args:
            project_name: Nome del progetto (auto-generato se None)
            source_paths: Path delle immagini sorgente
            
        Returns:
            Path del progetto creato
        """
        # Auto-genera nome se non fornito
        if not project_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = f"noise_project_{timestamp}"
        
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
        
        # Crea struttura progetto
        project_path.mkdir(exist_ok=True)
        
        # Sottocartelle per la GUI
        folders = [
            "input",              # Immagini originali
            "noisy_images",       # Immagini con rumore generate
            "visualizations",     # Visualizzazioni salvate
            "analysis",           # Risultati analisi e plot
            "config",             # File di configurazione
            "reports"             # Report e log
        ]
        
        for folder in folders:
            (project_path / folder).mkdir(exist_ok=True)
        
        # Crea metadata del progetto
        metadata = {
            "project_name": project_name,
            "safe_name": safe_name,
            "description": f"Progetto generazione rumore creato da GUI",
            "created_date": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "version": "1.0",
            "gui_version": True,
            "structure": {
                "input": "Immagini originali da elaborare",
                "noisy_images": "Immagini con rumore generate",
                "visualizations": "Visualizzazioni salvate dalla GUI",
                "analysis": "Plot e analisi metriche",
                "config": "File di configurazione",
                "reports": "Report di elaborazione"
            },
            "source_info": self._analyze_source_paths(source_paths),
            "processing_history": [],
            "visualizations": []
        }
        
        with open(project_path / "project_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Copia file sorgente se forniti
        if source_paths:
            self._copy_source_files(source_paths, project_path / "input")
        
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
    
    def _copy_source_files(self, source_paths: List[str], input_dir: Path):
        """Copia file sorgente nella cartella input del progetto"""
        try:
            for source_path in source_paths:
                if os.path.isfile(source_path):
                    # Copia file singolo
                    dest_path = input_dir / os.path.basename(source_path)
                    shutil.copy2(source_path, dest_path)
                elif os.path.isdir(source_path):
                    # Copia file TIFF dalla cartella
                    tiff_files = self._find_tiff_files(source_path)
                    for tiff_file in tiff_files:
                        dest_path = input_dir / os.path.basename(tiff_file)
                        shutil.copy2(tiff_file, dest_path)
        except Exception as e:
            print(f"⚠ Errore copiando file sorgente: {e}")
    
    def get_project_paths(self) -> Dict[str, str]:
        """Restituisce i path delle cartelle del progetto corrente"""
        if not self.current_project_path:
            return {}
        
        return {
            "project": str(self.current_project_path),
            "input": str(self.current_project_path / "input"),
            "noisy_images": str(self.current_project_path / "noisy_images"),
            "visualizations": str(self.current_project_path / "visualizations"),
            "analysis": str(self.current_project_path / "analysis"),
            "config": str(self.current_project_path / "config"),
            "reports": str(self.current_project_path / "reports")
        }
    
    def get_source_info(self) -> Dict[str, Any]:
        """Restituisce informazioni sui file sorgente"""
        if not self.current_project:
            return {}
        
        return self.current_project.get("source_info", {})
    
    def add_visualization(self, file_path: str, visualization_type: str):
        """Aggiunge una visualizzazione al progetto"""
        if not self.current_project:
            return
        
        visualization_record = {
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "type": visualization_type,
            "file_name": os.path.basename(file_path)
        }
        
        if "visualizations" not in self.current_project:
            self.current_project["visualizations"] = []
        
        self.current_project["visualizations"].append(visualization_record)
        self._save_current_metadata()
    
    def add_processing_record(self, operation: str, details: Dict[str, Any]):
        """Aggiunge un record di elaborazione al progetto"""
        if not self.current_project:
            return
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details
        }
        
        if "processing_history" not in self.current_project:
            self.current_project["processing_history"] = []
        
        self.current_project["processing_history"].append(record)
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
        """Pulisce il progetto se vuoto (nessuna elaborazione effettuata)"""
        if not self.current_project_path or not self.current_project:
            return
        
        # Verifica se ci sono file nelle cartelle di output
        output_dirs = ["noisy_images", "visualizations", "analysis"]
        has_output = False
        
        for dir_name in output_dirs:
            dir_path = self.current_project_path / dir_name
            if dir_path.exists():
                files = list(dir_path.rglob("*"))
                if any(f.is_file() for f in files):
                    has_output = True
                    break
        
        # Se non ci sono output, rimuovi il progetto
        if not has_output:
            try:
                shutil.rmtree(self.current_project_path)
                print(f"🗑️ Progetto vuoto rimosso: {self.current_project_path.name}")
            except Exception as e:
                print(f"⚠ Errore rimuovendo progetto vuoto: {e}")
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """Lista tutti i progetti disponibili"""
        if self.backend_manager:
            return self.backend_manager.list_projects()
        
        # Implementazione fallback
        projects = []
        for item in self.projects_dir.iterdir():
            if item.is_dir() and (item / "project_metadata.json").exists():
                try:
                    with open(item / "project_metadata.json", 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    projects.append({
                        "path": item,
                        "metadata": metadata
                    })
                except Exception as e:
                    print(f"⚠ Errore leggendo metadata di {item.name}: {e}")
        
        return sorted(projects, key=lambda x: x["metadata"]["created_date"], reverse=True)
