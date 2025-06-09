#!/usr/bin/env python3
"""
Script di avvio per la GUI del Noise Generator

Avvia l'interfaccia grafica per la generazione di immagini rumorose multispettrali.
"""

import sys
import os
from pathlib import Path

# Aggiungi il percorso del modulo al PYTHONPATH
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

def check_dependencies():
    """Verifica che tutte le dipendenze necessarie siano installate"""
    missing_deps = []
    
    # Dipendenze critiche
    critical_deps = [
        'tkinter',
        'numpy', 
        'matplotlib',
        'tifffile'
    ]
    
    # Dipendenze opzionali
    optional_deps = [
        'rasterio',
        'imagecodecs'
    ]
    
    # Verifica dipendenze critiche
    for dep in critical_deps:
        try:
            if dep == 'tkinter':
                import tkinter
            elif dep == 'numpy':
                import numpy
            elif dep == 'matplotlib':
                import matplotlib
            elif dep == 'tifffile':
                import tifffile
        except ImportError:
            missing_deps.append(dep)
    
    # Verifica dipendenze opzionali (solo warning)
    missing_optional = []
    for dep in optional_deps:
        try:
            if dep == 'rasterio':
                import rasterio
            elif dep == 'imagecodecs':
                import imagecodecs
        except ImportError:
            missing_optional.append(dep)
    
    # Gestisci dipendenze mancanti
    if missing_deps:
        print("❌ ERRORE: Dipendenze critiche mancanti:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nInstalla le dipendenze con:")
        print("   pip install numpy matplotlib tifffile")
        if 'tkinter' in missing_deps:
            print("   # Per tkinter su Ubuntu/Debian:")
            print("   sudo apt-get install python3-tk")
        return False
    
    # Warning per dipendenze opzionali
    if missing_optional:
        print("⚠️  Dipendenze opzionali mancanti (funzionalità limitate):")
        for dep in missing_optional:
            print(f"   - {dep}")
        print("\nPer funzionalità complete installa:")
        print("   pip install rasterio imagecodecs")
        print()
    
    return True

def setup_environment():
    """Configura l'ambiente per l'esecuzione"""
    # Verifica che la cartella projects esista
    projects_dir = script_dir / "projects"
    projects_dir.mkdir(exist_ok=True)
    
    # Verifica che la cartella configs esista
    configs_dir = script_dir / "configs"
    if not configs_dir.exists():
        print(f"⚠️  Cartella configs non trovata: {configs_dir}")
        print("   Alcune funzionalità potrebbero essere limitate")
    
    # Verifica che gli scripts esistano
    scripts_dir = script_dir / "scripts"
    if not scripts_dir.exists():
        print(f"❌ Cartella scripts non trovata: {scripts_dir}")
        print("   La generazione di rumore non sarà disponibile")
        return False
    
    # Verifica script critici
    critical_scripts = [
        "add_noise_to_images.py",
        "project_manager.py"
    ]
    
    for script in critical_scripts:
        script_path = scripts_dir / script
        if not script_path.exists():
            print(f"❌ Script critico mancante: {script_path}")
            return False
    
    return True

def main():
    """Funzione principale"""
    print("🚀 Avvio Noise Generator GUI...")
    print("=" * 50)
    
    # Verifica dipendenze
    print("📦 Verifica dipendenze...")
    if not check_dependencies():
        print("\n❌ Impossibile avviare a causa di dipendenze mancanti")
        sys.exit(1)
    
    # Configura ambiente
    print("⚙️  Configurazione ambiente...")
    if not setup_environment():
        print("\n❌ Errore nella configurazione dell'ambiente")
        sys.exit(1)
    
    print("✅ Ambiente configurato correttamente")
    print()
    
    # Avvia GUI
    try:
        print("🖥️  Avvio interfaccia grafica...")
        from gui.main_window import launch_gui
        launch_gui()
        
    except ImportError as e:
        print(f"❌ Errore importando moduli GUI: {e}")
        print("\nVerifica che tutti i file GUI siano presenti:")
        gui_files = [
            "gui/__init__.py",
            "gui/main_window.py", 
            "gui/image_viewer.py",
            "gui/file_selector.py",
            "gui/project_manager.py",
            "gui/noise_controls.py"
        ]
        
        for gui_file in gui_files:
            file_path = script_dir / gui_file
            status = "✅" if file_path.exists() else "❌"
            print(f"   {status} {gui_file}")
        
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Errore inaspettato: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
