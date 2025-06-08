# Progetto: test_proj

**Descrizione:** Test project with three levels of noise
**Creato:** 2025-06-08 18:58:34

## Struttura Progetto

```
test_proj/
├── input/              # Immagini originali
├── noisy_images/       # Immagini con rumore
│   ├── gaussian/
│   ├── salt_pepper/
│   ├── poisson/
│   ├── speckle/
│   ├── motion_blur/
│   ├── atmospheric/
│   ├── compression/
│   └── iso_noise/
├── analysis/           # Plot e metriche
├── config/            # Configurazioni
├── reports/           # Report elaborazione
└── project_metadata.json
```

## Comandi

### Generazione Rumore
```bash
python scripts/add_noise_to_images.py --project test_projj -l 3
```

### Analisi Metriche
```bash
python scripts/analyze_noise_metrics.py --project test_projj
```

### Gestione Progetto
```bash
# Lista progetti
python scripts/project_manager.py list

# Info progetto
python scripts/project_manager.py info test_projj

# Cleanup progetto
python scripts/project_manager.py clean test_projj
```
