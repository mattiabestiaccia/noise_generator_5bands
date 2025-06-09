# 🎯 Noise Generator for UAV Drone Images

**Independent module** specialized in **generating noisy images** from UAV drone imagery for creating training datasets for denoising algorithms.

## 📁 Project Structure

```
noise_generator/
├── 📁 output/                    # Generated noisy images
│   ├── 📁 gaussian/             # Gaussian noise images
│   ├── 📁 salt_pepper/          # Salt & pepper noise images
│   ├── 📁 poisson/              # Poisson noise images
│   ├── 📁 speckle/              # Speckle noise images
│   ├── 📁 motion_blur/          # Motion blur images
│   ├── 📁 atmospheric/          # Atmospheric effects images
│   ├── 📁 compression/          # Compression artifacts images
│   ├── 📁 iso_noise/            # ISO noise images
│   └── 📄 noise_processing_report.json
├── 📁 scripts/                  # Core processing scripts
│   ├── 🎯 add_noise_to_images.py       # Main noise generator
│   ├── 📊 analyze_noisy_images.py      # Quality analysis
│   ├── 📊 analyze_noise_metrics.py     # Metrics analysis
│   ├── 📊 analyze_multiband_corrected.py # Multiband analysis
│   ├── 📈 create_progressive_plots.py  # Visualization plots
│   ├── 📦 dataset_utils.py             # Dataset management
│   └── 🗂️ project_manager.py           # Project organization
├── 📁 projects/                 # Project-based organization
│   └── 📁 test_proj/           # Example project
├── 📁 configs/                  # Configuration files
│   └── ⚙️ noise_config.json     # Complete noise configuration
├── 📁 docs/                     # Documentation
│   └── 📖 README_NOISE_GENERATION.md
├── 📁 utils/                    # Utility modules
└── 📄 requirements.txt          # Python dependencies
```

## 🚀 Quick Start

### 1. Complete Generation
```bash
# Generate all noisy images (8 types × 10 levels)
python scripts/add_noise_to_images.py

# Analyze image quality
python scripts/analyze_noisy_images.py

# Create visualization plots
python scripts/create_progressive_plots.py
```

### 2. Custom Generation
```bash
# Specific noise types only
python scripts/add_noise_to_images.py -i input_folder -o output_folder \
  --noise-types gaussian salt_pepper --levels 5

# Targeted analysis
python scripts/analyze_noisy_images.py -n output_folder -r analysis/results
```

### 3. Dataset Management
```bash
# Create training subset
python scripts/dataset_utils.py subset -o datasets/training_set \
  --noise-types gaussian iso_noise --levels 1 3 5 7 10

# Create train/val/test splits
python scripts/dataset_utils.py split -o datasets/splits

# Create paired dataset for denoising
python scripts/dataset_utils.py paired -o datasets/denoising_pairs
```

## 🎯 Available Noise Types

| Type | Description | Parameters | Levels |
|------|-------------|------------|--------|
| **gaussian** | Sensor thermal noise | σ: 5-50 | 1-10 |
| **salt_pepper** | Defective pixels | prob: 0.001-0.01 | 1-10 |
| **poisson** | Shot noise | scale: 0.1-1.0 | 1-10 |
| **speckle** | Multiplicative noise | var: 0.05-0.5 | 1-10 |
| **motion_blur** | Movement blur | kernel: 3-21 | 1-10 |
| **atmospheric** | Atmospheric effects | intensity: 0.1-1.0 | 1-10 |
| **compression** | JPEG artifacts | quality: 95-50 | 1-10 |
| **iso_noise** | High ISO noise | luma+chroma | 1-10 |

## 📊 Dataset Statistics

- **Original images**: Variable (project-based)
- **Generated images**: 8 types × 10 levels × N originals
- **Supported formats**: TIFF (multiband), JPG, JPEG, PNG
- **Resolution**: Preserved from original
- **Metadata**: Preserved for geospatial TIFF files

## 📈 Quality Metrics

The system automatically calculates:
- **PSNR** (Peak Signal-to-Noise Ratio) in dB
- **SSIM** (Structural Similarity Index) 0-1
- **MSE** (Mean Squared Error)
- **SNR** (Signal-to-Noise Ratio) in dB

### Typical Results (Level 5)

| Type | PSNR (dB) | SSIM | Quality |
|------|-----------|------|---------|
| Compression | 38.66 | 0.9989 | Excellent |
| Motion Blur | 29.13 | 0.9758 | Good |
| Gaussian | 23.29 | 0.9751 | Moderate |
| ISO Noise | 15.64 | 0.8712 | Low |

## 🛠️ Core Scripts and Features

### 🎯 Main Noise Generator (`add_noise_to_images.py`)
Generates noisy images with progressive intensity levels.
```bash
# Basic usage
python scripts/add_noise_to_images.py

# Project-based processing
python scripts/add_noise_to_images.py --project my_project -l 5

# Custom input/output
python scripts/add_noise_to_images.py -i input_folder -o output_folder \
  --noise-types gaussian salt_pepper --levels 3
```

### 📊 Quality Analysis (`analyze_noisy_images.py`)
Calculates PSNR, SSIM, MSE, and SNR metrics for generated images.
```bash
# Analyze all generated images
python scripts/analyze_noisy_images.py

# Project-specific analysis
python scripts/analyze_noisy_images.py --project my_project

# Custom analysis
python scripts/analyze_noisy_images.py -o original_folder -n noisy_folder -r results
```

### 📈 Metrics Analysis (`analyze_noise_metrics.py`)
Advanced metrics analysis with statistical comparisons and trend analysis.
```bash
# Comprehensive metrics analysis
python scripts/analyze_noise_metrics.py --project my_project

# Compare multiple noise types
python scripts/analyze_noise_metrics.py --compare gaussian poisson iso_noise
```

### 🔬 Multiband Analysis (`analyze_multiband_corrected.py`)
Specialized analysis for multispectral/multiband TIFF images.
```bash
# Analyze multiband images
python scripts/analyze_multiband_corrected.py --project my_project

# Band-specific analysis
python scripts/analyze_multiband_corrected.py -i input_folder --bands 1 2 3 4 5
```

### 📈 Progressive Plots (`create_progressive_plots.py`)
Creates visualization plots showing noise progression and quality metrics.
```bash
# Generate all visualization plots
python scripts/create_progressive_plots.py --project my_project

# Specific plot types
python scripts/create_progressive_plots.py --plots comparison progression metrics
```

### 🗂️ Project Manager (`project_manager.py`)
Manages project creation, organization, and maintenance.
```bash
# Create new project
python scripts/project_manager.py create my_project -d "Description"

# List all projects
python scripts/project_manager.py list

# Get project information
python scripts/project_manager.py info my_project

# Clean project (remove temporary files)
python scripts/project_manager.py clean my_project --what temp

# Clean all generated data
python scripts/project_manager.py clean my_project --what all
```

### 📦 Dataset Utilities (`dataset_utils.py`)
Manages dataset creation, splitting, and organization.
```bash
# Create training/validation/test splits
python scripts/dataset_utils.py split -o datasets/splits --project my_project

# Create subset with specific criteria
python scripts/dataset_utils.py subset -o datasets/subset \
  --noise-types gaussian iso_noise --levels 1 3 5

# Create paired dataset for supervised learning
python scripts/dataset_utils.py paired -o datasets/paired --project my_project
```

## 🎮 Usage Examples

### Research and Development
```bash
# Create research project
python scripts/project_manager.py create research_proj -d "Algorithm testing"

# Generate specific noise types
python scripts/add_noise_to_images.py --project research_proj \
  --noise-types gaussian poisson iso_noise -l 5

# Comprehensive analysis
python scripts/analyze_noise_metrics.py --project research_proj
python scripts/create_progressive_plots.py --project research_proj
```

### Machine Learning Training
```bash
# Balanced dataset for training
python scripts/dataset_utils.py split -o datasets/ml_training \
  --train-ratio 0.8 --val-ratio 0.1 --test-ratio 0.1

# Paired dataset for supervised learning
python scripts/dataset_utils.py paired -o datasets/supervised
```

### Benchmarking and Evaluation
```bash
# Subset with specific levels
python scripts/dataset_utils.py subset -o datasets/benchmark \
  --levels 3 5 7 --noise-types gaussian salt_pepper motion_blur
```

## ⚙️ Configuration

The `configs/noise_config.json` file contains:
- Parameters for each noise type
- Quality thresholds
- Usage recommendations
- Default configurations

## 📚 Complete Documentation

See `docs/README_NOISE_GENERATION.md` for:
- Detailed description of each noise type
- Technical parameters and calibration
- Advanced usage examples
- Best practices for dataset creation

## 🔧 Requirements

```bash
pip install -r requirements.txt
```

Main dependencies:
- **opencv-python** (image processing)
- **numpy** (numerical computations)
- **matplotlib** (plotting)
- **scikit-image** (quality metrics)
- **rasterio** (multiband TIFF support)
- **tqdm** (progress bars)
- **imagecodecs** (TIFF compression support)

## 📝 Output Files

### Automatic Reports
- `output/noise_processing_report.json`
- `output/noise_processing_report.txt`
- `projects/*/analysis/metrics_report.json`

### Visualizations
- `projects/*/plots/noise_comparison_*.png`
- `projects/*/plots/intensity_progression_*.png`
- `projects/*/plots/metrics_*_progression.png`

## 🧪 Testing and Verification

### Quick Test
```bash
# Verify module functionality
python scripts/add_noise_to_images.py --help
```

### Complete Test on Multiband TIFF Images
```bash
# Generate noise on registered images (example)
python scripts/add_noise_to_images.py \
  -i ../image_registration/projects/test_proj/registered \
  -o output -l 3

# Analyze quality
python scripts/analyze_noisy_images.py \
  -o ../image_registration/projects/test_proj/registered \
  -n output -r analysis/results
```

## 🎯 Recommendations

### By Application Type
- **Light denoising**: Levels 1-3, gaussian/compression types
- **Moderate denoising**: Levels 4-6, all types
- **Heavy denoising**: Levels 7-10, poisson/iso_noise types
- **Robustness testing**: salt_pepper, speckle
- **Realistic simulation**: gaussian, iso_noise, atmospheric

### By Dataset Size
- **Prototyping**: 1-2 types, 3-5 levels
- **Development**: 3-4 types, 5-7 levels
- **Production**: All types, all levels
- **Benchmarking**: Balanced subset with known metrics

### Format Support
- ✅ **Multiband TIFF** (5 spectral bands) - Primary format
- ✅ **JPEG/PNG** (RGB standard) - Compatibility
- ✅ **Metadata preservation** for geospatial TIFF files

## 🗂️ Project Management System

The noise generator features a comprehensive project management system that organizes all processing activities:

### Key Features
- **Structured Organization**: Each project has standardized folder structure
- **Metadata Tracking**: Automatic tracking of processing history and statistics
- **Batch Processing**: Support for processing multiple projects
- **Cleanup Tools**: Automated cleanup of temporary and generated files
- **Progress Monitoring**: Track processing status and file statistics

### Project Structure
```
projects/
└── your_project/
    ├── input/              # Original images to process
    ├── noisy_images/       # Generated noisy images
    │   ├── gaussian/       # Organized by noise type
    │   ├── salt_pepper/
    │   ├── poisson/
    │   ├── speckle/
    │   ├── motion_blur/
    │   ├── atmospheric/
    │   ├── compression/
    │   └── iso_noise/
    ├── analysis/           # Quality analysis results
    ├── config/             # Project-specific configurations
    ├── reports/            # Processing reports and logs
    ├── project_metadata.json  # Project metadata and history
    └── README.md           # Project documentation
```

### Project Lifecycle
1. **Creation**: `python scripts/project_manager.py create project_name`
2. **Processing**: Add images to `input/` folder
3. **Generation**: `python scripts/add_noise_to_images.py --project project_name`
4. **Analysis**: `python scripts/analyze_noise_metrics.py --project project_name`
5. **Visualization**: `python scripts/create_progressive_plots.py --project project_name`
6. **Maintenance**: `python scripts/project_manager.py clean project_name`

### Metadata Tracking
Each project automatically tracks:
- Creation and modification dates
- Processing history with timestamps
- File statistics and sizes
- Configuration parameters used
- Quality metrics results

---

**Module**: Noise Generator v2.0
**Compatibility**: Python 3.8+
**License**: HPL/WST Project
