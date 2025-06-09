# GUI Module

Graphical User Interface for the Multispectral Noise Generator.

## Overview

This module provides a complete tkinter-based GUI for generating noisy multispectral images. The interface reuses visualization components from the image registration GUI and integrates noise generation capabilities.

## Components

### Core GUI Files

- **`main_window.py`** - Complete main window with full functionality
- **`image_viewer.py`** - Advanced image viewer with multispectral visualization modes
- **`file_selector.py`** - File and folder selection widget
- **`project_manager.py`** - Project management for GUI integration
- **`noise_controls.py`** - Noise generation controls and configuration

### Alternative Versions

- **`simple_main.py`** - Simplified version without matplotlib dependency
- **`basic_main.py`** - Basic version using only standard tkinter
- **`simple_viewer.py`** - Simplified image viewer using PIL

## Features

### 🖼️ Multispectral Visualization
- **Single Bands**: Navigate through 5 spectral bands with ◀ ▶ controls
- **RGB Natural**: Composition (3,2,1) for natural color visualization
- **Red Edge Enhanced**: Composition (4,3,2) for vegetation stress analysis
- **NDVI-like**: Composition (5,4,3) for vegetation health assessment
- **NDVI**: Vegetation index calculation with colorbar

### 📁 File Management
- **Single File**: Select individual TIFF images
- **Multiple Files**: Batch selection of multiple images
- **Folder Selection**: Process entire directories
- **Preview**: List of selected files with double-click loading

### 🎲 Noise Generation
- **8 Noise Types**: Gaussian, Salt&Pepper, Poisson, Speckle, Motion Blur, Atmospheric, Compression, ISO
- **Configurable Levels**: 1-20 intensity levels
- **Batch Processing**: Background threading for non-blocking operation
- **Progress Monitoring**: Real-time progress bar and status updates

### 🏗️ Project Management
- **Automatic Creation**: Projects created on first file selection
- **Organized Structure**: Separate folders for input, output, visualizations
- **Metadata Tracking**: Processing history and parameters
- **Empty Project Cleanup**: Automatic removal of unused projects

## Usage

### Quick Start
```bash
# Test basic functionality (always works)
python basic_main.py

# Full GUI (requires dependencies)
python main_window.py
```

### Dependencies

#### Required (Basic Version)
- Python 3.6+
- tkinter (standard library)
- tifffile

#### Optional (Full Version)
- matplotlib (for advanced visualizations)
- opencv-python (for noise generation)
- Pillow (for image display)
- numpy

### Installation
```bash
# Basic dependencies
pip install tifffile

# Full functionality
pip install matplotlib opencv-python Pillow numpy
```

## Architecture

### Module Structure
```
gui/
├── __init__.py           # Module initialization
├── main_window.py        # Main application window
├── image_viewer.py       # Multispectral image viewer
├── file_selector.py      # File/folder selection
├── project_manager.py    # Project management
├── noise_controls.py     # Noise generation controls
├── simple_main.py        # Simplified version
├── basic_main.py         # Basic version
└── simple_viewer.py      # Simplified viewer
```

### Design Patterns
- **Component-based**: Each widget is a separate, reusable component
- **Callback-driven**: Event handling through callback functions
- **Graceful Degradation**: Fallback versions for limited environments
- **Threading**: Non-blocking operations for long-running tasks

## Integration

### With Existing Scripts
The GUI integrates seamlessly with existing command-line scripts:
- Uses the same `NoiseGenerator` class from `scripts/add_noise_to_images.py`
- Compatible with `ProjectManager` from `scripts/project_manager.py`
- Maintains the same project structure as command-line tools

### Project Structure
Generated projects follow the standard structure:
```
project_name/
├── input/              # Original images
├── noisy_images/       # Generated noisy images
├── visualizations/     # Saved visualizations
├── analysis/           # Analysis results
├── config/             # Configuration files
└── reports/            # Processing reports
```

## Customization

### Adding New Noise Types
1. Add noise type to `configs/noise_config.json`
2. Implement noise function in `scripts/add_noise_to_images.py`
3. GUI will automatically detect and include new types

### Adding Visualization Modes
1. Add new mode to `image_viewer.py`
2. Update mode selection dropdown
3. Implement visualization method

### Extending File Support
1. Modify file filters in `file_selector.py`
2. Update image loading logic in `image_viewer.py`
3. Ensure compatibility with noise generation pipeline

## Troubleshooting

### Common Issues

**GUI won't start**
- Check tkinter installation: `python -c "import tkinter"`
- Try basic version: `python basic_main.py`

**Image loading fails**
- Install tifffile: `pip install tifffile`
- For compressed TIFFs: `pip install imagecodecs`

**Visualization errors**
- Install matplotlib: `pip install matplotlib`
- Use simplified version: `python simple_main.py`

**Noise generation fails**
- Install opencv: `pip install opencv-python`
- Check noise configuration in `configs/noise_config.json`

### Performance Tips
- Use "Realistic Drone" preset for faster processing
- Reduce number of levels for initial testing
- Process single files before batch operations
- Close other applications for memory-intensive operations

## Development

### Adding New Components
1. Create new widget class following existing patterns
2. Implement callback-based event handling
3. Add to main window layout
4. Update `__init__.py` exports

### Testing
- Use `basic_main.py` for component testing
- Test with various image formats and sizes
- Verify project creation and cleanup
- Test error handling with invalid inputs

### Contributing
- Follow existing code style and patterns
- Add docstrings for all public methods
- Include error handling and user feedback
- Test with both basic and full dependency sets
