#!/usr/bin/env python3
"""
Script per analizzare le metriche di qualità delle immagini con rumore.
Calcola PSNR, SSIM, MSE e altre metriche per valutare l'impatto del rumore.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pandas as pd
import json
from tqdm import tqdm
import argparse

# Aggiungi il percorso degli scripts
sys.path.append(str(Path(__file__).parent))

try:
    from skimage.metrics import peak_signal_noise_ratio, structural_similarity
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False
    print("⚠ scikit-image non disponibile. Installare con: pip install scikit-image")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠ OpenCV non disponibile. Installare con: pip install opencv-python")

from add_noise_to_images import load_multiband_image

class NoiseMetricsAnalyzer:
    """Analizzatore di metriche per immagini con rumore."""
    
    def __init__(self):
        self.metrics_data = []
        self.noise_types = [
            'gaussian', 'salt_pepper', 'poisson', 'speckle',
            'motion_blur', 'atmospheric', 'compression', 'iso_noise'
        ]
        
    def calculate_psnr(self, original, noisy):
        """Calcola Peak Signal-to-Noise Ratio."""
        if not SKIMAGE_AVAILABLE:
            # Implementazione manuale
            mse = np.mean((original.astype(np.float64) - noisy.astype(np.float64)) ** 2)
            if mse == 0:
                return float('inf')
            max_pixel = np.max(original)
            return 20 * np.log10(max_pixel / np.sqrt(mse))
        else:
            # Usa scikit-image
            data_range = original.max() - original.min()
            return peak_signal_noise_ratio(original, noisy, data_range=data_range)
    
    def calculate_ssim(self, original, noisy):
        """Calcola Structural Similarity Index."""
        if not SKIMAGE_AVAILABLE:
            # Implementazione semplificata
            mu1 = np.mean(original)
            mu2 = np.mean(noisy)
            sigma1_sq = np.var(original)
            sigma2_sq = np.var(noisy)
            sigma12 = np.mean((original - mu1) * (noisy - mu2))
            
            c1 = (0.01 * (original.max() - original.min())) ** 2
            c2 = (0.03 * (original.max() - original.min())) ** 2
            
            ssim = ((2 * mu1 * mu2 + c1) * (2 * sigma12 + c2)) / \
                   ((mu1 ** 2 + mu2 ** 2 + c1) * (sigma1_sq + sigma2_sq + c2))
            return ssim
        else:
            # Usa scikit-image per immagini multi-banda
            if len(original.shape) == 3:
                # Calcola SSIM per ogni banda e media
                ssim_values = []
                for band in range(original.shape[0]):
                    data_range = original[band].max() - original[band].min()
                    ssim_band = structural_similarity(
                        original[band], noisy[band], 
                        data_range=data_range
                    )
                    ssim_values.append(ssim_band)
                return np.mean(ssim_values)
            else:
                data_range = original.max() - original.min()
                return structural_similarity(original, noisy, data_range=data_range)
    
    def calculate_mse(self, original, noisy):
        """Calcola Mean Squared Error."""
        return np.mean((original.astype(np.float64) - noisy.astype(np.float64)) ** 2)
    
    def calculate_mae(self, original, noisy):
        """Calcola Mean Absolute Error."""
        return np.mean(np.abs(original.astype(np.float64) - noisy.astype(np.float64)))
    
    def calculate_snr(self, original, noisy):
        """Calcola Signal-to-Noise Ratio."""
        signal_power = np.mean(original.astype(np.float64) ** 2)
        noise_power = np.mean((original.astype(np.float64) - noisy.astype(np.float64)) ** 2)
        if noise_power == 0:
            return float('inf')
        return 10 * np.log10(signal_power / noise_power)
    
    def calculate_histogram_metrics(self, original, noisy):
        """Calcola metriche basate su istogramma."""
        # Converti a formato standard per istogramma
        if len(original.shape) == 3:
            # Per immagini multi-banda, usa la prima banda
            orig_hist = original[0].flatten()
            noisy_hist = noisy[0].flatten()
        else:
            orig_hist = original.flatten()
            noisy_hist = noisy.flatten()
        
        # Calcola istogrammi
        hist_orig, bins = np.histogram(orig_hist, bins=256, density=True)
        hist_noisy, _ = np.histogram(noisy_hist, bins=bins, density=True)
        
        # Correlazione istogrammi
        hist_corr = np.corrcoef(hist_orig, hist_noisy)[0, 1]
        
        # Distanza chi-quadrato
        chi2_dist = np.sum((hist_orig - hist_noisy) ** 2 / (hist_orig + hist_noisy + 1e-10))
        
        return {
            'histogram_correlation': hist_corr,
            'chi2_distance': chi2_dist
        }
    
    def analyze_image_pair(self, original_path, noisy_path, noise_type, level, image_name):
        """Analizza una coppia di immagini (originale vs rumorosa)."""
        try:
            # Carica immagini
            original = load_multiband_image(original_path)
            noisy = load_multiband_image(noisy_path)
            
            # Verifica che abbiano la stessa forma
            if original.shape != noisy.shape:
                print(f"⚠ Forme diverse: {original.shape} vs {noisy.shape}")
                return None
            
            # Calcola metriche
            psnr = self.calculate_psnr(original, noisy)
            ssim = self.calculate_ssim(original, noisy)
            mse = self.calculate_mse(original, noisy)
            mae = self.calculate_mae(original, noisy)
            snr = self.calculate_snr(original, noisy)
            hist_metrics = self.calculate_histogram_metrics(original, noisy)
            
            # Calcola metriche per banda (se multi-banda)
            band_metrics = {}
            if len(original.shape) == 3:
                for band in range(original.shape[0]):
                    band_psnr = self.calculate_psnr(original[band], noisy[band])
                    band_ssim = self.calculate_ssim(original[band], noisy[band])
                    band_metrics[f'band_{band+1}_psnr'] = band_psnr
                    band_metrics[f'band_{band+1}_ssim'] = band_ssim
            
            metrics = {
                'image_name': image_name,
                'noise_type': noise_type,
                'level': level,
                'psnr': psnr,
                'ssim': ssim,
                'mse': mse,
                'mae': mae,
                'snr': snr,
                'shape': str(original.shape),
                'dtype': str(original.dtype),
                **hist_metrics,
                **band_metrics
            }
            
            return metrics
            
        except Exception as e:
            print(f"⚠ Errore analizzando {noisy_path}: {e}")
            return None
    
    def analyze_noise_dataset(self, original_folder, noisy_folder, levels=3):
        """Analizza tutto il dataset di immagini con rumore."""
        print("🔍 Analizzando dataset immagini con rumore...")
        
        # Trova immagini originali
        original_folder = Path(original_folder)
        noisy_folder = Path(noisy_folder)
        
        original_files = list(original_folder.glob('*.tif')) + list(original_folder.glob('*.tiff'))
        
        if not original_files:
            print(f"⚠ Nessuna immagine originale trovata in {original_folder}")
            return
        
        print(f"📷 Trovate {len(original_files)} immagini originali")
        
        # Analizza ogni combinazione
        total_analyses = len(original_files) * len(self.noise_types) * levels
        print(f"📊 Analisi totali da eseguire: {total_analyses}")
        
        with tqdm(total=total_analyses, desc="Analizzando metriche") as pbar:
            for original_file in original_files:
                image_name = original_file.stem
                
                for noise_type in self.noise_types:
                    noise_folder_path = noisy_folder / noise_type
                    
                    if not noise_folder_path.exists():
                        print(f"⚠ Cartella {noise_folder_path} non trovata")
                        pbar.update(levels)
                        continue
                    
                    for level in range(1, levels + 1):
                        # Costruisci nome file rumoroso
                        noisy_filename = f"{image_name}_{noise_type}_level_{level:02d}.tif"
                        noisy_path = noise_folder_path / noisy_filename
                        
                        if not noisy_path.exists():
                            print(f"⚠ File {noisy_path} non trovato")
                            pbar.update(1)
                            continue
                        
                        # Analizza coppia
                        metrics = self.analyze_image_pair(
                            original_file, noisy_path, 
                            noise_type, level, image_name
                        )
                        
                        if metrics:
                            self.metrics_data.append(metrics)
                        
                        pbar.update(1)
        
        print(f"✅ Analisi completata: {len(self.metrics_data)} metriche calcolate")
    
    def create_metrics_plots(self, output_folder):
        """Crea plot delle metriche."""
        if not self.metrics_data:
            print("⚠ Nessun dato di metriche disponibile")
            return
        
        output_folder = Path(output_folder)
        output_folder.mkdir(exist_ok=True)
        
        # Converti in DataFrame
        df = pd.DataFrame(self.metrics_data)
        
        # Configura stile plot
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Plot 1: PSNR vs Livello di rumore
        plt.figure(figsize=(12, 8))
        for noise_type in self.noise_types:
            data = df[df['noise_type'] == noise_type]
            if not data.empty:
                levels = data['level'].values
                psnr_values = data['psnr'].values
                plt.plot(levels, psnr_values, 'o-', label=noise_type, linewidth=2, markersize=6)
        
        plt.xlabel('Livello di Rumore', fontsize=12)
        plt.ylabel('PSNR (dB)', fontsize=12)
        plt.title('Peak Signal-to-Noise Ratio vs Livello di Rumore', fontsize=14, fontweight='bold')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_folder / 'psnr_vs_noise_level.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 2: SSIM vs Livello di rumore
        plt.figure(figsize=(12, 8))
        for noise_type in self.noise_types:
            data = df[df['noise_type'] == noise_type]
            if not data.empty:
                levels = data['level'].values
                ssim_values = data['ssim'].values
                plt.plot(levels, ssim_values, 'o-', label=noise_type, linewidth=2, markersize=6)
        
        plt.xlabel('Livello di Rumore', fontsize=12)
        plt.ylabel('SSIM', fontsize=12)
        plt.title('Structural Similarity Index vs Livello di Rumore', fontsize=14, fontweight='bold')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_folder / 'ssim_vs_noise_level.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 3: Heatmap metriche
        plt.figure(figsize=(14, 10))
        
        # Crea matrice per heatmap
        metrics_matrix = df.pivot_table(
            values='psnr', 
            index='noise_type', 
            columns='level', 
            aggfunc='mean'
        )
        
        sns.heatmap(metrics_matrix, annot=True, fmt='.1f', cmap='RdYlBu_r', 
                   cbar_kws={'label': 'PSNR (dB)'})
        plt.title('PSNR Heatmap: Tipo di Rumore vs Livello', fontsize=14, fontweight='bold')
        plt.xlabel('Livello di Rumore', fontsize=12)
        plt.ylabel('Tipo di Rumore', fontsize=12)
        plt.tight_layout()
        plt.savefig(output_folder / 'psnr_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 4: SSIM Heatmap
        plt.figure(figsize=(14, 10))
        
        ssim_matrix = df.pivot_table(
            values='ssim', 
            index='noise_type', 
            columns='level', 
            aggfunc='mean'
        )
        
        sns.heatmap(ssim_matrix, annot=True, fmt='.3f', cmap='RdYlBu_r',
                   cbar_kws={'label': 'SSIM'})
        plt.title('SSIM Heatmap: Tipo di Rumore vs Livello', fontsize=14, fontweight='bold')
        plt.xlabel('Livello di Rumore', fontsize=12)
        plt.ylabel('Tipo di Rumore', fontsize=12)
        plt.tight_layout()
        plt.savefig(output_folder / 'ssim_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 5: Distribuzione metriche per tipo di rumore
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # PSNR distribution
        df.boxplot(column='psnr', by='noise_type', ax=axes[0,0])
        axes[0,0].set_title('Distribuzione PSNR per Tipo di Rumore')
        axes[0,0].set_xlabel('Tipo di Rumore')
        axes[0,0].set_ylabel('PSNR (dB)')
        
        # SSIM distribution
        df.boxplot(column='ssim', by='noise_type', ax=axes[0,1])
        axes[0,1].set_title('Distribuzione SSIM per Tipo di Rumore')
        axes[0,1].set_xlabel('Tipo di Rumore')
        axes[0,1].set_ylabel('SSIM')
        
        # MSE distribution
        df.boxplot(column='mse', by='noise_type', ax=axes[1,0])
        axes[1,0].set_title('Distribuzione MSE per Tipo di Rumore')
        axes[1,0].set_xlabel('Tipo di Rumore')
        axes[1,0].set_ylabel('MSE')
        
        # SNR distribution
        df.boxplot(column='snr', by='noise_type', ax=axes[1,1])
        axes[1,1].set_title('Distribuzione SNR per Tipo di Rumore')
        axes[1,1].set_xlabel('Tipo di Rumore')
        axes[1,1].set_ylabel('SNR (dB)')
        
        plt.suptitle('Distribuzione Metriche di Qualità per Tipo di Rumore', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_folder / 'metrics_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 6: Correlazione metriche
        plt.figure(figsize=(10, 8))
        
        metrics_cols = ['psnr', 'ssim', 'mse', 'mae', 'snr']
        correlation_matrix = df[metrics_cols].corr()
        
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, cbar_kws={'label': 'Correlazione'})
        plt.title('Matrice di Correlazione tra Metriche', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_folder / 'metrics_correlation.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Plot salvati in: {output_folder}")
        
        # Lista file generati
        plot_files = [
            'psnr_vs_noise_level.png',
            'ssim_vs_noise_level.png', 
            'psnr_heatmap.png',
            'ssim_heatmap.png',
            'metrics_distribution.png',
            'metrics_correlation.png'
        ]
        
        for plot_file in plot_files:
            print(f"  📊 {plot_file}")
    
    def save_metrics_report(self, output_folder):
        """Salva report dettagliato delle metriche."""
        if not self.metrics_data:
            print("⚠ Nessun dato di metriche disponibile")
            return
        
        output_folder = Path(output_folder)
        output_folder.mkdir(exist_ok=True)
        
        # Salva dati grezzi JSON
        with open(output_folder / 'noise_metrics_raw.json', 'w') as f:
            json.dump(self.metrics_data, f, indent=2, default=str)
        
        # Salva CSV
        df = pd.DataFrame(self.metrics_data)
        df.to_csv(output_folder / 'noise_metrics.csv', index=False)
        
        # Calcola statistiche riassuntive
        summary_stats = {}
        
        for noise_type in self.noise_types:
            type_data = df[df['noise_type'] == noise_type]
            if not type_data.empty:
                summary_stats[noise_type] = {
                    'psnr_mean': float(type_data['psnr'].mean()),
                    'psnr_std': float(type_data['psnr'].std()),
                    'ssim_mean': float(type_data['ssim'].mean()),
                    'ssim_std': float(type_data['ssim'].std()),
                    'mse_mean': float(type_data['mse'].mean()),
                    'samples': len(type_data)
                }
        
        # Salva report testuale
        with open(output_folder / 'noise_metrics_report.txt', 'w') as f:
            f.write("REPORT ANALISI METRICHE RUMORE IMMAGINI\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("RIEPILOGO GENERALE:\n")
            f.write(f"  Immagini analizzate: {len(df['image_name'].unique())}\n")
            f.write(f"  Tipi di rumore: {len(df['noise_type'].unique())}\n")
            f.write(f"  Livelli per tipo: {len(df['level'].unique())}\n")
            f.write(f"  Totale analisi: {len(df)}\n\n")
            
            f.write("STATISTICHE PER TIPO DI RUMORE:\n")
            for noise_type, stats in summary_stats.items():
                f.write(f"\n  {noise_type.upper()}:\n")
                f.write(f"    PSNR: {stats['psnr_mean']:.2f} ± {stats['psnr_std']:.2f} dB\n")
                f.write(f"    SSIM: {stats['ssim_mean']:.3f} ± {stats['ssim_std']:.3f}\n")
                f.write(f"    MSE: {stats['mse_mean']:.2f}\n")
                f.write(f"    Campioni: {stats['samples']}\n")
            
            # Trova migliori e peggiori per PSNR
            f.write("\nCLASSIFICA QUALITÀ (PSNR medio):\n")
            psnr_ranking = df.groupby('noise_type')['psnr'].mean().sort_values(ascending=False)
            for i, (noise_type, psnr) in enumerate(psnr_ranking.items(), 1):
                f.write(f"  {i}. {noise_type}: {psnr:.2f} dB\n")
            
            # Trova migliori e peggiori per SSIM
            f.write("\nCLASSIFICA QUALITÀ (SSIM medio):\n")
            ssim_ranking = df.groupby('noise_type')['ssim'].mean().sort_values(ascending=False)
            for i, (noise_type, ssim) in enumerate(ssim_ranking.items(), 1):
                f.write(f"  {i}. {noise_type}: {ssim:.3f}\n")
        
        print(f"✅ Report salvato in: {output_folder}")


def main():
    """Funzione principale."""
    parser = argparse.ArgumentParser(description='Analizza metriche di qualità delle immagini con rumore')
    
    # Opzione progetto o percorsi manuali
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--project', help='Nome del progetto (usa struttura projects/)')
    group.add_argument('-o', '--original', help='Cartella immagini originali')
    
    parser.add_argument('-n', '--noisy', help='Cartella immagini con rumore (ignorato se --project)')
    parser.add_argument('-r', '--results', help='Cartella risultati analisi (ignorato se --project)')
    parser.add_argument('-l', '--levels', type=int, default=3,
                       help='Numero di livelli di rumore da analizzare')
    
    args = parser.parse_args()
    
    # Determina percorsi
    if args.project:
        # Modalità progetto
        script_dir = Path(__file__).parent.parent
        projects_dir = script_dir / "projects"
        project_path = projects_dir / args.project
        
        if not project_path.exists():
            print(f"❌ Progetto '{args.project}' non trovato in {projects_dir}")
            print("💡 Crea il progetto con: python scripts/project_manager.py create {args.project}")
            return
        
        original_dir = project_path / "input"
        noisy_dir = project_path / "noisy_images"
        results_dir = project_path / "analysis"
        
        # Importa project manager per logging
        try:
            import sys
            sys.path.append(str(Path(__file__).parent))
            from project_manager import NoiseProjectManager
            project_manager = NoiseProjectManager()
        except ImportError:
            project_manager = None
        
    else:
        # Modalità tradizionale
        original_dir = args.original or '/home/brus/Projects/HPL/paper/image_registration/projects/test_proj/registered'
        noisy_dir = args.noisy or 'noisy_images'
        results_dir = args.results or 'analysis'
        project_manager = None
    
    print("📊 ANALISI METRICHE RUMORE IMMAGINI DRONE")
    print("=" * 50)
    if args.project:
        print(f"📁 Progetto: {args.project}")
        print(f"📂 Percorso: {project_path}")
    print(f"📥 Immagini originali: {original_dir}")
    print(f"🔧 Immagini con rumore: {noisy_dir}")
    print(f"📊 Risultati: {results_dir}")
    print(f"🎚 Livelli di rumore: {args.levels}")
    print()
    
    # Verifica percorsi
    if not Path(original_dir).exists():
        print(f"❌ Cartella originali non trovata: {original_dir}")
        if args.project:
            print(f"💡 Copia le immagini originali in: {original_dir}")
        return
    
    if not Path(noisy_dir).exists():
        print(f"❌ Cartella immagini con rumore non trovata: {noisy_dir}")
        if args.project:
            print(f"💡 Genera prima il rumore con: python scripts/add_noise_to_images.py --project {args.project}")
        return
    
    # Crea analizzatore
    analyzer = NoiseMetricsAnalyzer()
    
    # Analizza dataset
    analyzer.analyze_noise_dataset(original_dir, noisy_dir, args.levels)
    
    if analyzer.metrics_data:
        # Crea plot
        analyzer.create_metrics_plots(results_dir)
        
        # Salva report
        analyzer.save_metrics_report(results_dir)
        
        # Se modalità progetto, aggiorna metadata
        if args.project and project_manager:
            analysis_details = {
                "metrics_calculated": len(analyzer.metrics_data),
                "noise_levels_analyzed": args.levels,
                "noise_types": len(analyzer.noise_types),
                "plots_generated": 6,
                "best_noise_type_psnr": "salt_pepper",  # Placeholder, calcolato dinamicamente
                "worst_noise_type_psnr": "motion_blur"   # Placeholder, calcolato dinamicamente
            }
            
            # Calcola metriche riassuntive
            df = pd.DataFrame(analyzer.metrics_data)
            if not df.empty:
                psnr_by_type = df.groupby('noise_type')['psnr'].mean().sort_values(ascending=False)
                analysis_details["best_noise_type_psnr"] = psnr_by_type.index[0]
                analysis_details["worst_noise_type_psnr"] = psnr_by_type.index[-1]
                analysis_details["avg_psnr_range"] = f"{psnr_by_type.iloc[-1]:.1f} - {psnr_by_type.iloc[0]:.1f} dB"
            
            project_manager.add_processing_record(
                args.project,
                "metrics_analysis", 
                analysis_details
            )
        
        print(f"\n✅ ANALISI COMPLETATA!")
        print(f"📊 Plot e report salvati in: {results_dir}")
        
        # Mostra riassunto risultati
        df = pd.DataFrame(analyzer.metrics_data)
        if not df.empty:
            print(f"\n📈 RIASSUNTO RISULTATI:")
            psnr_by_type = df.groupby('noise_type')['psnr'].mean().sort_values(ascending=False)
            print(f"   🥇 Migliore qualità: {psnr_by_type.index[0]} ({psnr_by_type.iloc[0]:.1f} dB)")
            print(f"   🥉 Peggiore qualità: {psnr_by_type.index[-1]} ({psnr_by_type.iloc[-1]:.1f} dB)")
            print(f"   📊 Range PSNR: {psnr_by_type.iloc[-1]:.1f} - {psnr_by_type.iloc[0]:.1f} dB")
            print(f"   🔢 Analisi totali: {len(analyzer.metrics_data)}")
        
        if args.project:
            print(f"\n📁 File generati:")
            results_path = Path(results_dir)
            if results_path.exists():
                for file in sorted(results_path.glob("*.png")):
                    print(f"   📊 {file.name}")
                for file in sorted(results_path.glob("*.txt")):
                    print(f"   📄 {file.name}")
                for file in sorted(results_path.glob("*.csv")):
                    print(f"   📋 {file.name}")
    else:
        print("❌ Nessun dato analizzato. Verificare i percorsi.")
        if args.project:
            print(f"💡 Assicurati di aver generato il rumore prima con:")
            print(f"   python scripts/add_noise_to_images.py --project {args.project}")


if __name__ == "__main__":
    main()