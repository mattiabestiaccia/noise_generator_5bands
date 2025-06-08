#!/usr/bin/env python3
"""
Utilità per gestire il dataset di immagini con rumore generato.
"""

import os
import cv2
import numpy as np
from pathlib import Path
import json
import argparse
import random
from tqdm import tqdm
import shutil

def create_training_splits(noisy_folder, output_folder, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
    """
    Crea split train/validation/test dal dataset di immagini con rumore.
    
    Args:
        noisy_folder: Cartella con le immagini con rumore
        output_folder: Cartella di output per gli split
        train_ratio: Percentuale per training (default: 0.7)
        val_ratio: Percentuale per validation (default: 0.2)
        test_ratio: Percentuale per test (default: 0.1)
    """
    
    # Verifica che le percentuali sommino a 1
    if abs(train_ratio + val_ratio + test_ratio - 1.0) > 0.001:
        raise ValueError("Le percentuali devono sommare a 1.0")
    
    # Trova tutte le cartelle di rumore
    noise_folders = [d for d in Path(noisy_folder).iterdir() if d.is_dir()]
    
    if not noise_folders:
        print(f"⚠ Nessuna cartella di rumore trovata in {noisy_folder}")
        return
    
    # Crea cartelle di output
    splits = ['train', 'val', 'test']
    for split in splits:
        for noise_folder in noise_folders:
            split_path = Path(output_folder) / split / noise_folder.name
            split_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Creando split del dataset...")
    print(f"Train: {train_ratio*100:.1f}%, Val: {val_ratio*100:.1f}%, Test: {test_ratio*100:.1f}%")
    
    # Statistiche
    stats = {
        'total_images': 0,
        'train_images': 0,
        'val_images': 0,
        'test_images': 0,
        'noise_types': {}
    }
    
    # Processa ogni tipo di rumore
    for noise_folder in tqdm(noise_folders, desc="Processando tipi di rumore"):
        noise_type = noise_folder.name
        stats['noise_types'][noise_type] = {'train': 0, 'val': 0, 'test': 0}
        
        # Trova tutte le immagini in questa cartella
        image_files = list(noise_folder.glob('*.jpg')) + list(noise_folder.glob('*.JPG'))
        
        if not image_files:
            continue
        
        # Mescola le immagini per split casuale
        random.shuffle(image_files)
        
        # Calcola indici per gli split
        n_total = len(image_files)
        n_train = int(n_total * train_ratio)
        n_val = int(n_total * val_ratio)
        
        # Dividi le immagini
        train_files = image_files[:n_train]
        val_files = image_files[n_train:n_train + n_val]
        test_files = image_files[n_train + n_val:]
        
        # Copia i file negli split appropriati
        for split, files in [('train', train_files), ('val', val_files), ('test', test_files)]:
            for file in files:
                dest_path = Path(output_folder) / split / noise_type / file.name
                shutil.copy2(file, dest_path)
                
                stats['noise_types'][noise_type][split] += 1
                stats[f'{split}_images'] += 1
                stats['total_images'] += 1
    
    # Salva statistiche
    stats_file = Path(output_folder) / 'split_statistics.json'
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Split completato!")
    print(f"Totale immagini: {stats['total_images']}")
    print(f"Train: {stats['train_images']}")
    print(f"Validation: {stats['val_images']}")
    print(f"Test: {stats['test_images']}")
    print(f"Statistiche salvate in: {stats_file}")


def create_noise_subset(noisy_folder, output_folder, noise_types=None, levels=None, max_images_per_type=None):
    """
    Crea un subset del dataset con tipi e livelli di rumore specifici.
    
    Args:
        noisy_folder: Cartella con tutte le immagini con rumore
        output_folder: Cartella di output per il subset
        noise_types: Lista di tipi di rumore da includere (None = tutti)
        levels: Lista di livelli da includere (None = tutti)
        max_images_per_type: Numero massimo di immagini per tipo (None = tutte)
    """
    
    # Trova cartelle di rumore disponibili
    available_noise_folders = [d for d in Path(noisy_folder).iterdir() if d.is_dir()]
    available_noise_types = [d.name for d in available_noise_folders]
    
    # Determina tipi di rumore da includere
    if noise_types is None:
        selected_noise_types = available_noise_types
    else:
        selected_noise_types = [nt for nt in noise_types if nt in available_noise_types]
    
    if not selected_noise_types:
        print("⚠ Nessun tipo di rumore valido specificato")
        return
    
    # Determina livelli da includere
    if levels is None:
        selected_levels = list(range(1, 11))  # Tutti i livelli 1-10
    else:
        selected_levels = levels
    
    print(f"Creando subset del dataset...")
    print(f"Tipi di rumore: {selected_noise_types}")
    print(f"Livelli: {selected_levels}")
    
    # Crea cartella di output
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # Statistiche
    stats = {
        'total_images': 0,
        'noise_types': selected_noise_types,
        'levels': selected_levels,
        'images_per_type': {}
    }
    
    # Processa ogni tipo di rumore selezionato
    for noise_type in tqdm(selected_noise_types, desc="Creando subset"):
        noise_folder = Path(noisy_folder) / noise_type
        
        if not noise_folder.exists():
            continue
        
        # Crea cartella di output per questo tipo
        output_noise_folder = Path(output_folder) / noise_type
        output_noise_folder.mkdir(exist_ok=True)
        
        # Trova immagini per i livelli selezionati
        selected_images = []
        
        for level in selected_levels:
            level_pattern = f"*_level_{level:02d}.jpg"
            level_images = list(noise_folder.glob(level_pattern))
            selected_images.extend(level_images)
        
        # Limita il numero di immagini se specificato
        if max_images_per_type and len(selected_images) > max_images_per_type:
            random.shuffle(selected_images)
            selected_images = selected_images[:max_images_per_type]
        
        # Copia le immagini selezionate
        for img_file in selected_images:
            dest_path = output_noise_folder / img_file.name
            shutil.copy2(img_file, dest_path)
            stats['total_images'] += 1
        
        stats['images_per_type'][noise_type] = len(selected_images)
    
    # Salva statistiche del subset
    subset_stats_file = Path(output_folder) / 'subset_statistics.json'
    with open(subset_stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Subset creato!")
    print(f"Totale immagini: {stats['total_images']}")
    for noise_type, count in stats['images_per_type'].items():
        print(f"  {noise_type}: {count} immagini")
    print(f"Statistiche salvate in: {subset_stats_file}")


def create_paired_dataset(original_folder, noisy_folder, output_folder, noise_types=None):
    """
    Crea un dataset con coppie (originale, rumorosa) per training di denoising.
    
    Args:
        original_folder: Cartella con immagini originali
        noisy_folder: Cartella con immagini con rumore
        output_folder: Cartella di output per il dataset paired
        noise_types: Tipi di rumore da includere (None = tutti)
    """
    
    # Trova immagini originali
    original_files = list(Path(original_folder).glob('*.JPG')) + list(Path(original_folder).glob('*.jpg'))
    
    if not original_files:
        print(f"⚠ Nessuna immagine originale trovata in {original_folder}")
        return
    
    # Trova cartelle di rumore
    noise_folders = [d for d in Path(noisy_folder).iterdir() if d.is_dir()]
    
    if noise_types:
        noise_folders = [d for d in noise_folders if d.name in noise_types]
    
    if not noise_folders:
        print(f"⚠ Nessuna cartella di rumore valida trovata")
        return
    
    # Crea struttura di output
    clean_folder = Path(output_folder) / 'clean'
    noisy_output_folder = Path(output_folder) / 'noisy'
    clean_folder.mkdir(parents=True, exist_ok=True)
    noisy_output_folder.mkdir(parents=True, exist_ok=True)
    
    print(f"Creando dataset paired...")
    print(f"Immagini originali: {len(original_files)}")
    print(f"Tipi di rumore: {[d.name for d in noise_folders]}")
    
    # Statistiche
    stats = {
        'total_pairs': 0,
        'original_images': len(original_files),
        'noise_types': [d.name for d in noise_folders]
    }
    
    pair_index = 0
    
    # Per ogni immagine originale
    for orig_file in tqdm(original_files, desc="Creando coppie"):
        base_name = orig_file.stem
        
        # Per ogni tipo di rumore
        for noise_folder in noise_folders:
            noise_type = noise_folder.name
            
            # Per ogni livello di rumore
            for level in range(1, 11):
                noisy_file = noise_folder / f"{base_name}_{noise_type}_level_{level:02d}.jpg"
                
                if not noisy_file.exists():
                    continue
                
                # Copia immagine originale con nome univoco
                clean_dest = clean_folder / f"clean_{pair_index:06d}.jpg"
                shutil.copy2(orig_file, clean_dest)
                
                # Copia immagine con rumore con nome corrispondente
                noisy_dest = noisy_output_folder / f"noisy_{pair_index:06d}.jpg"
                shutil.copy2(noisy_file, noisy_dest)
                
                pair_index += 1
                stats['total_pairs'] += 1
    
    # Salva statistiche del dataset paired
    paired_stats_file = Path(output_folder) / 'paired_dataset_statistics.json'
    with open(paired_stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Dataset paired creato!")
    print(f"Totale coppie: {stats['total_pairs']}")
    print(f"Cartella clean: {clean_folder}")
    print(f"Cartella noisy: {noisy_output_folder}")
    print(f"Statistiche salvate in: {paired_stats_file}")


def main():
    """Funzione principale."""
    
    parser = argparse.ArgumentParser(description='Utilità per gestire il dataset di immagini con rumore')
    parser.add_argument('command', choices=['split', 'subset', 'paired'], 
                       help='Comando da eseguire')
    parser.add_argument('-n', '--noisy', default='data/noisy/noisy_images',
                       help='Cartella immagini con rumore')
    parser.add_argument('-o', '--output', required=True,
                       help='Cartella di output')
    parser.add_argument('--original', default='data/original',
                       help='Cartella immagini originali (per comando paired)')
    parser.add_argument('--noise-types', nargs='+',
                       help='Tipi di rumore da includere')
    parser.add_argument('--levels', nargs='+', type=int,
                       help='Livelli di rumore da includere')
    parser.add_argument('--max-images', type=int,
                       help='Numero massimo di immagini per tipo')
    parser.add_argument('--train-ratio', type=float, default=0.7,
                       help='Percentuale per training (default: 0.7)')
    parser.add_argument('--val-ratio', type=float, default=0.2,
                       help='Percentuale per validation (default: 0.2)')
    parser.add_argument('--test-ratio', type=float, default=0.1,
                       help='Percentuale per test (default: 0.1)')
    
    args = parser.parse_args()
    
    print(f"DATASET UTILS - Comando: {args.command.upper()}")
    print("=" * 40)
    
    if args.command == 'split':
        create_training_splits(
            args.noisy, 
            args.output,
            args.train_ratio,
            args.val_ratio, 
            args.test_ratio
        )
    
    elif args.command == 'subset':
        create_noise_subset(
            args.noisy,
            args.output,
            args.noise_types,
            args.levels,
            args.max_images
        )
    
    elif args.command == 'paired':
        create_paired_dataset(
            args.original,
            args.noisy,
            args.output,
            args.noise_types
        )


if __name__ == "__main__":
    main()
