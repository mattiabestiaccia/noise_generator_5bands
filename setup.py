#!/usr/bin/env python3
"""
Setup script per il modulo Noise Generator.
"""

import subprocess
import sys
from pathlib import Path

def install_dependencies():
    """Installa le dipendenze necessarie."""
    
    dependencies = [
        'opencv-python',
        'numpy',
        'matplotlib',
        'scikit-image',
        'tqdm',
        'pathlib'
    ]
    
    print("🔧 Installazione dipendenze...")
    
    for dep in dependencies:
        try:
            print(f"  Installando {dep}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"  ✅ {dep} installato")
        except subprocess.CalledProcessError:
            print(f"  ❌ Errore installando {dep}")
            return False
    
    return True

def check_structure():
    """Verifica la struttura del modulo."""
    
    print("\n📁 Verifica struttura modulo...")
    
    required_dirs = ['data', 'scripts', 'analysis', 'tests', 'configs', 'docs', 'utils']
    required_files = [
        'scripts/add_noise_to_images.py',
        'scripts/analyze_noisy_images.py', 
        'scripts/dataset_utils.py',
        'configs/noise_config.json'
    ]
    
    # Verifica cartelle
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  ❌ {dir_name}/ - MANCANTE")
            dir_path.mkdir(exist_ok=True)
            print(f"  🔧 {dir_name}/ creata")
    
    # Verifica file
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"  ✅ {file_name}")
        else:
            print(f"  ⚠️ {file_name} - MANCANTE")
    
    return True

def check_data():
    """Verifica la presenza dei dati."""
    
    print("\n📊 Verifica dati...")
    
    # Verifica immagini originali
    original_path = Path('data/original')
    if original_path.exists():
        images = list(original_path.glob('*.JPG')) + list(original_path.glob('*.jpg'))
        print(f"  ✅ Immagini originali: {len(images)} file")
    else:
        print("  ⚠️ Cartella immagini originali non trovata")
        print("  💡 Copia le immagini originali in data/original/")
    
    # Verifica immagini con rumore
    noisy_path = Path('data/noisy/noisy_images')
    if noisy_path.exists():
        noise_folders = [d for d in noisy_path.iterdir() if d.is_dir()]
        total_noisy = sum(len(list(folder.glob('*.jpg'))) for folder in noise_folders)
        print(f"  ✅ Immagini con rumore: {total_noisy} file in {len(noise_folders)} categorie")
    else:
        print("  ⚠️ Immagini con rumore non trovate")
        print("  💡 Esegui 'python scripts/add_noise_to_images.py' per generarle")

def create_requirements():
    """Crea file requirements.txt."""
    
    requirements_content = """# Noise Generator Dependencies
opencv-python>=4.5.0
numpy>=1.20.0
matplotlib>=3.3.0
scikit-image>=0.18.0
tqdm>=4.60.0
pathlib
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements_content)
    
    print("  ✅ requirements.txt creato")

def main():
    """Funzione principale di setup."""
    
    print("🎯 NOISE GENERATOR - SETUP")
    print("=" * 40)
    
    # Verifica che siamo nella cartella corretta
    if not Path('README.md').exists():
        print("❌ Esegui questo script dalla cartella noise_generator/")
        sys.exit(1)
    
    # Setup
    print("🚀 Inizializzazione modulo Noise Generator...")
    
    # 1. Verifica struttura
    check_structure()
    
    # 2. Crea requirements
    create_requirements()
    
    # 3. Installa dipendenze
    install_deps = input("\n❓ Installare dipendenze? (y/N): ").lower()
    if install_deps == 'y':
        if install_dependencies():
            print("✅ Dipendenze installate con successo")
        else:
            print("❌ Errore nell'installazione delle dipendenze")
    
    # 4. Verifica dati
    check_data()
    
    # 5. Risultato finale
    print("\n" + "=" * 40)
    print("✅ SETUP COMPLETATO!")
    print("\n🚀 Per iniziare:")
    print("  python quick_start_noise.py")
    print("\n📚 Documentazione:")
    print("  cat README.md")
    print("\n🎯 Generazione rumore:")
    print("  python scripts/add_noise_to_images.py")

if __name__ == "__main__":
    main()
