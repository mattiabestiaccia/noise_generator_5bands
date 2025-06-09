# Project: `test_proj`

**Description:** Test project with three levels of noise
**Created:** 2025-06-08 18:58:34

## Project Structure

```
test_proj/
├── input/              # Original images
├── noisy_images/       # Noisy versions of the images
│   ├── gaussian/
│   ├── salt_pepper/
│   ├── poisson/
│   ├── speckle/
│   ├── motion_blur/
│   ├── atmospheric/
│   ├── compression/
│   └── iso_noise/
├── analysis/           # Plots and evaluation metrics
├── config/             # Configuration files
├── reports/            # Processing reports
└── project_metadata.json
```

## Commands

### Noise Generation

```bash
python scripts/add_noise_to_images.py --project test_proj -l 3
```

### Metric Analysis

```bash
python scripts/analyze_noise_metrics.py --project test_proj
```

### Project Management

```bash
# List available projects
python scripts/project_manager.py list

# Show project info
python scripts/project_manager.py info test_proj

# Clean up project files
python scripts/project_manager.py clean test_proj
```

---

Let me know if you want to adapt it for documentation or a README.
