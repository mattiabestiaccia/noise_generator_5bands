#!/bin/bash

# Script di avvio per il Noise Generator
# Verifica l'ambiente virtuale, installa le dipendenze e avvia la GUI

set -e  # Esce se qualsiasi comando fallisce

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzione per stampare messaggi colorati
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Funzione per verificare se un comando esiste
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Directory dello script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_DIR="$SCRIPT_DIR/venv_noise"

# Banner di avvio
echo "================================================================"
print_message $BLUE "🚀 NOISE GENERATOR - Script di Avvio"
echo "================================================================"

# Verifica Python
print_message $YELLOW "🐍 Verifica installazione Python..."
if ! command_exists python3; then
    print_message $RED "❌ Python3 non trovato. Installalo prima di continuare."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
print_message $GREEN "✅ Trovato: $PYTHON_VERSION"

# Verifica pip
if ! command_exists pip3; then
    print_message $RED "❌ pip3 non trovato. Installalo prima di continuare."
    exit 1
fi

# Verifica ambiente virtuale
print_message $YELLOW "🔧 Verifica ambiente virtuale..."
if [ ! -d "$VENV_DIR" ]; then
    print_message $YELLOW "📦 Creazione ambiente virtuale..."
    python3 -m venv "$VENV_DIR"
    print_message $GREEN "✅ Ambiente virtuale creato"
else
    print_message $GREEN "✅ Ambiente virtuale trovato"
fi

# Attiva ambiente virtuale
print_message $YELLOW "🔌 Attivazione ambiente virtuale..."
source "$VENV_DIR/bin/activate"

# Verifica se requirements.txt esiste e installa dipendenze
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    print_message $YELLOW "📋 Installazione dipendenze da requirements.txt..."
    pip install --upgrade pip
    pip install -r "$SCRIPT_DIR/requirements.txt"
    print_message $GREEN "✅ Dipendenze installate"
else
    # Installa dipendenze critiche manualmente
    print_message $YELLOW "📋 Installazione dipendenze critiche..."
    pip install --upgrade pip
    pip install numpy matplotlib tifffile rasterio imagecodecs
    print_message $GREEN "✅ Dipendenze critiche installate"
fi

# Verifica dipendenze tkinter (potrebbe richiedere installazione di sistema)
print_message $YELLOW "🖥️  Verifica tkinter..."
if ! python3 -c "import tkinter" 2>/dev/null; then
    print_message $RED "❌ tkinter non trovato."
    print_message $YELLOW "💡 Per installare tkinter su Ubuntu/Debian:"
    print_message $YELLOW "   sudo apt-get install python3-tk"
    print_message $YELLOW "💡 Per installare tkinter su Fedora/RHEL:"
    print_message $YELLOW "   sudo dnf install python3-tkinter"
    print_message $YELLOW "💡 Per installare tkinter su Arch:"
    print_message $YELLOW "   sudo pacman -S tk"
    
    read -p "Hai installato tkinter? Premi ENTER per continuare o Ctrl+C per uscire..."
fi

# Verifica che il file run_gui.py esista
if [ ! -f "$SCRIPT_DIR/run_gui.py" ]; then
    print_message $RED "❌ File run_gui.py non trovato!"
    exit 1
fi

# Avvio della GUI
print_message $GREEN "🎯 Tutto pronto! Avvio Noise Generator GUI..."
echo "================================================================"

# Cambia nella directory dello script e avvia
cd "$SCRIPT_DIR"
python3 run_gui.py

# Messaggio di chiusura
echo "================================================================"
print_message $BLUE "👋 Noise Generator chiuso."
print_message $YELLOW "💡 Per riavviare, esegui: ./start_noise_generator.sh"
echo "================================================================"
