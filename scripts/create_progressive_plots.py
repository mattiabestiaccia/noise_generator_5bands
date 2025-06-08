#!/usr/bin/env python3
"""
Script per creare grafici progressivi delle metriche di qualità
al variare del livello di rumore per immagini multispettrali.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import argparse

# Configura stile grafici
try:
    plt.style.use('seaborn-v0_8')
except:
    plt.style.use('seaborn')
sns.set_palette("husl")

def load_analysis_results(results_file):
    """Carica i risultati dell'analisi."""
    with open(results_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_progressive_plots(results, output_folder):
    """Crea grafici progressivi per tutte le metriche."""
    
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Estrai dati
    noise_types = list(results['noise_analysis'].keys())
    metrics = ['psnr', 'ssim', 'mse', 'snr']
    metric_names = {
        'psnr': 'PSNR (dB)',
        'ssim': 'SSIM',
        'mse': 'MSE',
        'snr': 'SNR (dB)'
    }
    
    # Colori per ogni tipo di rumore
    colors = plt.cm.Set3(np.linspace(0, 1, len(noise_types)))
    color_map = dict(zip(noise_types, colors))
    
    print(f"📊 Creando grafici progressivi per {len(noise_types)} tipi di rumore...")
    
    # 1. Grafico combinato di tutte le metriche
    create_combined_metrics_plot(results, noise_types, output_folder, color_map)
    
    # 2. Grafici individuali per ogni metrica
    for metric in metrics:
        create_individual_metric_plot(results, noise_types, metric, metric_names[metric], 
                                    output_folder, color_map)
    
    # 3. Grafico comparativo per immagine
    create_per_image_comparison(results, output_folder)
    
    # 4. Heatmap delle metriche
    create_metrics_heatmap(results, noise_types, output_folder)
    
    # 5. Grafico radar per confronto tipi di rumore
    create_radar_chart(results, noise_types, output_folder)
    
    print(f"✅ Grafici salvati in: {output_folder}")

def create_combined_metrics_plot(results, noise_types, output_folder, color_map):
    """Crea grafico combinato con tutte le metriche."""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Progressione Metriche di Qualità per Tipo di Rumore', fontsize=16, fontweight='bold')
    
    metrics_info = [
        ('psnr', 'PSNR (dB)', axes[0,0], True),
        ('ssim', 'SSIM', axes[0,1], True),
        ('mse', 'MSE', axes[1,0], False),
        ('snr', 'SNR (dB)', axes[1,1], True)
    ]
    
    for metric, title, ax, higher_better in metrics_info:
        
        for noise_type in noise_types:
            levels = []
            values = []
            
            avg_metrics = results['noise_analysis'][noise_type]['avg_metrics']
            
            for level in sorted(avg_metrics.keys(), key=int):
                if metric in avg_metrics[level]:
                    levels.append(int(level))
                    values.append(avg_metrics[level][metric])
            
            if levels and values:
                # Filtra valori infiniti
                finite_mask = np.isfinite(values)
                levels_clean = np.array(levels)[finite_mask]
                values_clean = np.array(values)[finite_mask]
                
                if len(levels_clean) > 0:
                    ax.plot(levels_clean, values_clean, 
                           marker='o', linewidth=2.5, markersize=6,
                           label=noise_type.replace('_', ' ').title(),
                           color=color_map[noise_type])
        
        ax.set_xlabel('Livello di Rumore', fontweight='bold')
        ax.set_ylabel(title, fontweight='bold')
        ax.set_title(f'{title} vs Livello Rumore', fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Aggiungi freccia per indicare direzione migliore
        arrow_text = "↑ Migliore" if higher_better else "↓ Migliore"
        ax.text(0.02, 0.98, arrow_text, transform=ax.transAxes, 
               verticalalignment='top', fontsize=10, 
               bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(output_folder / 'progressive_metrics_combined.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("✓ Grafico combinato creato")

def create_individual_metric_plot(results, noise_types, metric, metric_name, output_folder, color_map):
    """Crea grafico individuale per una metrica specifica."""
    
    plt.figure(figsize=(12, 8))
    
    for noise_type in noise_types:
        levels = []
        values = []
        
        avg_metrics = results['noise_analysis'][noise_type]['avg_metrics']
        
        for level in sorted(avg_metrics.keys(), key=int):
            if metric in avg_metrics[level]:
                levels.append(int(level))
                values.append(avg_metrics[level][metric])
        
        if levels and values:
            # Filtra valori infiniti
            finite_mask = np.isfinite(values)
            levels_clean = np.array(levels)[finite_mask]
            values_clean = np.array(values)[finite_mask]
            
            if len(levels_clean) > 0:
                plt.plot(levels_clean, values_clean, 
                        marker='o', linewidth=3, markersize=8,
                        label=noise_type.replace('_', ' ').title(),
                        color=color_map[noise_type])
    
    plt.xlabel('Livello di Rumore', fontsize=14, fontweight='bold')
    plt.ylabel(metric_name, fontsize=14, fontweight='bold')
    plt.title(f'Progressione {metric_name} per Tipo di Rumore', fontsize=16, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Aggiungi statistiche
    if metric == 'psnr':
        plt.text(0.02, 0.02, "Valori più alti = Migliore qualità", 
                transform=plt.gca().transAxes, fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))
    elif metric == 'ssim':
        plt.text(0.02, 0.02, "Range: 0-1, Valori più alti = Migliore similarità", 
                transform=plt.gca().transAxes, fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))
    elif metric == 'mse':
        plt.text(0.02, 0.98, "Valori più bassi = Migliore qualità", 
                transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(output_folder / f'progressive_{metric}.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✓ Grafico {metric_name} creato")

def create_per_image_comparison(results, output_folder):
    """Crea grafico comparativo per ogni immagine."""
    
    image_analysis = results['image_analysis']
    images = list(image_analysis.keys())
    
    if len(images) == 0:
        return
    
    fig, axes = plt.subplots(len(images), 1, figsize=(14, 4*len(images)))
    if len(images) == 1:
        axes = [axes]
    
    fig.suptitle('Confronto PSNR per Immagine', fontsize=16, fontweight='bold')
    
    colors = plt.cm.tab10(np.linspace(0, 1, 10))
    
    for idx, image_name in enumerate(images):
        ax = axes[idx]
        
        noise_types = list(image_analysis[image_name].keys())
        
        for i, noise_type in enumerate(noise_types):
            levels = []
            psnr_values = []
            
            for level_str, metrics in image_analysis[image_name][noise_type].items():
                level = int(level_str)
                if 'psnr' in metrics and np.isfinite(metrics['psnr']):
                    levels.append(level)
                    psnr_values.append(metrics['psnr'])
            
            if levels and psnr_values:
                ax.plot(levels, psnr_values, 
                       marker='o', linewidth=2, markersize=5,
                       label=noise_type.replace('_', ' ').title(),
                       color=colors[i % len(colors)])
        
        ax.set_xlabel('Livello di Rumore', fontweight='bold')
        ax.set_ylabel('PSNR (dB)', fontweight='bold')
        ax.set_title(f'{image_name}', fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig(output_folder / 'progressive_per_image.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("✓ Grafico per immagine creato")

def create_metrics_heatmap(results, noise_types, output_folder):
    """Crea heatmap delle metriche."""
    
    # Prepara dati per heatmap (livello 3 come esempio)
    metrics_data = []
    labels = []
    
    for noise_type in noise_types:
        avg_metrics = results['noise_analysis'][noise_type]['avg_metrics']
        if '3' in avg_metrics:  # Usa livello 3
            metrics = avg_metrics['3']
            row = [
                metrics.get('psnr', 0) if np.isfinite(metrics.get('psnr', 0)) else 0,
                metrics.get('ssim', 0) * 100,  # Scala SSIM per visualizzazione
                -np.log10(metrics.get('mse', 1)),  # Log inverso di MSE
                metrics.get('snr', 0) if np.isfinite(metrics.get('snr', 0)) else 0
            ]
            metrics_data.append(row)
            labels.append(noise_type.replace('_', ' ').title())
    
    if metrics_data:
        metrics_array = np.array(metrics_data)
        
        plt.figure(figsize=(10, 8))
        
        # Normalizza per confronto
        metrics_norm = (metrics_array - metrics_array.min(axis=0)) / (metrics_array.max(axis=0) - metrics_array.min(axis=0))
        
        sns.heatmap(metrics_norm, 
                   xticklabels=['PSNR', 'SSIM×100', '-log(MSE)', 'SNR'],
                   yticklabels=labels,
                   annot=True, fmt='.3f', cmap='RdYlGn',
                   cbar_kws={'label': 'Qualità Normalizzata (0-1)'})
        
        plt.title('Heatmap Metriche di Qualità (Livello 3)', fontsize=14, fontweight='bold')
        plt.xlabel('Metriche', fontweight='bold')
        plt.ylabel('Tipo di Rumore', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_folder / 'metrics_heatmap.png', 
                    dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print("✓ Heatmap metriche creata")

def create_radar_chart(results, noise_types, output_folder):
    """Crea grafico radar per confronto tipi di rumore."""
    
    # Prepara dati (livello 3)
    categories = ['PSNR', 'SSIM', 'Stabilità MSE', 'SNR']
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]  # Chiudi il cerchio
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(noise_types)))
    
    for i, noise_type in enumerate(noise_types[:6]):  # Limita a 6 per leggibilità
        avg_metrics = results['noise_analysis'][noise_type]['avg_metrics']
        if '3' in avg_metrics:
            metrics = avg_metrics['3']
            
            # Normalizza valori per radar (0-1)
            values = [
                min(metrics.get('psnr', 0) / 10, 1) if np.isfinite(metrics.get('psnr', 0)) else 0,
                metrics.get('ssim', 0) * 50,  # Scala SSIM
                1 - min(np.log10(metrics.get('mse', 1e6)) / 10, 1),  # Inverti MSE
                min(metrics.get('snr', 0) / 10, 1) if np.isfinite(metrics.get('snr', 0)) else 0
            ]
            values += values[:1]  # Chiudi il cerchio
            
            ax.plot(angles, values, 'o-', linewidth=2, 
                   label=noise_type.replace('_', ' ').title(),
                   color=colors[i])
            ax.fill(angles, values, alpha=0.25, color=colors[i])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontweight='bold')
    ax.set_ylim(0, 1)
    ax.set_title('Confronto Radar Tipi di Rumore (Livello 3)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig(output_folder / 'radar_comparison.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("✓ Grafico radar creato")

def main():
    """Funzione principale."""
    
    parser = argparse.ArgumentParser(description='Crea grafici progressivi delle metriche')
    parser.add_argument('-r', '--results', 
                       default='analysis/corrected_results/corrected_analysis_results.json',
                       help='File risultati analisi JSON')
    parser.add_argument('-o', '--output', default='analysis/progressive_plots',
                       help='Cartella output grafici')
    
    args = parser.parse_args()
    
    print("📊 GENERAZIONE GRAFICI PROGRESSIVI")
    print("=" * 50)
    print(f"File risultati: {args.results}")
    print(f"Output: {args.output}")
    print()
    
    # Carica risultati
    if not Path(args.results).exists():
        print(f"⚠ File risultati non trovato: {args.results}")
        print("Esegui prima: python scripts/analyze_multiband_corrected.py")
        return
    
    results = load_analysis_results(args.results)
    
    # Crea grafici
    create_progressive_plots(results, args.output)
    
    print(f"\n🎉 Grafici progressivi completati!")
    print(f"📁 Grafici salvati in: {args.output}")
    print("\nGrafici creati:")
    print("  • progressive_metrics_combined.png - Tutte le metriche")
    print("  • progressive_psnr.png - PSNR dettagliato")
    print("  • progressive_ssim.png - SSIM dettagliato")
    print("  • progressive_mse.png - MSE dettagliato")
    print("  • progressive_snr.png - SNR dettagliato")
    print("  • progressive_per_image.png - Confronto per immagine")
    print("  • metrics_heatmap.png - Heatmap metriche")
    print("  • radar_comparison.png - Confronto radar")

if __name__ == "__main__":
    main()
