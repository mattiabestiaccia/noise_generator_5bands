# 🔧 Prompt per Correzione Errore Formato TIFF Multi-banda

## 📋 Analisi Dettagliata del Problema

### 🎯 **Problema Principale**
Il modulo `noise_generator` genera immagini TIFF multi-banda in un formato incompatibile con il modulo `image_registration`. Le immagini risultanti hanno **960 bande invece di 5**, rendendo impossibile l'apertura nel sistema di registrazione immagini.

### 🔍 **Analisi Tecnica**

#### **Formato Atteso (image_registration)**:
```python
# Immagine originale caricata correttamente
Shape: (5, 960, 1280)  # (bande, altezza, larghezza)
Dtype: uint16
Range: 5296 - 65520
```

#### **Formato Prodotto (noise_generator)**:
```python
# Immagine con rumore salvata incorrettamente  
Shape: (960, 1280, 5)  # (altezza, larghezza, bande)
Dtype: uint16
Range: 5296 - 65520
```

### 🚨 **Conseguenze dell'Errore**
1. **Incompatibilità**: Le immagini con rumore non possono essere aperte da `image_registration`
2. **Interpretazione errata**: Il sistema interpreta 960 come numero di bande invece di altezza
3. **Workflow interrotto**: Impossibile utilizzare le immagini generate per test di algoritmi

### 🔍 **Parti di Codice Problematiche**

#### **File**: `noise_generator/scripts/add_noise_to_images.py`

#### **Problema 1: Caricamento Immagini (Righe 55-62)**
```python
# PROBLEMATICO: Converte da formato corretto a formato sbagliato
# Stack delle bande: (bands, height, width) -> (height, width, bands)
if len(bands) > 1:
    image = np.stack(bands, axis=-1)  # ❌ SBAGLIATO: axis=-1
else:
    image = bands[0]
    if len(image.shape) == 2:
        image = np.expand_dims(image, axis=-1)
```

**Problema**: La funzione `load_multiband_image` converte il formato corretto `(5, 960, 1280)` in formato sbagliato `(960, 1280, 5)` usando `axis=-1`.

#### **Problema 2: Salvataggio Immagini (Righe 124-129)**
```python
# PROBLEMATICO: Conversione formato durante salvataggio
# Prepara i dati: (height, width, bands) -> (bands, height, width)
if len(image.shape) == 3:
    bands_data = [image[:, :, i] for i in range(bands)]  # ❌ Assume formato sbagliato
else:
    bands_data = [image]
```

**Problema**: La funzione `save_multiband_image` assume che l'input sia in formato `(height, width, bands)` e cerca di convertirlo, ma questo crea confusione.

#### **Problema 3: Funzioni di Rumore**
Tutte le funzioni di rumore (righe 187-402) sono progettate per lavorare con formato `(height, width, bands)`:
- `add_gaussian_noise`
- `add_salt_pepper_noise` 
- `add_poisson_noise`
- `add_speckle_noise`
- etc.

### 🎯 **Test di Verifica Errore**
```python
# Test eseguito che dimostra il problema
import tifffile

# Immagine originale (corretta)
orig = tifffile.imread('IMG_0002_registered.tif')
print(f'Originale: {orig.shape}')  # Output: (5, 960, 1280) ✅

# Immagine con rumore (sbagliata)
noisy = tifffile.imread('IMG_0002_gaussian_level_03.tif') 
print(f'Con rumore: {noisy.shape}')  # Output: (960, 1280, 5) ❌
```

---

## 🤖 **PROMPT PER LLM**

Sei un esperto sviluppatore Python specializzato in elaborazione di immagini multi-banda e compatibilità tra moduli. 

### **TASK**: Correggere il formato delle immagini TIFF multi-banda nel modulo `noise_generator`

### **PROBLEMA**:
Il modulo `noise_generator` salva immagini TIFF multi-banda nel formato `(altezza, larghezza, bande)` ma il modulo `image_registration` si aspetta il formato `(bande, altezza, larghezza)`. Questo causa incompatibilità totale.

### **SPECIFICHE TECNICHE**:
- **Input originale**: `(5, 960, 1280)` uint16, range 5296-65520
- **Output richiesto**: `(5, 960, 1280)` uint16, range 5296-65520  
- **Formato attuale**: `(960, 1280, 5)` uint16, range 5296-65520 ❌

### **FILE DA MODIFICARE**: 
`noise_generator/scripts/add_noise_to_images.py`

### **AREE PROBLEMATICHE SPECIFICHE**:

1. **Funzione `load_multiband_image` (righe 45-89)**:
   - Attualmente converte `(bands, height, width)` → `(height, width, bands)` 
   - **RICHIESTO**: Mantenere formato originale `(bands, height, width)`

2. **Funzione `save_multiband_image` (righe 92-170)**:
   - Attualmente assume input `(height, width, bands)`
   - **RICHIESTO**: Gestire input `(bands, height, width)` e salvare correttamente

3. **Tutte le funzioni di rumore (righe 187-402)**:
   - Attualmente lavorano con `(height, width, bands)`
   - **RICHIESTO**: Adattare per lavorare con `(bands, height, width)`

### **VINCOLI**:
- ✅ Mantenere compatibilità con immagini RGB/PNG standard
- ✅ Preservare metadati geospaziali TIFF
- ✅ Mantenere range dinamico 16-bit
- ✅ Non rompere funzionalità esistenti
- ✅ Gestire sia formato `(bands, height, width)` che `(height, width, bands)`

### **STRATEGIA SUGGERITA**:
1. **Opzione A**: Modificare tutto per lavorare con `(bands, height, width)`
2. **Opzione B**: Creare funzioni di conversione formato trasparenti
3. **Opzione C**: Rilevamento automatico formato e gestione adattiva

### **TEST DI VERIFICA**:
```python
# Il test deve passare dopo la correzione
orig = tifffile.imread('IMG_0002_registered.tif')          # (5, 960, 1280)
noisy = apply_noise_and_save(orig, 'gaussian', 5)
saved = tifffile.imread('output.tif')
assert orig.shape == saved.shape  # Deve essere True
assert saved.shape == (5, 960, 1280)  # Formato corretto
```

### **DELIVERABLE**:
Fornisci il codice corretto per le funzioni problematiche con:
- Spiegazione delle modifiche
- Gestione robusta dei formati
- Mantenimento compatibilità
- Test di verifica inclusi

### **PRIORITÀ**: CRITICA - Il sistema è attualmente inutilizzabile per immagini multi-banda.

---

## 📝 **Note Aggiuntive per il Debugging**

### **Comando per Test Rapido**:
```bash
cd /home/brus/Projects/HPL/paper/noise_generator
python test_format_fix.py
```

### **File di Riferimento**:
- **Input**: `/home/brus/Projects/HPL/paper/image_registration/projects/test_proj/registered/IMG_0002_registered.tif`
- **Output**: `noise_generator/output/gaussian/IMG_0002_gaussian_level_03.tif`
- **Modulo compatibile**: `/home/brus/Projects/HPL/paper/image_registration/`

### **Dipendenze**:
- `rasterio` (per TIFF multi-banda)
- `tifffile` (per verifica formato)
- `numpy` (manipolazione array)
- `opencv-python` (elaborazione immagini)

### **Risultato Atteso**:
Dopo la correzione, le immagini generate dal `noise_generator` devono essere direttamente utilizzabili nel modulo `image_registration` senza errori di formato o incompatibilità.
