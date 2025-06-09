# Utilities Module

Utility functions and helper modules for the Multispectral Noise Generator.

## Overview

This directory is intended for utility functions, helper classes, and common functionality that can be shared across different components of the noise generator system.

## Intended Structure

### Image Processing Utilities
**`image_utils.py`** (planned)
- Image loading and saving helpers
- Format conversion utilities
- Metadata preservation functions
- Image validation and preprocessing

### Mathematical Utilities
**`math_utils.py`** (planned)
- Statistical analysis functions
- Noise calculation helpers
- Signal processing utilities
- Metric computation functions

### File System Utilities
**`file_utils.py`** (planned)
- Directory management
- File organization helpers
- Batch processing utilities
- Path manipulation functions

### Validation Utilities
**`validation_utils.py`** (planned)
- Input validation functions
- Configuration validation
- Data integrity checks
- Error handling helpers

## Planned Functionality

### Image Processing
```python
# Example planned functions
def load_multiband_image(filepath):
    """Load multispectral TIFF image with error handling."""
    pass

def save_with_metadata(image, filepath, metadata):
    """Save image preserving original metadata."""
    pass

def validate_image_format(image):
    """Validate image format and dimensions."""
    pass

def normalize_image_data(image, method='percentile'):
    """Normalize image data for visualization."""
    pass
```

### Mathematical Operations
```python
# Example planned functions
def calculate_psnr(original, noisy):
    """Calculate Peak Signal-to-Noise Ratio."""
    pass

def calculate_ssim(original, noisy):
    """Calculate Structural Similarity Index."""
    pass

def compute_noise_statistics(image):
    """Compute comprehensive noise statistics."""
    pass

def apply_statistical_filter(image, filter_type):
    """Apply statistical filtering operations."""
    pass
```

### File Management
```python
# Example planned functions
def organize_output_files(source_dir, target_dir, pattern):
    """Organize files according to naming pattern."""
    pass

def batch_rename_files(directory, pattern, replacement):
    """Batch rename files with pattern matching."""
    pass

def create_project_structure(project_path):
    """Create standard project directory structure."""
    pass

def cleanup_temporary_files(directory):
    """Clean up temporary processing files."""
    pass
```

### Validation and Error Handling
```python
# Example planned functions
def validate_noise_parameters(noise_type, parameters):
    """Validate noise generation parameters."""
    pass

def check_system_requirements():
    """Check system requirements and dependencies."""
    pass

def validate_project_structure(project_path):
    """Validate project directory structure."""
    pass

def handle_processing_errors(error, context):
    """Standardized error handling and logging."""
    pass
```

## Current Status

This directory is currently empty but reserved for future utility functions. As the project grows, common functionality should be extracted into utility modules to:

- Reduce code duplication
- Improve maintainability
- Provide consistent interfaces
- Enable easier testing

## Development Guidelines

### When to Add Utilities

Add functions to utils when:
- The same functionality is used in multiple modules
- Complex operations need standardized implementations
- Error handling patterns are repeated
- Configuration or validation logic is shared

### Organization Principles

- **Single Responsibility**: Each utility module should have a clear, focused purpose
- **No Dependencies**: Utilities should minimize external dependencies
- **Documentation**: All utility functions should be well-documented
- **Testing**: Utility functions should have comprehensive unit tests

### Naming Conventions

- Use descriptive function names
- Follow Python naming conventions (snake_case)
- Group related functions in appropriately named modules
- Use consistent parameter naming across functions

## Integration

### With Existing Code
When adding utilities, update existing code to use them:

```python
# Before
def some_function():
    # Inline image loading logic
    with open(filepath, 'rb') as f:
        # Complex loading code
        pass

# After
from utils.image_utils import load_multiband_image

def some_function():
    image = load_multiband_image(filepath)
```

### With GUI Components
Utilities should be designed to work seamlessly with GUI components:

```python
# GUI callback using utility
def on_image_load(self, filepath):
    try:
        image = load_multiband_image(filepath)
        if validate_image_format(image):
            self.display_image(image)
    except Exception as e:
        handle_processing_errors(e, 'image_loading')
```

### With Command-Line Scripts
Utilities should also support command-line usage:

```python
# Script using utility
from utils.file_utils import organize_output_files

if __name__ == "__main__":
    organize_output_files(args.input, args.output, args.pattern)
```

## Future Enhancements

### Planned Modules

1. **Performance Utilities**
   - Memory usage monitoring
   - Processing time measurement
   - Resource optimization helpers

2. **Logging Utilities**
   - Standardized logging configuration
   - Progress tracking utilities
   - Debug information helpers

3. **Configuration Utilities**
   - Configuration file management
   - Environment-specific settings
   - Parameter validation helpers

4. **Testing Utilities**
   - Test data generation
   - Mock object creation
   - Assertion helpers

### Integration Opportunities

- **Plugin System**: Utilities for loading external noise generators
- **Export Functions**: Utilities for exporting to different formats
- **Batch Processing**: Advanced batch operation utilities
- **Cloud Integration**: Utilities for cloud storage and processing

## Contributing

When contributing utility functions:

1. **Check for Existing Solutions**: Ensure the functionality doesn't already exist
2. **Design for Reusability**: Make functions generic and configurable
3. **Add Documentation**: Include docstrings and usage examples
4. **Write Tests**: Add unit tests for all new utilities
5. **Update Dependencies**: Document any new dependencies required

### Example Contribution

```python
def calculate_band_statistics(image, band_index):
    """
    Calculate comprehensive statistics for a specific band.
    
    Args:
        image (numpy.ndarray): Multispectral image array
        band_index (int): Index of the band to analyze
        
    Returns:
        dict: Dictionary containing mean, std, min, max, percentiles
        
    Raises:
        ValueError: If band_index is out of range
        TypeError: If image is not a numpy array
    """
    # Implementation here
    pass
```

## Migration Path

As utility functions are developed:

1. **Identify Common Patterns**: Look for repeated code across modules
2. **Extract Functions**: Move common code to appropriate utility modules
3. **Update Imports**: Update existing modules to use new utilities
4. **Test Integration**: Ensure all functionality still works correctly
5. **Document Changes**: Update documentation and examples

This approach ensures the codebase remains clean, maintainable, and follows DRY (Don't Repeat Yourself) principles.
