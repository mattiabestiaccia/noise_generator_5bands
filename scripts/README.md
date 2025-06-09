# Scripts Module

Command-line tools and core functionality for multispectral noise generation and analysis.

## Overview

This module contains the core scripts for generating noise on multispectral images, analyzing results, and managing projects. All scripts can be used independently or integrated with the GUI.

## Core Scripts

### Noise Generation

**`add_noise_to_images.py`**
- Main noise generation engine
- Supports 8 different noise types
- Configurable intensity levels
- Batch processing capabilities
- Preserves multispectral metadata

**Usage:**
```bash
python add_noise_to_images.py --input image.tif --output noisy/ --noise gaussian --levels 5
```

### Analysis Tools

**`analyze_noise_metrics.py`**
- Comprehensive noise analysis
- PSNR, SSIM, MSE calculations
- Per-band and overall metrics
- Statistical analysis and reporting

**`analyze_noisy_images.py`**
- Image quality assessment
- Noise characterization
- Comparative analysis between noise types

**`analyze_multiband_corrected.py`**
- Corrected analysis for multispectral data
- Band-specific noise impact assessment
- Spectral signature preservation analysis

### Visualization

**`create_progressive_plots.py`**
- Progressive noise level visualization
- Comparative plots across noise types
- Quality metrics visualization
- Publication-ready figures

### Utilities

**`project_manager.py`**
- Project structure management
- Metadata handling
- Batch operations
- Integration with GUI

**`dataset_utils.py`**
- Dataset preparation utilities
- File organization tools
- Batch processing helpers

## Noise Types

### 1. Gaussian Noise
**File:** `add_noise_to_images.py`
- **Description:** Thermal sensor noise simulation
- **Parameter:** Standard deviation (σ)
- **Range:** 5-50
- **Use Case:** Basic sensor noise modeling

### 2. Salt & Pepper Noise
- **Description:** Dead/hot pixel simulation
- **Parameter:** Corruption probability
- **Range:** 0.001-0.01
- **Use Case:** Sensor defect modeling

### 3. Poisson Noise
- **Description:** Shot noise simulation
- **Parameter:** Scale factor
- **Range:** 0.1-1.0
- **Use Case:** Signal-dependent noise

### 4. Speckle Noise
- **Description:** Multiplicative noise
- **Parameter:** Variance
- **Range:** 0.05-0.5
- **Use Case:** Optical interference simulation

### 5. Motion Blur
- **Description:** Movement-induced blur
- **Parameter:** Kernel size
- **Range:** 3-21 pixels
- **Use Case:** Platform/subject movement

### 6. Atmospheric Effects
- **Description:** Haze and vapor simulation
- **Parameter:** Haze intensity
- **Range:** 0.1-1.0
- **Use Case:** Environmental conditions

### 7. Compression Artifacts
- **Description:** JPEG compression simulation
- **Parameter:** Quality (inverse)
- **Range:** 50-95
- **Use Case:** Data transmission effects

### 8. ISO Noise
- **Description:** High ISO sensitivity noise
- **Parameter:** ISO level
- **Range:** 1-10
- **Use Case:** Low-light conditions

## Usage Examples

### Basic Noise Generation
```bash
# Single noise type
python add_noise_to_images.py \
    --input image.tif \
    --output noisy_images/ \
    --noise gaussian \
    --levels 5

# Multiple noise types
python add_noise_to_images.py \
    --input image.tif \
    --output noisy_images/ \
    --noise gaussian salt_pepper poisson \
    --levels 10
```

### Batch Processing
```bash
# Process entire directory
python add_noise_to_images.py \
    --input images/ \
    --output noisy_images/ \
    --noise all \
    --levels 5

# With project management
python project_manager.py \
    --create new_project \
    --input images/ \
    --noise gaussian poisson \
    --levels 8
```

### Analysis
```bash
# Analyze noise metrics
python analyze_noise_metrics.py \
    --original image.tif \
    --noisy noisy_images/ \
    --output analysis/

# Create visualization plots
python create_progressive_plots.py \
    --project project_name \
    --output plots/
```

## Configuration

### Noise Configuration
Edit `configs/noise_config.json` to customize:
- Noise type parameters
- Default intensity ranges
- Processing options

### Project Structure
Projects are organized as:
```
project_name/
├── input/              # Original images
├── noisy_images/       # Generated noisy images
│   ├── gaussian/       # Gaussian noise variants
│   ├── salt_pepper/    # Salt & pepper variants
│   └── ...            # Other noise types
├── analysis/           # Analysis results
├── plots/             # Visualization plots
└── metadata.json      # Project information
```

## Integration

### With GUI
All scripts are designed to work with the GUI:
- Same `NoiseGenerator` class used by GUI
- Compatible project structure
- Shared configuration files

### With External Tools
- TIFF format compatibility with ImageJ, QGIS, ENVI
- Metadata preservation for GIS applications
- Standard file naming conventions

## Dependencies

### Required
```bash
pip install numpy opencv-python tifffile
```

### Optional
```bash
pip install matplotlib seaborn scikit-image rasterio
```

### For Analysis
```bash
pip install pandas scipy statsmodels
```

## Performance

### Optimization Tips
- Use appropriate data types (uint16 for most multispectral data)
- Process images in chunks for large datasets
- Utilize multiprocessing for batch operations
- Monitor memory usage with large images

### Benchmarks
- **Single 5-band image (2048x1536):** ~2-5 seconds per noise type
- **Batch processing (100 images):** ~10-30 minutes depending on noise types
- **Memory usage:** ~2-4x image size during processing

## Troubleshooting

### Common Issues

**Import errors**
```bash
# Check dependencies
pip list | grep -E "(numpy|opencv|tifffile)"

# Reinstall if needed
pip install --upgrade numpy opencv-python tifffile
```

**Memory errors with large images**
- Reduce batch size
- Process images individually
- Use image tiling for very large images

**Slow processing**
- Use fewer noise levels for testing
- Disable unnecessary noise types
- Check available system memory

**Output format issues**
- Ensure input images are valid TIFF files
- Check bit depth compatibility
- Verify multispectral band count

## Development

### Adding New Noise Types
1. Implement noise function in `add_noise_to_images.py`
2. Add configuration to `noise_config.json`
3. Update analysis scripts if needed
4. Add tests and documentation

### Extending Analysis
1. Add new metrics to analysis scripts
2. Update visualization functions
3. Ensure compatibility with existing data
4. Document new features

### Testing
```bash
# Run with test images
python add_noise_to_images.py --input test_image.tif --output test/ --noise gaussian --levels 3

# Verify output
python analyze_noise_metrics.py --original test_image.tif --noisy test/
```

## API Reference

### NoiseGenerator Class
```python
from add_noise_to_images import NoiseGenerator

generator = NoiseGenerator()
noisy_image = generator.apply_noise(image, 'gaussian', level=5)
```

### ProjectManager Class
```python
from project_manager import ProjectManager

pm = ProjectManager('projects/')
project_path = pm.create_project('my_project')
```

## Contributing

- Follow PEP 8 style guidelines
- Add docstrings for all functions
- Include unit tests for new features
- Update configuration files as needed
- Maintain backward compatibility
