#!/usr/bin/env python3
"""
Script per analizzare le immagini con rumore e calcolare metriche di qualità.
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
    print("⚠ rasterio non disponibile. Installare con: pip install rasterio")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠ PIL non disponibile. Installare con: pip install Pillow")


def load_multiband_image(file_path):
    """
    Carica un'immagine multi-banda (TIFF) o standard (JPG/PNG).
    """
    file_path = str(file_path)

    # Prova prima con rasterio per TIFF multi-banda
    if RASTERIO_AVAILABLE and file_path.lower().endswith(('.tif', '.tiff')):
        try:
            with rasterio.open(file_path) as src:
                # Leggi tutte le bande
                bands = []
                for i in range(1, src.count + 1):
                    band = src.read(i)
                    bands.append(band)

                # Stack delle bande: (bands, height, width) -> (height, width, bands)
                if len(bands) > 1:
                    image = np.stack(bands, axis=-1)
                else:
                    image = bands[0]
                    if len(image.shape) == 2:
                        image = np.expand_dims(image, axis=-1)

                return image.astype(np.float32)

        except Exception as e:
            print(f"⚠ Errore caricando con rasterio: {e}")

    # Fallback con PIL per TIFF
    if PIL_AVAILABLE and file_path.lower().endswith(('.tif', '.tiff')):
        try:
            with Image.open(file_path) as img:
                image = np.array(img)
                if len(image.shape) == 2:
                    image = np.expand_dims(image, axis=-1)
                return image.astype(np.float32)
        except Exception as e:
            print(f"⚠ Errore caricando con PIL: {e}")

    # Fallback con OpenCV per immagini standard
    try:
        image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        if image is not None:
            if len(image.shape) == 2:
                image = np.expand_dims(image, axis=-1)
            return image.astype(np.float32)
    except Exception as e:
        print(f"⚠ Errore caricando con OpenCV: {e}")

    return None


def calculate_image_metrics(original, noisy, resize_for_ssim=True):
    """
    Calcola metriche di qualità tra immagine originale e con rumore.

    Args:
        original: Immagine originale
        noisy: Immagine con rumore
        resize_for_ssim: Se True, ridimensiona per calcolo SSIM veloce

    Returns:
        dict: Dizionario con le metriche calcolate
    """

    # Converti in float per i calcoli
    orig_float = original.astype(np.float64)
    noisy_float = noisy.astype(np.float64)

    # MSE (Mean Squared Error)
    mse = np.mean((orig_float - noisy_float) ** 2)

    # PSNR (Peak Signal-to-Noise Ratio)
    if mse == 0:
        psnr = float('inf')
    else:
        psnr = peak_signal_noise_ratio(original, noisy, data_range=255)

    # SSIM (Structural Similarity Index)
    # Converti in grayscale per SSIM se necessario
    if len(original.shape) == 3:
        if original.shape[2] == 3:
            # Immagine RGB standard
            orig_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
            noisy_gray = cv2.cvtColor(noisy, cv2.COLOR_BGR2GRAY)
        else:
            # Immagine multi-banda: usa la prima banda o media delle prime 3
            if original.shape[2] >= 3:
                # Media delle prime 3 bande per simulare RGB
                orig_gray = np.mean(original[:, :, :3], axis=2).astype(np.uint8)
                noisy_gray = np.mean(noisy[:, :, :3], axis=2).astype(np.uint8)
            else:
                # Usa la prima banda
                orig_gray = original[:, :, 0]
                noisy_gray = noisy[:, :, 0]
    else:
        orig_gray = original
        noisy_gray = noisy

    # Ridimensiona per calcolo SSIM più veloce se le immagini sono grandi
    if resize_for_ssim and (orig_gray.shape[0] > 1000 or orig_gray.shape[1] > 1000):
        # Ridimensiona a max 800x800 mantenendo aspect ratio
        h, w = orig_gray.shape
        max_size = 800

        if h > w:
            new_h = max_size
            new_w = int(w * max_size / h)
        else:
            new_w = max_size
            new_h = int(h * max_size / w)

        orig_resized = cv2.resize(orig_gray, (new_w, new_h), interpolation=cv2.INTER_AREA)
        noisy_resized = cv2.resize(noisy_gray, (new_w, new_h), interpolation=cv2.INTER_AREA)

        ssim = structural_similarity(orig_resized, noisy_resized, data_range=255)
    else:
        ssim = structural_similarity(orig_gray, noisy_gray, data_range=255)

    # SNR (Signal-to-Noise Ratio)
    signal_power = np.mean(orig_float ** 2)
    noise_power = np.mean((orig_float - noisy_float) ** 2)

    if noise_power == 0:
        snr = float('inf')
    else:
        snr = 10 * np.log10(signal_power / noise_power)

    return {
        'mse': float(mse),
        'psnr': float(psnr),
        'ssim': float(ssim),
        'snr': float(snr)
    }


def analyze_noise_progression(original_folder, noisy_folder, output_folder):
    """
    Analizza la progressione del rumore per tutti i tipi e livelli.
    """
    
    # Trova immagini originali (inclusi TIFF)
    image_extensions = ['*.JPG', '*.jpg', '*.JPEG', '*.jpeg', '*.png', '*.PNG', '*.tif', '*.tiff', '*.TIF', '*.TIFF']
    original_files = []
    for ext in image_extensions:
        original_files.extend(list(Path(original_folder).glob(ext)))
    
    if not original_files:
        print(f"⚠ Nessuna immagine originale trovata in {original_folder}")
        return
    
    # Trova cartelle di rumore
    noise_folders = [d for d in Path(noisy_folder).iterdir() if d.is_dir()]
    
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
        
        # Analizza ogni tipo di rumore
        for noise_folder in noise_folders:
            noise_type = noise_folder.name
            
            if noise_type not in analysis_results['noise_analysis']:
                analysis_results['noise_analysis'][noise_type] = {
                    'levels': {},
                    'avg_metrics': {}
                }
            
            analysis_results['image_analysis'][base_name][noise_type] = {}
            
            # Analizza ogni livello di rumore
            for level in range(1, 11):
                # Prova diverse estensioni per trovare il file
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
                
                # Calcola metriche
                metrics = calculate_image_metrics(original, noisy)
                
                # Salva risultati
                if level not in analysis_results['noise_analysis'][noise_type]['levels']:
                    analysis_results['noise_analysis'][noise_type]['levels'][level] = []
                
                analysis_results['noise_analysis'][noise_type]['levels'][level].append(metrics)
                analysis_results['image_analysis'][base_name][noise_type][level] = metrics
                analysis_results['summary']['total_comparisons'] += 1
    
    # Calcola metriche medie per ogni tipo di rumore e livello
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
                        'snr': np.mean([m['snr'] for m in metrics_list if m['snr'] != float('inf')])
                    }
        
        analysis_results['noise_analysis'][noise_type]['avg_metrics'] = avg_metrics
    
    # Salva risultati
    results_file = Path(output_folder) / 'noise_analysis_results.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Analisi salvata in: {results_file}")
    
    return analysis_results


def create_metrics_plots(analysis_results, output_folder):
    """
    Crea grafici delle metriche di qualità per ogni tipo di rumore.
    """
    
    noise_types = list(analysis_results['noise_analysis'].keys())
    
    # Crea grafici per ogni metrica
    metrics = ['psnr', 'ssim', 'mse', 'snr']
    metric_names = ['PSNR (dB)', 'SSIM', 'MSE', 'SNR (dB)']
    
    for i, (metric, metric_name) in enumerate(zip(metrics, metric_names)):
        
        plt.figure(figsize=(12, 8))
        
        for noise_type in noise_types:
            levels = []
            values = []
            
            avg_metrics = analysis_results['noise_analysis'][noise_type]['avg_metrics']
            
            for level in range(1, 11):
                if level in avg_metrics:
                    levels.append(level)
                    values.append(avg_metrics[level][metric])
            
            if levels and values:
                plt.plot(levels, values, marker='o', label=noise_type.replace('_', ' ').title(), linewidth=2)
        
        plt.xlabel('Livello di Rumore')
        plt.ylabel(metric_name)
        plt.title(f'Progressione {metric_name} per Tipo di Rumore')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Salva grafico
        plot_file = Path(output_folder) / f'metrics_{metric}_progression.png'
        plt.savefig(plot_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Grafico {metric_name} salvato: {plot_file}")


def create_summary_report(analysis_results, output_folder):
    """
    Crea un report testuale riassuntivo dell'analisi.
    """
    
    report_file = Path(output_folder) / 'noise_analysis_report.txt'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("REPORT ANALISI QUALITÀ IMMAGINI CON RUMORE\n")
        f.write("=" * 50 + "\n\n")
        
        # Riepilogo generale
        f.write("RIEPILOGO GENERALE:\n")
        f.write(f"  Immagini originali analizzate: {analysis_results['summary']['original_images']}\n")
        f.write(f"  Tipi di rumore: {analysis_results['summary']['noise_types']}\n")
        f.write(f"  Confronti totali: {analysis_results['summary']['total_comparisons']}\n\n")
        
        # Analisi per tipo di rumore
        f.write("ANALISI PER TIPO DI RUMORE:\n")
        f.write("-" * 30 + "\n")
        
        for noise_type, data in analysis_results['noise_analysis'].items():
            f.write(f"\n{noise_type.upper().replace('_', ' ')}:\n")
            
            avg_metrics = data['avg_metrics']
            
            if avg_metrics:
                # Trova il livello con la migliore e peggiore qualità (basato su PSNR)
                psnr_values = [(level, metrics['psnr']) for level, metrics in avg_metrics.items() 
                              if metrics['psnr'] != float('inf')]
                
                if psnr_values:
                    best_level = max(psnr_values, key=lambda x: x[1])
                    worst_level = min(psnr_values, key=lambda x: x[1])
                    
                    f.write(f"  Migliore qualità: Livello {best_level[0]} (PSNR: {best_level[1]:.2f} dB)\n")
                    f.write(f"  Peggiore qualità: Livello {worst_level[0]} (PSNR: {worst_level[1]:.2f} dB)\n")
                
                # Metriche per livello 1, 5 e 10
                for level in [1, 5, 10]:
                    if level in avg_metrics:
                        metrics = avg_metrics[level]
                        f.write(f"  Livello {level}:\n")
                        f.write(f"    PSNR: {metrics['psnr']:.2f} dB\n")
                        f.write(f"    SSIM: {metrics['ssim']:.4f}\n")
                        f.write(f"    MSE: {metrics['mse']:.2f}\n")
                        f.write(f"    SNR: {metrics['snr']:.2f} dB\n")
        
        # Raccomandazioni
        f.write("\nRACCOMANDAZIONI:\n")
        f.write("-" * 15 + "\n")
        f.write("• Per test di denoising leggero: usa livelli 1-3\n")
        f.write("• Per test di denoising moderato: usa livelli 4-6\n")
        f.write("• Per test di denoising intenso: usa livelli 7-10\n")
        f.write("• Gaussian e ISO noise sono i più realistici per immagini drone\n")
        f.write("• Salt & pepper è utile per testare robustezza agli outlier\n")
        f.write("• Motion blur simula problemi di stabilizzazione\n")
        f.write("• Compression artifacts testano la resilienza alla compressione\n")
    
    print(f"✓ Report riassuntivo salvato: {report_file}")


def main():
    """Funzione principale."""
    
    parser = argparse.ArgumentParser(description='Analizza la qualità delle immagini con rumore')
    parser.add_argument('-o', '--original', default='data/original',
                       help='Cartella immagini originali (default: data/original)')
    parser.add_argument('-n', '--noisy', default='data/noisy/noisy_images',
                       help='Cartella immagini con rumore (default: data/noisy/noisy_images)')
    parser.add_argument('-r', '--results', default='analysis/noise_analysis',
                       help='Cartella risultati analisi (default: analysis/noise_analysis)')
    
    args = parser.parse_args()
    
    print("ANALISI QUALITÀ IMMAGINI CON RUMORE")
    print("=" * 40)
    print(f"Immagini originali: {args.original}")
    print(f"Immagini con rumore: {args.noisy}")
    print(f"Risultati: {args.results}")
    print()
    
    # Esegui analisi
    print("Calcolando metriche di qualità...")
    results = analyze_noise_progression(args.original, args.noisy, args.results)
    
    if results:
        print("\nCreando grafici delle metriche...")
        create_metrics_plots(results, args.results)
        
        print("\nGenerando report riassuntivo...")
        create_summary_report(results, args.results)
        
        print(f"\n✓ Analisi completata!")
        print(f"Risultati salvati in: {args.results}")
    else:
        print("⚠ Errore durante l'analisi")


if __name__ == "__main__":
    main()
