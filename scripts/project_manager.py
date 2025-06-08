#!/usr/bin/env python3
"""
Project Manager per il noise generator.
Gestisce la creazione e organizzazione dei progetti di elaborazione.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import argparse
import shutil

class NoiseProjectManager:
    """Gestisce i progetti di elaborazione rumore."""
    
    def __init__(self, base_projects_dir=None):
        if base_projects_dir is None:
            # Default: cartella projects nella directory del modulo
            script_dir = Path(__file__).parent.parent
            self.projects_dir = script_dir / "projects"
        else:
            self.projects_dir = Path(base_projects_dir)
        
        self.projects_dir.mkdir(exist_ok=True)
    
    def create_project(self, project_name, description="", overwrite=False):
        """
        Crea un nuovo progetto con la struttura standard.
        
        Args:
            project_name: Nome del progetto
            description: Descrizione del progetto
            overwrite: Se sovrascrivere progetto esistente
            
        Returns:
            Path: Percorso del progetto creato
        """
        # Sanitize project name
        safe_name = "".join(c for c in project_name if c.isalnum() or c in ('-', '_')).strip()
        if not safe_name:
            safe_name = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        project_path = self.projects_dir / safe_name
        
        # Verifica se esiste già
        if project_path.exists() and not overwrite:
            print(f"⚠ Progetto '{safe_name}' esiste già. Usa --overwrite per sovrascrivere.")
            return None
        
        # Rimuovi progetto esistente se overwrite
        if project_path.exists() and overwrite:
            shutil.rmtree(project_path)
            print(f"🗑 Progetto esistente '{safe_name}' rimosso")
        
        # Crea struttura progetto
        project_path.mkdir(exist_ok=True)
        
        # Sottocartelle standard
        folders = [
            "input",           # Immagini originali
            "noisy_images",    # Immagini con rumore
            "analysis",        # Risultati analisi e plot
            "config",          # File di configurazione
            "reports"          # Report e log
        ]
        
        for folder in folders:
            (project_path / folder).mkdir(exist_ok=True)
        
        # Crea metadata del progetto
        metadata = {
            "project_name": project_name,
            "safe_name": safe_name,
            "description": description,
            "created_date": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "version": "1.0",
            "structure": {
                "input": "Immagini originali da elaborare",
                "noisy_images": "Immagini con rumore generate",
                "analysis": "Plot e analisi metriche",
                "config": "File di configurazione",
                "reports": "Report di elaborazione"
            },
            "processing_history": []
        }
        
        with open(project_path / "project_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Crea README del progetto
        readme_content = f"""# Progetto: {project_name}

**Descrizione:** {description}
**Creato:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Struttura Progetto

```
{safe_name}/
├── input/              # Immagini originali
├── noisy_images/       # Immagini con rumore
│   ├── gaussian/
│   ├── salt_pepper/
│   ├── poisson/
│   ├── speckle/
│   ├── motion_blur/
│   ├── atmospheric/
│   ├── compression/
│   └── iso_noise/
├── analysis/           # Plot e metriche
├── config/            # Configurazioni
├── reports/           # Report elaborazione
└── project_metadata.json
```

## Comandi

### Generazione Rumore
```bash
python scripts/add_noise_to_images.py --project {safe_name} -l 3
```

### Analisi Metriche
```bash
python scripts/analyze_noise_metrics.py --project {safe_name}
```

### Gestione Progetto
```bash
# Lista progetti
python scripts/project_manager.py list

# Info progetto
python scripts/project_manager.py info {safe_name}

# Cleanup progetto
python scripts/project_manager.py clean {safe_name}
```
"""
        
        with open(project_path / "README.md", 'w') as f:
            f.write(readme_content)
        
        print(f"✅ Progetto '{safe_name}' creato in: {project_path}")
        print(f"📁 Struttura:")
        for folder in folders:
            print(f"   {project_path / folder}")
        
        return project_path
    
    def list_projects(self):
        """Lista tutti i progetti esistenti."""
        projects = []
        
        for item in self.projects_dir.iterdir():
            if item.is_dir() and (item / "project_metadata.json").exists():
                try:
                    with open(item / "project_metadata.json", 'r') as f:
                        metadata = json.load(f)
                    projects.append({
                        "path": item,
                        "metadata": metadata
                    })
                except Exception as e:
                    print(f"⚠ Errore leggendo metadata di {item.name}: {e}")
        
        return sorted(projects, key=lambda x: x["metadata"]["created_date"], reverse=True)
    
    def get_project_info(self, project_name):
        """Ottiene informazioni dettagliate su un progetto."""
        project_path = self.projects_dir / project_name
        
        if not project_path.exists():
            print(f"❌ Progetto '{project_name}' non trovato")
            return None
        
        metadata_file = project_path / "project_metadata.json"
        if not metadata_file.exists():
            print(f"❌ Metadata del progetto '{project_name}' non trovato")
            return None
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Calcola statistiche cartelle
            stats = {}
            for folder in ["input", "noisy_images", "analysis", "reports"]:
                folder_path = project_path / folder
                if folder_path.exists():
                    files = list(folder_path.rglob("*"))
                    stats[folder] = {
                        "files": len([f for f in files if f.is_file()]),
                        "size_mb": sum(f.stat().st_size for f in files if f.is_file()) / (1024*1024)
                    }
                else:
                    stats[folder] = {"files": 0, "size_mb": 0}
            
            return {
                "path": project_path,
                "metadata": metadata,
                "stats": stats
            }
            
        except Exception as e:
            print(f"❌ Errore leggendo progetto '{project_name}': {e}")
            return None
    
    def update_project_metadata(self, project_name, updates):
        """Aggiorna i metadata di un progetto."""
        project_path = self.projects_dir / project_name
        metadata_file = project_path / "project_metadata.json"
        
        if not metadata_file.exists():
            return False
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            metadata.update(updates)
            metadata["last_modified"] = datetime.now().isoformat()
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"❌ Errore aggiornando metadata: {e}")
            return False
    
    def add_processing_record(self, project_name, operation, details):
        """Aggiunge un record di elaborazione al progetto."""
        project_path = self.projects_dir / project_name
        metadata_file = project_path / "project_metadata.json"
        
        if not metadata_file.exists():
            return False
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            record = {
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "details": details
            }
            
            if "processing_history" not in metadata:
                metadata["processing_history"] = []
            
            metadata["processing_history"].append(record)
            metadata["last_modified"] = datetime.now().isoformat()
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"❌ Errore aggiungendo record: {e}")
            return False
    
    def clean_project(self, project_name, what="temp"):
        """
        Pulisce un progetto rimuovendo file temporanei o specifici.
        
        Args:
            project_name: Nome del progetto
            what: Cosa pulire ("temp", "noisy", "analysis", "all")
        """
        project_path = self.projects_dir / project_name
        
        if not project_path.exists():
            print(f"❌ Progetto '{project_name}' non trovato")
            return False
        
        cleaned = []
        
        if what in ["temp", "all"]:
            # Rimuovi file temporanei
            temp_patterns = ["*.tmp", "*.log", "*~", "*.bak"]
            for pattern in temp_patterns:
                for temp_file in project_path.rglob(pattern):
                    temp_file.unlink()
                    cleaned.append(str(temp_file))
        
        if what in ["noisy", "all"]:
            # Rimuovi immagini con rumore
            noisy_dir = project_path / "noisy_images"
            if noisy_dir.exists():
                shutil.rmtree(noisy_dir)
                noisy_dir.mkdir()
                cleaned.append("noisy_images/*")
        
        if what in ["analysis", "all"]:
            # Rimuovi risultati analisi
            analysis_dir = project_path / "analysis"
            if analysis_dir.exists():
                shutil.rmtree(analysis_dir)
                analysis_dir.mkdir()
                cleaned.append("analysis/*")
        
        if cleaned:
            print(f"🧹 Puliti: {', '.join(cleaned)}")
            self.add_processing_record(project_name, "cleanup", {"cleaned": cleaned})
        else:
            print("✨ Niente da pulire")
        
        return True


def main():
    """Funzione principale CLI."""
    parser = argparse.ArgumentParser(description='Gestione progetti noise generator')
    subparsers = parser.add_subparsers(dest='command', help='Comandi disponibili')
    
    # Comando create
    create_parser = subparsers.add_parser('create', help='Crea nuovo progetto')
    create_parser.add_argument('name', help='Nome del progetto')
    create_parser.add_argument('-d', '--description', default='', help='Descrizione progetto')
    create_parser.add_argument('--overwrite', action='store_true', help='Sovrascrivi se esiste')
    
    # Comando list
    list_parser = subparsers.add_parser('list', help='Lista progetti')
    
    # Comando info
    info_parser = subparsers.add_parser('info', help='Info progetto')
    info_parser.add_argument('name', help='Nome del progetto')
    
    # Comando clean
    clean_parser = subparsers.add_parser('clean', help='Pulisci progetto')
    clean_parser.add_argument('name', help='Nome del progetto')
    clean_parser.add_argument('--what', choices=['temp', 'noisy', 'analysis', 'all'], 
                             default='temp', help='Cosa pulire')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Inizializza manager
    manager = NoiseProjectManager()
    
    if args.command == 'create':
        project_path = manager.create_project(args.name, args.description, args.overwrite)
        if project_path:
            print(f"\n📝 Per iniziare:")
            print(f"   1. Copia le immagini originali in: {project_path / 'input'}")
            print(f"   2. Genera rumore: python scripts/add_noise_to_images.py --project {project_path.name}")
            print(f"   3. Analizza: python scripts/analyze_noise_metrics.py --project {project_path.name}")
    
    elif args.command == 'list':
        projects = manager.list_projects()
        if not projects:
            print("📁 Nessun progetto trovato")
        else:
            print(f"📁 PROGETTI ({len(projects)}):")
            print("=" * 60)
            for proj in projects:
                meta = proj["metadata"]
                created = datetime.fromisoformat(meta["created_date"]).strftime('%Y-%m-%d %H:%M')
                print(f"  {meta['safe_name']}")
                print(f"    📝 {meta['project_name']}")
                if meta.get('description'):
                    print(f"    💬 {meta['description']}")
                print(f"    📅 Creato: {created}")
                print(f"    📂 {proj['path']}")
                print()
    
    elif args.command == 'info':
        info = manager.get_project_info(args.name)
        if info:
            meta = info["metadata"]
            stats = info["stats"]
            
            print(f"📊 PROGETTO: {meta['project_name']}")
            print("=" * 50)
            print(f"Nome sicuro: {meta['safe_name']}")
            print(f"Descrizione: {meta.get('description', 'N/A')}")
            print(f"Creato: {datetime.fromisoformat(meta['created_date']).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Modificato: {datetime.fromisoformat(meta['last_modified']).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Percorso: {info['path']}")
            print()
            print("📁 STATISTICHE:")
            for folder, stat in stats.items():
                print(f"   {folder}: {stat['files']} files, {stat['size_mb']:.1f} MB")
            
            if meta.get('processing_history'):
                print(f"\n📋 STORIA ELABORAZIONI ({len(meta['processing_history'])}):")
                for record in meta['processing_history'][-5:]:  # Ultime 5
                    timestamp = datetime.fromisoformat(record['timestamp']).strftime('%Y-%m-%d %H:%M')
                    print(f"   {timestamp}: {record['operation']}")
    
    elif args.command == 'clean':
        manager.clean_project(args.name, args.what)


if __name__ == "__main__":
    main()