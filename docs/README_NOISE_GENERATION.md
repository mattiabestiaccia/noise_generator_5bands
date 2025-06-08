# Generatore di Rumore per Immagini Drone UAV

Questo progetto fornisce strumenti completi per aggiungere diversi tipi di rumore alle immagini da drone, analizzare la qualità delle immagini risultanti e gestire i dataset generati.

## 📁 Struttura del Progetto

```
denoising_pipeline/
├── inp/                              # Immagini originali (4 immagini DJI)
├── noisy_images/                     # Immagini con rumore generate (320 immagini)
│   ├── gaussian/                     # Rumore gaussiano (40 immagini)
│   ├── salt_pepper/                  # Rumore salt & pepper (40 immagini)
│   ├── poisson/                      # Rumore di Poisson (40 immagini)
│   ├── speckle/                      # Rumore speckle (40 immagini)
│   ├── motion_blur/                  # Motion blur (40 immagini)
│   ├── atmospheric/                  # Effetti atmosferici (40 immagini)
│   ├── compression/                  # Artefatti compressione (40 immagini)
│   ├── iso_noise/                    # Rumore ISO (40 immagini)
│   └── noise_processing_report.txt   # Report del processing
├── noise_analysis/                   # Analisi qualità immagini
│   ├── metrics_*.png                 # Grafici delle metriche
│   └── noise_analysis_report.txt     # Report analisi qualità
├── noise_tests/                      # Test e visualizzazioni
└── scripts/                          # Script principali
```

## 🎯 Tipi di Rumore Implementati

### 1. **Gaussian Noise** 
- **Descrizione**: Rumore termico del sensore
- **Parametri**: Sigma da 5 a 50 (deviazione standard)
- **Uso**: Simula rumore elettronico del sensore

### 2. **Salt & Pepper Noise**
- **Descrizione**: Pixel difettosi casuali
- **Parametri**: Probabilità da 0.001 a 0.01
- **Uso**: Simula pixel morti o difettosi

### 3. **Poisson Noise**
- **Descrizione**: Rumore shot del sensore
- **Parametri**: Scala da 0.1 a 1.0
- **Uso**: Rumore dipendente dall'intensità del segnale

### 4. **Speckle Noise**
- **Descrizione**: Rumore moltiplicativo
- **Parametri**: Varianza da 0.05 a 0.5
- **Uso**: Rumore granulare tipico di alcuni sensori

### 5. **Motion Blur**
- **Descrizione**: Sfocatura da movimento
- **Parametri**: Kernel size da 3 a 21
- **Uso**: Simula problemi di stabilizzazione del drone

### 6. **Atmospheric Noise**
- **Descrizione**: Effetti atmosferici (foschia, vapore)
- **Parametri**: Intensità foschia da 0.1 a 1.0
- **Uso**: Simula condizioni atmosferiche avverse

### 7. **Compression Artifacts**
- **Descrizione**: Artefatti di compressione JPEG
- **Parametri**: Qualità JPEG da 95 a 50
- **Uso**: Testa resilienza alla compressione

### 8. **ISO Noise**
- **Descrizione**: Rumore ad alto ISO (luminanza + crominanza)
- **Parametri**: Sigma luma 5-95, chroma 2-29
- **Uso**: Simula rumore in condizioni di scarsa illuminazione

## 🚀 Script Principali

### 1. `add_noise_to_images.py`
Genera immagini con rumore progressivamente crescente.

```bash
# Uso base
python add_noise_to_images.py

# Uso personalizzato
python add_noise_to_images.py -i input_folder -o output_folder -l 10
```

**Parametri:**
- `-i, --input`: Cartella immagini di input (default: `denoising_pipeline/inp`)
- `-o, --output`: Cartella di output (default: `denoising_pipeline/noisy_images`)
- `-l, --levels`: Numero di livelli di rumore (default: 10)

### 2. `analyze_noisy_images.py`
Analizza la qualità delle immagini con rumore calcolando metriche PSNR, SSIM, MSE, SNR.

```bash
# Uso base
python analyze_noisy_images.py

# Uso personalizzato
python analyze_noisy_images.py -o original_folder -n noisy_folder -r results_folder
```

### 3. `test_noise_generator.py`
Crea visualizzazioni di test per verificare gli effetti del rumore.

```bash
python test_noise_generator.py
```

Genera:
- Griglia di confronto di tutti i tipi di rumore
- Progressioni di intensità per tipi specifici
- Test dettagliati per singoli tipi

### 4. `dataset_utils.py`
Utilità per gestire e organizzare il dataset generato.

```bash
# Crea split train/val/test
python dataset_utils.py split -o dataset_splits

# Crea subset con tipi specifici
python dataset_utils.py subset -o subset --noise-types gaussian salt_pepper --levels 1 3 5

# Crea dataset paired per denoising
python dataset_utils.py paired -o paired_dataset --original inp
```

## 📊 Risultati e Metriche

### Metriche di Qualità Calcolate

1. **PSNR (Peak Signal-to-Noise Ratio)**: Misura la qualità dell'immagine in dB
2. **SSIM (Structural Similarity Index)**: Misura la similarità strutturale (0-1)
3. **MSE (Mean Squared Error)**: Errore quadratico medio
4. **SNR (Signal-to-Noise Ratio)**: Rapporto segnale-rumore in dB

### Risultati Principali (Livello 5)

| Tipo Rumore | PSNR (dB) | SSIM | MSE | SNR (dB) |
|-------------|-----------|------|-----|----------|
| Compression | 38.66 | 0.9989 | 9.62 | 32.94 |
| Motion Blur | 29.13 | 0.9758 | 124.61 | 23.40 |
| Salt & Pepper | 28.43 | 0.9908 | 93.44 | 22.71 |
| Atmospheric | 26.06 | 0.9726 | 172.26 | 20.34 |
| Gaussian | 23.29 | 0.9751 | 305.01 | 17.56 |
| Speckle | 15.87 | 0.8706 | 1715.08 | 10.14 |
| ISO Noise | 15.64 | 0.8712 | 1776.51 | 9.92 |
| Poisson | 11.59 | 0.7192 | 4530.64 | 5.86 |

## 🎯 Raccomandazioni d'Uso

### Per Test di Denoising
- **Leggero**: Livelli 1-3 (PSNR > 30 dB)
- **Moderato**: Livelli 4-6 (PSNR 20-30 dB)
- **Intenso**: Livelli 7-10 (PSNR < 20 dB)

### Per Tipi di Applicazione
- **Realistici per drone**: Gaussian, ISO Noise
- **Test robustezza**: Salt & Pepper, Speckle
- **Problemi meccanici**: Motion Blur
- **Condizioni ambientali**: Atmospheric
- **Problemi di storage**: Compression

## 📈 Grafici e Visualizzazioni

Il sistema genera automaticamente:

1. **Grafici di progressione**: Mostrano come le metriche cambiano con l'intensità
2. **Griglie di confronto**: Confronto visivo di tutti i tipi di rumore
3. **Progressioni di intensità**: Evoluzione del rumore per tipo specifico

## 🔧 Requisiti

```bash
pip install opencv-python numpy matplotlib scikit-image tqdm pathlib
```

## 📝 File di Output

### Report Automatici
- `noise_processing_report.txt`: Statistiche del processing
- `noise_analysis_report.txt`: Analisi qualità dettagliata
- `*.json`: Dati strutturati per ulteriori analisi

### Visualizzazioni
- `noise_comparison_*.png`: Griglie di confronto
- `intensity_progression_*.png`: Progressioni di intensità
- `metrics_*_progression.png`: Grafici delle metriche

## 🎮 Esempi di Uso

### Generazione Completa
```bash
# Genera tutte le immagini con rumore
python add_noise_to_images.py

# Analizza la qualità
python analyze_noisy_images.py

# Crea visualizzazioni di test
python test_noise_generator.py
```

### Dataset per Training
```bash
# Crea dataset paired per denoising
python dataset_utils.py paired -o denoising_dataset

# Crea split per training
python dataset_utils.py split -o training_splits --train-ratio 0.8 --val-ratio 0.1 --test-ratio 0.1
```

### Subset Specifico
```bash
# Solo rumore gaussiano e ISO, livelli bassi
python dataset_utils.py subset -o light_noise \
  --noise-types gaussian iso_noise \
  --levels 1 2 3 \
  --max-images 50
```

## 📊 Statistiche Dataset

- **Immagini originali**: 4
- **Tipi di rumore**: 8
- **Livelli per tipo**: 10
- **Totale immagini generate**: 320
- **Tasso di successo**: 100%
- **Tempo di processing**: ~8 minuti
- **Tempo di analisi**: ~7.5 minuti

## 🔍 Note Tecniche

- Le immagini sono processate mantenendo la risoluzione originale
- Per l'analisi SSIM, le immagini grandi vengono ridimensionate a 800x800 per velocità
- Tutti i parametri di rumore sono calibrati per immagini da drone
- Il sistema preserva i metadati EXIF quando possibile

---

**Autore**: Sistema di Generazione Rumore per Immagini Drone  
**Data**: Generato automaticamente  
**Versione**: 1.0
