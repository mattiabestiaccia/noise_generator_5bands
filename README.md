# Multispectral Noise Generator

A comprehensive toolkit for generating realistic noise on multispectral images, designed for testing and validating denoising algorithms on 5-band imagery from MicaSense RedEdge cameras.

## 🎯 Overview

This project provides both command-line tools and a graphical user interface for generating various types of noise on multispectral images. It supports 8 different noise types with configurable intensity levels, comprehensive analysis tools, and organized project management.

## ✨ Key Features

- **🎲 8 Noise Types**: Gaussian, Salt&Pepper, Poisson, Speckle, Motion Blur, Atmospheric, Compression, ISO
- **🖥️ Dual Interface**: Both GUI and command-line tools
- **📊 Advanced Visualization**: RGB, NDVI, Red Edge Enhanced, and single-band views
- **📁 Project Management**: Organized workflow with automatic structure creation
- **📈 Analysis Tools**: PSNR, SSIM, MSE calculations and progressive plots
- **🔧 Configurable**: JSON-based configuration for all noise parameters
- **💾 Metadata Preservation**: Maintains original image metadata when possible

## 🚀 Quick Start

### GUI Application (Recommended)
```bash
# Launch the graphical interface
python run_gui.py
```

### Command Line
```bash
# Generate noise on a single image
python scripts/add_noise_to_images.py \
    --input image.tif \
    --output noisy/ \
    --noise gaussian \
    --levels 5
```

## 📦 Installation

### Basic Requirements
```bash
pip install numpy opencv-python tifffile
```

### Full GUI Support
```bash
pip install matplotlib tkinter Pillow
```

### Analysis Tools
```bash
pip install pandas seaborn scikit-image
```

### All Dependencies
```bash
pip install -r requirements.txt
```

## 🏗️ Project Structure

```
noise_generator/
├── gui/                    # Graphical user interface
│   ├── main_window.py     # Complete GUI application
│   ├── image_viewer.py    # Multispectral image viewer
│   ├── file_selector.py   # File/folder selection
│   └── ...               # Other GUI components
├── scripts/               # Command-line tools
│   ├── add_noise_to_images.py      # Main noise generator
│   ├── analyze_noise_metrics.py    # Analysis tools
│   ├── create_progressive_plots.py # Visualization
│   └── project_manager.py          # Project management
├── configs/               # Configuration files
│   └── noise_config.json # Noise parameters
├── projects/              # Generated projects
└── utils/                 # Utility functions
```

## 🎲 Noise Types

| Type | Description | Parameter | Range | Use Case |
|------|-------------|-----------|-------|----------|
| **Gaussian** | Thermal sensor noise | σ (std dev) | 5-50 | Basic sensor noise |
| **Salt & Pepper** | Dead/hot pixels | Probability | 0.001-0.01 | Sensor defects |
| **Poisson** | Shot noise | Scale factor | 0.1-1.0 | Signal-dependent noise |
| **Speckle** | Multiplicative noise | Variance | 0.05-0.5 | Optical interference |
| **Motion Blur** | Movement blur | Kernel size | 3-21 px | Platform movement |
| **Atmospheric** | Haze effects | Intensity | 0.1-1.0 | Environmental conditions |
| **Compression** | JPEG artifacts | Quality | 50-95 | Data transmission |
| **ISO Noise** | High ISO noise | Level | 1-10 | Low-light conditions |

## 🖼️ Visualization Modes

The GUI provides advanced visualization capabilities:

- **Single Bands**: Navigate through 5 spectral bands (Blue, Green, Red, Red Edge, Near-IR)
- **RGB Natural**: True color composition (3,2,1)
- **Red Edge Enhanced**: Vegetation stress analysis (4,3,2)
- **NDVI-like**: Vegetation health assessment (5,4,3)
- **NDVI**: Normalized Difference Vegetation Index with colorbar

## 📁 Project Workflow

### Automatic Project Creation
```bash
# Projects are created automatically with organized structure
project_name/
├── input/              # Original images
├── noisy_images/       # Generated noisy images
│   ├── gaussian/       # Organized by noise type
│   ├── salt_pepper/
│   └── ...
├── visualizations/     # Saved GUI visualizations
├── analysis/           # Analysis results
└── project_metadata.json
```

### GUI Workflow
1. **Launch GUI**: `python run_gui.py`
2. **Select Images**: Single files, multiple files, or folders
3. **Auto Project Creation**: Project created automatically
4. **Visualize**: Double-click to load images with multiple view modes
5. **Generate Noise**: Select types and levels, click generate
6. **Save Results**: Visualizations and noisy images saved automatically

### Command-Line Workflow
```bash
# Create project
python scripts/project_manager.py --create experiment_1 --input images/

# Generate noise
python scripts/add_noise_to_images.py \
    --project experiment_1 \
    --noise gaussian poisson speckle \
    --levels 10

# Analyze results
python scripts/analyze_noise_metrics.py --project experiment_1

# Create plots
python scripts/create_progressive_plots.py --project experiment_1
```

## 🔧 Configuration

### Noise Parameters
Edit `configs/noise_config.json`:
```json
{
  "noise_types": {
    "gaussian": {
      "description": "Thermal sensor noise simulation",
      "parameter_name": "sigma",
      "parameter_range": [5, 50]
    }
  },
  "generation_parameters": {
    "default_levels": 10
  }
}
```

### Presets
- **Realistic Drone**: Gaussian + ISO + Atmospheric (recommended for testing)
- **Stress Testing**: Salt&Pepper + Speckle + Motion Blur
- **Laboratory**: Gaussian + Poisson (controlled conditions)

## 📊 Analysis Tools

### Noise Metrics
```bash
python scripts/analyze_noise_metrics.py --project project_name
```
Calculates:
- Peak Signal-to-Noise Ratio (PSNR)
- Structural Similarity Index (SSIM)
- Mean Squared Error (MSE)
- Per-band statistics

### Progressive Visualization
```bash
python scripts/create_progressive_plots.py --project project_name
```
Generates:
- Progressive noise level plots
- Quality degradation curves
- Comparative analysis charts

## 🔍 Advanced Usage

### Custom Noise Generation
```python
from scripts.add_noise_to_images import NoiseGenerator

generator = NoiseGenerator()
noisy_image = generator.apply_noise(image, 'gaussian', level=5)
```

### Batch Analysis
```python
from scripts.analyze_noise_metrics import analyze_project

results = analyze_project('project_name')
print(results.summary())
```

### GUI Integration
```python
from gui.main_window import launch_gui
launch_gui()
```

## 🎯 Use Cases

### Algorithm Development
- Test denoising algorithms with realistic noise
- Validate robustness across different noise types
- Compare performance metrics systematically

### Research Applications
- Generate datasets for machine learning
- Study noise impact on spectral analysis
- Develop noise-aware processing pipelines

### Educational Purposes
- Demonstrate noise effects on multispectral data
- Teach image processing concepts
- Provide hands-on experience with real data

## 📈 Performance

| Operation | Time | Memory |
|-----------|------|--------|
| Single image (2048×1536×5) | 2-5 sec/noise | 2-4× image size |
| Batch (100 images) | 10-30 min | Scales linearly |
| GUI visualization | Real-time | Minimal overhead |

## 🔧 Troubleshooting

### Common Issues

**GUI won't start**
```bash
# Check tkinter
python -c "import tkinter"

# Try basic version
python gui/basic_main.py
```

**Missing dependencies**
```bash
# Install core dependencies
pip install numpy opencv-python tifffile

# For full functionality
pip install matplotlib Pillow
```

**Memory errors**
- Reduce batch size
- Process images individually
- Check available system memory

## 📚 Documentation

Each module has detailed documentation:
- [`gui/README.md`](gui/README.md) - GUI components and usage
- [`scripts/README.md`](scripts/README.md) - Command-line tools
- [`configs/README.md`](configs/README.md) - Configuration options
- [`projects/README.md`](projects/README.md) - Project structure
- [`utils/README.md`](utils/README.md) - Utility functions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
git clone https://github.com/yourusername/noise_generator_5bands.git
cd noise_generator_5bands
pip install -r requirements.txt
python -m pytest tests/  # Run tests
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📖 Citation

If you use this tool in your research, please cite:

```bibtex
@software{multispectral_noise_generator,
  title={Multispectral Noise Generator for 5-Band Images},
  author={HPL Research Team},
  year={2023},
  url={https://github.com/mattiabestiaccia/noise_generator_5bands},
  note={Tool for generating realistic noise on multispectral imagery}
}
```

## 🙏 Acknowledgments

- MicaSense for RedEdge camera specifications
- OpenCV community for image processing tools
- Scientific Python ecosystem for analysis capabilities

---

**🚀 Ready to start?** Try `python run_gui.py` for the full experience or `python gui/basic_main.py` for a quick test!
