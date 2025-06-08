# 🎯 Noise Generator - Modulo Generazione Rumore

Modulo **indipendente** specializzato nella **generazione di immagini rumorose** da immagini drone UAV per la creazione di dataset di training per algoritmi di denoising.

## 📁 Struttura del Modulo

```
noise_generation/
├── 📁 data/                    # Dati per generazione rumore
│   ├── 📁 original/           # 4 immagini DJI originali
│   ├── 📁 noisy/             # 320 immagini con rumore
│   │   └── 📁 noisy_images/   # Organizzate per tipo (8 cartelle)
│   └── 📁 datasets/          # Dataset organizzati
├── 📁 scripts/               # Script di generazione
│   ├── 🎯 add_noise_to_images.py    # Generatore principale
│   ├── 📊 analyze_noisy_images.py   # Analisi qualità
│   └── 📦 dataset_utils.py          # Gestione dataset
├── 📁 analysis/              # Risultati analisi
│   └── 📁 noise_analysis/    # Metriche e grafici
├── 📁 tests/                 # Test e visualizzazioni
│   ├── 📁 noise_tests/       # Griglie e progressioni
│   └── 🧪 test_noise_generator.py
├── 📁 configs/               # Configurazioni
│   └── ⚙️ noise_config.json  # Config completa rumore
└── 📁 docs/                  # Documentazione
    └── 📖 README_NOISE_GENERATION.md
```

## 🚀 Quick Start

### 1. Generazione Completa
```bash
# Genera tutte le immagini con rumore (320 immagini)
python scripts/add_noise_to_images.py

# Analizza la qualità
python scripts/analyze_noisy_images.py

# Crea visualizzazioni
python tests/test_noise_generator.py
```

### 2. Generazione Personalizzata
```bash
# Solo alcuni tipi di rumore
python scripts/add_noise_to_images.py -i data/original -o data/noisy/custom \
  --noise-types gaussian salt_pepper --levels 5

# Analisi specifica
python scripts/analyze_noisy_images.py -n data/noisy/custom -r analysis/custom
```

### 3. Gestione Dataset
```bash
# Crea subset per training
python scripts/dataset_utils.py subset -o data/datasets/training_set \
  --noise-types gaussian iso_noise --levels 1 3 5 7 10

# Crea split train/val/test
python scripts/dataset_utils.py split -o data/datasets/splits

# Dataset paired per denoising
python scripts/dataset_utils.py paired -o data/datasets/denoising_pairs
```

## 🎯 Tipi di Rumore Disponibili

| Tipo | Descrizione | Parametri | Livelli |
|------|-------------|-----------|---------|
| **gaussian** | Rumore termico sensore | σ: 5-50 | 1-10 |
| **salt_pepper** | Pixel difettosi | prob: 0.001-0.01 | 1-10 |
| **poisson** | Shot noise | scala: 0.1-1.0 | 1-10 |
| **speckle** | Rumore moltiplicativo | var: 0.05-0.5 | 1-10 |
| **motion_blur** | Sfocatura movimento | kernel: 3-21 | 1-10 |
| **atmospheric** | Effetti atmosferici | intensità: 0.1-1.0 | 1-10 |
| **compression** | Artefatti JPEG | qualità: 95-50 | 1-10 |
| **iso_noise** | Rumore alto ISO | luma+chroma | 1-10 |

## 📊 Statistiche Dataset

- **Immagini originali**: 4 (DJI drone)
- **Immagini generate**: 320 (8 tipi × 10 livelli × 4 originali)
- **Spazio occupato**: ~5 GB
- **Formati supportati**: JPG, JPEG, PNG
- **Risoluzione**: Mantenuta dall'originale

## 📈 Metriche di Qualità

Il sistema calcola automaticamente:
- **PSNR** (Peak Signal-to-Noise Ratio) in dB
- **SSIM** (Structural Similarity Index) 0-1  
- **MSE** (Mean Squared Error)
- **SNR** (Signal-to-Noise Ratio) in dB

### Risultati Tipici (Livello 5)

| Tipo | PSNR (dB) | SSIM | Qualità |
|------|-----------|------|---------|
| Compression | 38.66 | 0.9989 | Eccellente |
| Motion Blur | 29.13 | 0.9758 | Buona |
| Gaussian | 23.29 | 0.9751 | Moderata |
| ISO Noise | 15.64 | 0.8712 | Bassa |

## 🎮 Esempi d'Uso

### Ricerca e Sviluppo
```bash
# Dataset per test algoritmi denoising
python scripts/dataset_utils.py subset -o data/datasets/research \
  --noise-types gaussian poisson iso_noise --max-images 100

# Analisi comparativa
python scripts/analyze_noisy_images.py -r analysis/comparison
```

### Training Machine Learning
```bash
# Dataset bilanciato per training
python scripts/dataset_utils.py split -o data/datasets/ml_training \
  --train-ratio 0.8 --val-ratio 0.1 --test-ratio 0.1

# Dataset paired per supervised learning
python scripts/dataset_utils.py paired -o data/datasets/supervised
```

### Benchmark e Valutazione
```bash
# Subset con livelli specifici
python scripts/dataset_utils.py subset -o data/datasets/benchmark \
  --levels 3 5 7 --noise-types gaussian salt_pepper motion_blur
```

## ⚙️ Configurazione

Il file `configs/noise_config.json` contiene:
- Parametri per ogni tipo di rumore
- Soglie di qualità
- Raccomandazioni d'uso
- Configurazioni di default

## 📚 Documentazione Completa

Vedi `docs/README_NOISE_GENERATION.md` per:
- Descrizione dettagliata di ogni tipo di rumore
- Parametri tecnici e calibrazione
- Esempi avanzati di utilizzo
- Best practices per dataset creation

## 🔧 Requisiti

```bash
pip install -r requirements.txt
```

Dipendenze principali:
- opencv-python (elaborazione immagini)
- numpy (calcoli numerici)
- matplotlib (grafici)
- scikit-image (metriche qualità)
- rasterio (supporto TIFF multi-banda)
- tqdm (barre di progresso)

## 📝 Output Files

### Report Automatici
- `analysis/noise_analysis/noise_analysis_report.txt`
- `data/noisy/noisy_images/noise_processing_report.txt`
- `data/datasets/*/subset_statistics.json`

### Visualizzazioni
- `tests/noise_tests/noise_comparison_*.png`
- `tests/noise_tests/intensity_progression_*.png`
- `analysis/noise_analysis/metrics_*_progression.png`

## 🧪 Test e Verifica

### Test Veloce
```bash
# Verifica funzionamento del modulo
python test_quick.py
```

### Test Completo su Immagini TIFF Multi-banda
```bash
# Genera rumore su immagini registrate (esempio)
python scripts/add_noise_to_images.py \
  -i ../image_registration/projects/test_proj/registered \
  -o data -l 3

# Analizza qualità
python scripts/analyze_noisy_images.py \
  -o ../image_registration/projects/test_proj/registered \
  -n data -r analysis/results
```

## 🎯 Raccomandazioni

### Per Tipo di Applicazione
- **Denoising leggero**: Livelli 1-3, tipi gaussian/compression
- **Denoising moderato**: Livelli 4-6, tutti i tipi
- **Denoising intenso**: Livelli 7-10, tipi poisson/iso_noise
- **Test robustezza**: salt_pepper, speckle
- **Simulazione reale**: gaussian, iso_noise, atmospheric

### Per Dataset Size
- **Prototipazione**: 1-2 tipi, 3-5 livelli
- **Sviluppo**: 3-4 tipi, 5-7 livelli
- **Produzione**: Tutti i tipi, tutti i livelli
- **Benchmark**: Subset bilanciato con metriche note

### Supporto Formati
- ✅ **TIFF multi-banda** (5 bande spettrali) - Formato principale
- ✅ **JPEG/PNG** (RGB standard) - Compatibilità
- ✅ **Preservazione metadati** per TIFF geospaziali

---

**Modulo**: Noise Generation v1.0  
**Compatibilità**: Python 3.8+  
**Licenza**: Progetto HPL/WST
