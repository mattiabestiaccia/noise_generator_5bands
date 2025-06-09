# Configuration Files

Configuration files for the Multispectral Noise Generator.

## Overview

This directory contains configuration files that define noise parameters, processing options, and system settings for both command-line scripts and GUI applications.

## Configuration Files

### `noise_config.json`
Main configuration file defining all noise types and their parameters.

#### Structure
```json
{
  "noise_types": {
    "noise_name": {
      "description": "Human-readable description",
      "parameter_name": "Parameter identifier",
      "parameter_range": [min_value, max_value]
    }
  },
  "generation_parameters": {
    "default_levels": 10,
    "output_format": "tiff",
    "preserve_metadata": true
  }
}
```

#### Noise Type Definitions

**Gaussian Noise**
```json
"gaussian": {
  "description": "Thermal sensor noise simulation",
  "parameter_name": "sigma",
  "parameter_range": [5, 50]
}
```

**Salt & Pepper Noise**
```json
"salt_pepper": {
  "description": "Dead/hot pixel simulation",
  "parameter_name": "probability",
  "parameter_range": [0.001, 0.01]
}
```

**Poisson Noise**
```json
"poisson": {
  "description": "Shot noise simulation",
  "parameter_name": "scale",
  "parameter_range": [0.1, 1.0]
}
```

**Speckle Noise**
```json
"speckle": {
  "description": "Multiplicative noise simulation",
  "parameter_name": "variance",
  "parameter_range": [0.05, 0.5]
}
```

**Motion Blur**
```json
"motion_blur": {
  "description": "Movement-induced blur",
  "parameter_name": "kernel_size",
  "parameter_range": [3, 21]
}
```

**Atmospheric Effects**
```json
"atmospheric": {
  "description": "Haze and vapor simulation",
  "parameter_name": "haze_intensity",
  "parameter_range": [0.1, 1.0]
}
```

**Compression Artifacts**
```json
"compression": {
  "description": "JPEG compression artifacts",
  "parameter_name": "quality",
  "parameter_range": [50, 95]
}
```

**ISO Noise**
```json
"iso_noise": {
  "description": "High ISO sensitivity noise",
  "parameter_name": "iso_level",
  "parameter_range": [1, 10]
}
```

## Usage

### Loading Configuration
```python
import json

# Load noise configuration
with open('configs/noise_config.json', 'r') as f:
    config = json.load(f)

# Access noise types
noise_types = config['noise_types']
default_levels = config['generation_parameters']['default_levels']
```

### Modifying Configuration
```python
# Add new noise type
config['noise_types']['new_noise'] = {
    "description": "New noise type description",
    "parameter_name": "intensity",
    "parameter_range": [0.1, 2.0]
}

# Save configuration
with open('configs/noise_config.json', 'w') as f:
    json.dump(config, f, indent=2)
```

## Parameter Guidelines

### Parameter Ranges
- **Conservative:** Use lower end of ranges for realistic simulation
- **Aggressive:** Use higher end for stress testing algorithms
- **Research:** Use full range for comprehensive analysis

### Recommended Presets

**Realistic Drone Conditions**
```json
{
  "gaussian": {"sigma": [5, 15]},
  "atmospheric": {"haze_intensity": [0.1, 0.3]},
  "iso_noise": {"iso_level": [1, 3]}
}
```

**Stress Testing**
```json
{
  "salt_pepper": {"probability": [0.005, 0.01]},
  "speckle": {"variance": [0.2, 0.5]},
  "motion_blur": {"kernel_size": [11, 21]}
}
```

**Laboratory Conditions**
```json
{
  "gaussian": {"sigma": [5, 10]},
  "poisson": {"scale": [0.1, 0.3]}
}
```

## Customization

### Adding New Noise Types

1. **Define in Configuration**
```json
"custom_noise": {
  "description": "Custom noise description",
  "parameter_name": "custom_param",
  "parameter_range": [min_val, max_val]
}
```

2. **Implement in Code**
```python
# In add_noise_to_images.py
def apply_custom_noise(self, image, level):
    # Implementation here
    return noisy_image
```

3. **Update GUI**
The GUI automatically detects new noise types from configuration.

### Modifying Existing Types

**Change Parameter Range**
```json
"gaussian": {
  "description": "Thermal sensor noise simulation",
  "parameter_name": "sigma",
  "parameter_range": [1, 100]  # Extended range
}
```

**Add Additional Parameters**
```json
"gaussian": {
  "description": "Thermal sensor noise simulation",
  "parameter_name": "sigma",
  "parameter_range": [5, 50],
  "additional_params": {
    "mean": 0,
    "clip_values": true
  }
}
```

## Validation

### Configuration Validation
```python
def validate_config(config):
    required_keys = ['noise_types', 'generation_parameters']
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required key: {key}")
    
    for noise_name, noise_config in config['noise_types'].items():
        required_noise_keys = ['description', 'parameter_name', 'parameter_range']
        for key in required_noise_keys:
            if key not in noise_config:
                raise ValueError(f"Missing key '{key}' in noise type '{noise_name}'")
```

### Parameter Range Validation
```python
def validate_parameter_range(param_range):
    if not isinstance(param_range, list) or len(param_range) != 2:
        raise ValueError("Parameter range must be a list of two values")
    
    if param_range[0] >= param_range[1]:
        raise ValueError("Parameter range minimum must be less than maximum")
```

## Environment-Specific Configurations

### Development
```json
{
  "generation_parameters": {
    "default_levels": 3,
    "debug_mode": true,
    "verbose_logging": true
  }
}
```

### Production
```json
{
  "generation_parameters": {
    "default_levels": 10,
    "debug_mode": false,
    "optimize_memory": true
  }
}
```

### Research
```json
{
  "generation_parameters": {
    "default_levels": 20,
    "high_precision": true,
    "save_intermediate": true
  }
}
```

## Best Practices

### Configuration Management
- Keep backup copies of working configurations
- Use version control for configuration changes
- Document custom modifications
- Test configurations before deployment

### Parameter Selection
- Start with conservative values
- Gradually increase intensity for testing
- Consider real-world conditions
- Validate results with domain experts

### Performance Considerations
- Lower parameter ranges for faster processing
- Higher precision settings increase computation time
- Memory usage scales with parameter complexity

## Troubleshooting

### Common Issues

**Configuration not loading**
- Check JSON syntax validity
- Verify file permissions
- Ensure proper encoding (UTF-8)

**Invalid parameter ranges**
- Verify numeric values
- Check min < max constraint
- Ensure positive values where required

**Missing noise types**
- Check configuration completeness
- Verify all required keys present
- Update code implementation if needed

### Debugging
```python
import json

# Validate JSON syntax
try:
    with open('configs/noise_config.json', 'r') as f:
        config = json.load(f)
    print("Configuration loaded successfully")
except json.JSONDecodeError as e:
    print(f"JSON syntax error: {e}")
```

## Migration

### Updating Configuration Format
When updating configuration format, provide migration scripts:

```python
def migrate_config_v1_to_v2(old_config):
    new_config = old_config.copy()
    
    # Add new required fields
    if 'generation_parameters' not in new_config:
        new_config['generation_parameters'] = {
            'default_levels': 10
        }
    
    return new_config
```

### Backward Compatibility
Maintain backward compatibility when possible:
- Provide default values for new parameters
- Support legacy parameter names
- Include migration utilities
