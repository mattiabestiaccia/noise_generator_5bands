#!/usr/bin/env python3
"""
GUI Module per Noise Generator
Interfaccia grafica per la generazione di immagini rumorose multispettrali
"""

__version__ = "1.0.0"
__author__ = "Noise Generator Team"

# Import principali per facilitare l'uso del modulo
try:
    from .main_window import MainWindow
    from .image_viewer import ImageViewer
    from .file_selector import FileSelector
    from .project_manager import ProjectManager
    from .noise_controls import NoiseControls
except ImportError:
    # Fallback per import relativi
    pass

def launch_gui():
    """Lancia l'interfaccia grafica principale"""
    from .main_window import MainWindow
    app = MainWindow()
    app.run()

__all__ = [
    'MainWindow',
    'ImageViewer', 
    'FileSelector',
    'ProjectManager',
    'NoiseControls',
    'launch_gui'
]
