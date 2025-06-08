#!/usr/bin/env python3
"""
Script corretto per analizzare immagini multi-banda con range dinamico appropriato.
"""

import cv2
import numpy as np
from pathlib import Path
import json
import argparse
from tqdm import tqdm
from skimage.metrics import peak_signal_noise_ratio, structural_similarity
import matplotlib.pyplot as plt

try:
    import rasterio
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def load_multiband_image(file_path):
    """Carica immagine multi-banda."""
    file_path = str(file_path)

    if RASTERIO_AVAILABLE and file_path.lower().endswith(('.tif', '.tiff')):
        try:
            with rasterio.open(file_path) as src:
                bands = []
                for i in range(1, src.count + 1):
                    band = src.read(i)
                    bands.append(band)

                if len(bands) > 1:
                    image = np.stack(bands, axis=-1)
                else:
                    image = bands[0]
                    if len(image.shape) == 2:
                        image = np.expand_dims(image, axis=-1)

                return image.astype(np.float32)
        except Exception as e:
            print(f"⚠ Errore caricando con rasterio: {e}")

    # Fallback con OpenCV
    try:
        image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        if image is not None:
            if len(image.shape) == 2:
                image = np.expand_dims(image, axis=-1)
            return image.astype(np.float32)
    except Exception as e:
        print(f"⚠ Errore caricando con OpenCV: {e}")

    return None


def calculate_multiband_metrics(original, noisy):
    """
    Calcola metriche corrette per immagini multi-banda.
    """
    
    # Determina il range dinamico corretto
    orig_min, orig_max = original.min(), original.max()
    data_range = orig_max - orig_min
    
    print(f"  Range originale: {orig_min:.1f} - {orig_max:.1f}")
    
    # MSE globale
    mse = np.mean((original - noisy) ** 2)
    
    # PSNR con range corretto
    if mse == 0:
        psnr = float('inf')
    else:
        psnr = 20 * np.log10(data_range / np.sqrt(mse))
    
    # SNR
    signal_power = np.mean(original ** 2)
    noise_power = mse
    if noise_power == 0:
        snr = float('inf')
    else:
        snr = 10 * np.log10(signal_power / noise_power)
    
    # SSIM: usa la prima banda o media delle prime 3 bande
    if len(original.shape) == 3:
        if original.shape[2] >= 3:
            # Media delle prime 3 bande
            orig_gray = np.mean(original[:, :, :3], axis=2)
            noisy_gray = np.mean(noisy[:, :, :3], axis=2)
        else:
            # Prima banda
            orig_gray = original[:, :, 0]
            noisy_gray = noisy[:, :, 0]
    else:
        orig_gray = original
        noisy_gray = noisy
    
    # SSIM con range corretto
    gray_range = orig_gray.max() - orig_gray.min()
    ssim = structural_similarity(orig_gray, noisy_gray, data_range=gray_range)
    
    # Metriche per banda (se multi-banda)
    band_metrics = {}
    if len(original.shape) == 3 and original.shape[2] > 1:
        for band in range(original.shape[2]):
            band_orig = original[:, :, band]
            band_noisy = noisy[:, :, band]
            band_range = band_orig.max() - band_orig.min()
            
            band_mse = np.mean((band_orig - band_noisy) ** 2)
            if band_mse == 0:
                band_psnr = float('inf')
            else:
                band_psnr = 20 * np.log10(band_range / np.sqrt(band_mse))
            
            band_ssim = structural_similarity(band_orig, band_noisy, data_range=band_range)
            
            band_metrics[f'band_{band+1}'] = {
                'mse': float(band_mse),
                'psnr': float(band_psnr),
                'ssim': float(band_ssim)
            }
    
    return {
        'mse': float(mse),
        'psnr': float(psnr),
        'ssim': float(ssim),
        'snr': float(snr),
        'data_range': float(data_range),
        'band_metrics': band_metrics
    }


def analyze_corrected(original_folder, noisy_folder, output_folder):
    """Analisi corretta per immagini multi-banda."""
    
    # Trova immagini originali
    image_extensions = ['*.JPG', '*.jpg', '*.JPEG', '*.jpeg', '*.png', '*.PNG', '*.tif', '*.tiff', '*.TIF', '*.TIFF']
    original_files = []
    for ext in image_extensions:
        original_files.extend(list(Path(original_folder).glob(ext)))
    
    if not original_files:
        print(f"⚠ Nessuna immagine originale trovata in {original_folder}")
        return
    
    # Trova cartelle di rumore
    noise_folders = [d for d in Path(noisy_folder).iterdir() if d.is_dir() and d.name != 'real_tiff_noisy']
    
    if not noise_folders:
        print(f"⚠ Nessuna cartella di rumore trovata in {noisy_folder}")
        return
    
    print(f"Analizzando {len(original_files)} immagini originali")
    print(f"Tipi di rumore trovati: {len(noise_folders)}")
    
    # Risultati dell'analisi
    analysis_results = {
        'summary': {
            'original_images': len(original_files),
            'noise_types': len(noise_folders),
            'total_comparisons': 0
        },
        'noise_analysis': {},
        'image_analysis': {}
    }
    
    # Crea cartella di output
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # Analizza ogni immagine originale
    for orig_file in tqdm(original_files, desc="Analizzando immagini"):
        
        # Carica immagine originale
        original = load_multiband_image(orig_file)
        if original is None:
            continue
        
        base_name = orig_file.stem
        analysis_results['image_analysis'][base_name] = {}
        
        print(f"\n📷 {base_name}: shape {original.shape}")
        
        # Analizza ogni tipo di rumore
        for noise_folder in noise_folders:
            noise_type = noise_folder.name
            
            if noise_type not in analysis_results['noise_analysis']:
                analysis_results['noise_analysis'][noise_type] = {
                    'levels': {},
                    'avg_metrics': {}
                }
            
            analysis_results['image_analysis'][base_name][noise_type] = {}
            
            print(f"  🔧 {noise_type}:")
            
            # Analizza ogni livello di rumore
            for level in range(1, 11):
                # Prova diverse estensioni
                noisy_file = None
                for ext in ['.tif', '.jpg', '.png']:
                    candidate = noise_folder / f"{base_name}_{noise_type}_level_{level:02d}{ext}"
                    if candidate.exists():
                        noisy_file = candidate
                        break

                if noisy_file is None:
                    continue

                # Carica immagine con rumore
                noisy = load_multiband_image(noisy_file)
                if noisy is None:
                    continue
                
                # Calcola metriche corrette
                metrics = calculate_multiband_metrics(original, noisy)
                
                print(f"    Livello {level}: PSNR={metrics['psnr']:.2f}dB, SSIM={metrics['ssim']:.4f}")
                
                # Salva risultati
                if level not in analysis_results['noise_analysis'][noise_type]['levels']:
                    analysis_results['noise_analysis'][noise_type]['levels'][level] = []
                
                analysis_results['noise_analysis'][noise_type]['levels'][level].append(metrics)
                analysis_results['image_analysis'][base_name][noise_type][level] = metrics
                analysis_results['summary']['total_comparisons'] += 1
    
    # Calcola metriche medie
    for noise_type in analysis_results['noise_analysis']:
        avg_metrics = {}
        
        for level in range(1, 11):
            if level in analysis_results['noise_analysis'][noise_type]['levels']:
                metrics_list = analysis_results['noise_analysis'][noise_type]['levels'][level]
                
                if metrics_list:
                    avg_metrics[level] = {
                        'mse': np.mean([m['mse'] for m in metrics_list]),
                        'psnr': np.mean([m['psnr'] for m in metrics_list if m['psnr'] != float('inf')]),
                        'ssim': np.mean([m['ssim'] for m in metrics_list]),
                        'snr': np.mean([m['snr'] for m in metrics_list if m['snr'] != float('inf')]),
                        'data_range': np.mean([m['data_range'] for m in metrics_list])
                    }
        
        analysis_results['noise_analysis'][noise_type]['avg_metrics'] = avg_metrics
    
    # Salva risultati
    results_file = Path(output_folder) / 'corrected_analysis_results.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Analisi corretta salvata in: {results_file}")
    
    return analysis_results


def main():
    """Funzione principale."""
    
    parser = argparse.ArgumentParser(description='Analisi corretta per immagini multi-banda')
    parser.add_argument('-o', '--original', default='../image_registration/projects/test_proj/registered',
                       help='Cartella immagini originali')
    parser.add_argument('-n', '--noisy', default='data',
                       help='Cartella immagini con rumore')
    parser.add_argument('-r', '--results', default='analysis/corrected_results',
                       help='Cartella risultati analisi')
    
    args = parser.parse_args()
    
    print("ANALISI CORRETTA IMMAGINI MULTI-BANDA")
    print("=" * 50)
    print(f"Immagini originali: {args.original}")
    print(f"Immagini con rumore: {args.noisy}")
    print(f"Risultati: {args.results}")
    print()
    
    # Esegui analisi corretta
    results = analyze_corrected(args.original, args.noisy, args.results)
    
    if results:
        print(f"\n✅ Analisi corretta completata!")
        print(f"Risultati salvati in: {args.results}")
    else:
        print("⚠ Errore durante l'analisi")


if __name__ == "__main__":
    main()
