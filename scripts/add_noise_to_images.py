#!/usr/bin/env python3
"""
Script per aggiungere rumore progressivamente crescente alle immagini da drone.
Applica diversi tipi di rumore tipici delle immagini UAV con 10 livelli di intensità.
Supporta immagini TIFF multi-banda (5 bande spettrali).
"""

import os
import cv2
import numpy as np
from pathlib import Path
import argparse
from tqdm import tqdm
import json
try:
    import rasterio
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False
    print("⚠ rasterio non disponibile. Installare con: pip install rasterio")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠ PIL non disponibile. Installare con: pip install Pillow")


def load_multiband_image(file_path):
    """
    Carica un'immagine multi-banda (TIFF) o standard (JPG/PNG).
    Assicura sempre il formato (bands, height, width) per immagini multi-banda.

    Args:
        file_path: Percorso del file immagine

    Returns:
        numpy.ndarray: Immagine con shape (bands, height, width) per TIFF multi-banda
                      o (height, width) per immagini 2D

    Raises:
        ValueError: Se l'immagine non può essere caricata
    """
    file_path = str(file_path)

    # Prova prima con rasterio per TIFF multi-banda
    if RASTERIO_AVAILABLE and file_path.lower().endswith(('.tif', '.tiff')):
        try:
            with rasterio.open(file_path) as src:
                # Leggi tutte le bande mantenendo il formato originale (bands, height, width)
                if src.count > 1:
                    # Multi-banda: mantieni formato (bands, height, width)
                    image = src.read()  # Shape: (bands, height, width)
                else:
                    # Singola banda: leggi e mantieni 2D
                    image = src.read(1)  # Shape: (height, width)

                return image.astype(np.float32)

        except Exception as e:
            print(f"⚠ Errore caricando con rasterio: {e}")

    # Fallback con tifffile per compatibilità
    try:
        import tifffile
        image = tifffile.imread(file_path)
        
        # Converti da formato tifffile (height, width, bands) a (bands, height, width)
        if len(image.shape) == 3:
            # Se la terza dimensione è piccola (≤10), probabilmente sono bande
            if image.shape[2] <= 10:
                # Converti da (height, width, bands) a (bands, height, width)
                image = np.transpose(image, (2, 0, 1))
            # Altrimenti mantieni il formato (potrebbe essere già (bands, height, width))
        
        return image.astype(np.float32)
        
    except ImportError:
        pass
    except Exception as e:
        print(f"⚠ Errore caricando con tifffile: {e}")

    # Fallback con PIL per TIFF
    if PIL_AVAILABLE and file_path.lower().endswith(('.tif', '.tiff')):
        try:
            with Image.open(file_path) as img:
                image = np.array(img)
                if len(image.shape) == 2:
                    image = np.expand_dims(image, axis=-1)
                elif len(image.shape) == 3 and image.shape[2] <= 10:
                    # Converti da (height, width, bands) a (bands, height, width)
                    image = np.transpose(image, (2, 0, 1))
                return image.astype(np.float32)
        except Exception as e:
            print(f"⚠ Errore caricando con PIL: {e}")

    # Fallback con OpenCV per immagini standard
    try:
        image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        if image is not None:
            if len(image.shape) == 2:
                image = np.expand_dims(image, axis=-1)
            elif len(image.shape) == 3 and image.shape[2] <= 10:
                # Converti da (height, width, bands) a (bands, height, width)
                image = np.transpose(image, (2, 0, 1))
            return image.astype(np.float32)
    except Exception as e:
        print(f"⚠ Errore caricando con OpenCV: {e}")

    raise ValueError(f"Impossibile caricare l'immagine: {file_path}")


def save_multiband_image(image, file_path, original_path=None):
    """
    Salva un'immagine multi-banda preservando il formato originale quando possibile.

    Args:
        image: numpy.ndarray con shape (bands, height, width) per TIFF multi-banda
        file_path: Percorso di output
        original_path: Percorso dell'immagine originale per copiare metadati

    Returns:
        bool: True se il salvataggio è riuscito
    """
    file_path = str(file_path)

    # Assicurati che l'immagine sia nel range corretto
    if image.dtype == np.float32:
        # Determina il tipo di dato appropriato in base al range
        img_min, img_max = image.min(), image.max()
        if img_max <= 255:
            # Immagine 8-bit
            image = np.clip(image, 0, 255).astype(np.uint8)
        else:
            # Immagine 16-bit
            image = np.clip(image, 0, 65535).astype(np.uint16)

    # Per TIFF multi-banda, usa rasterio se disponibile
    if RASTERIO_AVAILABLE and file_path.lower().endswith(('.tif', '.tiff')):
        try:
            # L'immagine è già nel formato (bands, height, width) corretto per rasterio
            if len(image.shape) == 3:
                bands, height, width = image.shape
            else:
                # Immagine 2D
                height, width = image.shape
                bands = 1

            # Copia metadati dall'originale se disponibile
            profile = {
                'driver': 'GTiff',
                'height': height,
                'width': width,
                'count': bands,
                'dtype': image.dtype,
                'compress': 'lzw',
                'interleave': 'band'  # Forza l'organizzazione per bande
            }

            if original_path and RASTERIO_AVAILABLE:
                try:
                    with rasterio.open(str(original_path)) as src:
                        profile.update({
                            'crs': src.crs,
                            'transform': src.transform,
                            'nodata': src.nodata
                        })
                except:
                    pass  # Usa il profilo di default se non riesce a leggere l'originale

            with rasterio.open(file_path, 'w', **profile) as dst:
                # Salva nel formato (bands, height, width) usando rasterio
                if len(image.shape) == 3:
                    dst.write(image.astype(profile['dtype']))
                else:
                    # Immagine 2D
                    dst.write(image.astype(profile['dtype']), 1)

            return True

        except Exception as e:
            print(f"⚠ Errore salvando con rasterio: {e}")
    
    # Fallback con tifffile per garantire formato corretto
    try:
        import tifffile
        
        if len(image.shape) == 3:
            bands, height, width = image.shape
            # Salva direttamente nel formato (bands, height, width)
            tifffile.imwrite(file_path, image.astype(image.dtype), 
                           photometric='minisblack', 
                           planarconfig='separate')  # Separate bands
        else:
            # Immagine 2D
            tifffile.imwrite(file_path, image.astype(image.dtype))
            
        return True
        
    except ImportError:
        pass
    except Exception as e:
        print(f"⚠ Errore salvando con tifffile: {e}")

    # Fallback con OpenCV per immagini standard
    try:
        if len(image.shape) == 3 and image.shape[2] == 1:
            image = image[:, :, 0]  # Rimuovi dimensione singola

        success = cv2.imwrite(file_path, image)
        return success

    except Exception as e:
        print(f"⚠ Errore salvando con OpenCV: {e}")
        return False


class NoiseGenerator:
    """Generatore di diversi tipi di rumore per immagini da drone."""
    
    def __init__(self):
        self.noise_types = [
            'gaussian',
            'salt_pepper', 
            'poisson',
            'speckle',
            'motion_blur',
            'atmospheric',
            'compression',
            'iso_noise'
        ]
        
    def add_gaussian_noise(self, image, intensity):
        """Aggiunge rumore gaussiano (rumore termico del sensore)."""
        # Determina il range dinamico dell'immagine
        img_min, img_max = image.min(), image.max()
        img_range = img_max - img_min

        # Scala l'intensità in base al range dell'immagine
        # Per immagini 8-bit: sigma da 5 a 50
        # Per immagini 16-bit: scala proporzionalmente
        base_sigma = 5 + (intensity - 1) * 5
        sigma = base_sigma * (img_range / 255.0)

        noise = np.random.normal(0, sigma, image.shape).astype(np.float32)
        noisy = image.astype(np.float32) + noise
        return np.clip(noisy, img_min, img_max)
    
    def add_salt_pepper_noise(self, image, intensity):
        """Aggiunge rumore salt and pepper (pixel difettosi)."""
        # Intensità da 0.001 a 0.01 (probabilità)
        prob = 0.001 + (intensity - 1) * 0.001
        noisy = image.copy().astype(np.float32)

        # Determina il range dinamico dell'immagine
        img_min, img_max = image.min(), image.max()

        # Lavora sempre con formato (bands, height, width)
        if len(image.shape) == 3:
            bands, height, width = image.shape
            # Salt noise (pixel bianchi) - applica a tutte le bande
            salt_mask = np.random.random((height, width)) < prob/2
            for band in range(bands):
                noisy[band][salt_mask] = img_max

            # Pepper noise (pixel neri) - applica a tutte le bande
            pepper_mask = np.random.random((height, width)) < prob/2
            for band in range(bands):
                noisy[band][pepper_mask] = img_min
        else:
            # Immagine 2D
            salt_mask = np.random.random(image.shape) < prob/2
            pepper_mask = np.random.random(image.shape) < prob/2
            noisy[salt_mask] = img_max
            noisy[pepper_mask] = img_min

        return noisy
    
    def add_poisson_noise(self, image, intensity):
        """Aggiunge rumore di Poisson (rumore shot del sensore)."""
        # Scala l'intensità per controllare il rumore
        scale = 0.1 + (intensity - 1) * 0.1

        # Determina il range dinamico dell'immagine
        img_min, img_max = image.min(), image.max()

        # Normalizza l'immagine al range [0, 1]
        normalized = (image.astype(np.float32) - img_min) / (img_max - img_min)

        # Applica rumore di Poisson
        noisy = np.random.poisson(normalized / scale) * scale

        # Riporta al range originale
        return np.clip(noisy * (img_max - img_min) + img_min, img_min, img_max)
    
    def add_speckle_noise(self, image, intensity):
        """Aggiunge rumore speckle (rumore moltiplicativo)."""
        # Intensità da 0.05 a 0.5
        variance = 0.05 + (intensity - 1) * 0.05

        # Determina il range dinamico dell'immagine
        img_min, img_max = image.min(), image.max()

        noise = np.random.normal(0, variance**0.5, image.shape)
        noisy = image.astype(np.float32) * (1 + noise)

        return np.clip(noisy, img_min, img_max)
    
    def add_motion_blur_noise(self, image, intensity):
        """Aggiunge sfocatura da movimento."""
        # Dimensione kernel da 3 a 21
        kernel_size = 3 + (intensity - 1) * 2

        # Crea kernel di motion blur
        kernel = np.zeros((kernel_size, kernel_size))
        kernel[int((kernel_size-1)/2), :] = np.ones(kernel_size)
        kernel = kernel / kernel_size

        # Applica il blur a ogni banda separatamente
        if len(image.shape) == 3:
            blurred = np.zeros_like(image, dtype=np.float32)
            bands, height, width = image.shape
            for band in range(bands):
                band_img = image[band].astype(np.uint8)
                blurred[band] = cv2.filter2D(band_img, -1, kernel)
        else:
            blurred = cv2.filter2D(image.astype(np.uint8), -1, kernel).astype(np.float32)

        return blurred
    
    def add_atmospheric_noise(self, image, intensity):
        """Simula effetti atmosferici (foschia, vapore)."""
        # Intensità da 0.1 a 1.0
        haze_intensity = 0.1 + (intensity - 1) * 0.1

        # Determina il range dinamico dell'immagine
        img_min, img_max = image.min(), image.max()

        # Applica effetto atmosferico
        atmospheric = image.astype(np.float32)

        if len(image.shape) == 3:
            bands, height, width = image.shape
            # Crea pattern di foschia
            haze = np.random.normal(0.8, 0.1, (height, width))
            haze = np.clip(haze, 0.5, 1.0)

            for band in range(bands):
                atmospheric[band] = atmospheric[band] * haze + (img_max * (1 - haze)) * haze_intensity
        else:
            # Immagine 2D
            haze = np.random.normal(0.8, 0.1, image.shape)
            haze = np.clip(haze, 0.5, 1.0)
            atmospheric = atmospheric * haze + (img_max * (1 - haze)) * haze_intensity

        return np.clip(atmospheric, img_min, img_max)
    
    def add_compression_artifacts(self, image, intensity):
        """Simula artefatti di compressione JPEG."""
        # Qualità da 95 a 50
        quality = 95 - (intensity - 1) * 5

        if len(image.shape) == 3:
            compressed = image.copy().astype(np.float32)
            bands, height, width = image.shape
            
            if bands >= 3:
                # Per immagini con almeno 3 bande, comprimi le prime 3
                # Converti in formato (height, width, 3) per OpenCV
                rgb_bands = np.transpose(image[:3], (1, 2, 0)).astype(np.uint8)

                # Comprimi e decomprimi
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
                _, encimg = cv2.imencode('.jpg', rgb_bands, encode_param)
                compressed_rgb = cv2.imdecode(encimg, 1)

                # Riconverti in formato (3, height, width) e sostituisci
                compressed[:3] = np.transpose(compressed_rgb, (2, 0, 1)).astype(np.float32)
            else:
                # Per immagini con meno di 3 bande, comprimi tutte
                for band in range(bands):
                    band_img = image[band].astype(np.uint8)
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
                    _, encimg = cv2.imencode('.jpg', band_img, encode_param)
                    compressed_band = cv2.imdecode(encimg, cv2.IMREAD_GRAYSCALE)
                    compressed[band] = compressed_band.astype(np.float32)

            return compressed
        else:
            # Immagine 2D
            img_uint8 = image.astype(np.uint8)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            _, encimg = cv2.imencode('.jpg', img_uint8, encode_param)
            compressed = cv2.imdecode(encimg, cv2.IMREAD_UNCHANGED)
            return compressed.astype(np.float32)
    
    def add_iso_noise(self, image, intensity):
        """Simula rumore ad alto ISO."""
        # Combina rumore gaussiano e cromatico
        # Intensità da 10 a 100
        sigma_luma = 5 + (intensity - 1) * 10
        sigma_chroma = 2 + (intensity - 1) * 3
        
        # Determina il range dinamico dell'immagine
        img_min, img_max = image.min(), image.max()

        # Per immagini multi-banda, applica rumore diverso per tipo di banda
        if len(image.shape) == 3:
            noisy = image.copy().astype(np.float32)
            bands, height, width = image.shape

            if bands >= 3:
                # Se abbiamo almeno 3 bande, usa conversione YUV per le prime 3
                # Converti da (bands, height, width) a (height, width, bands) per OpenCV
                rgb_part = np.transpose(image[:3], (1, 2, 0)).astype(np.uint8)
                yuv = cv2.cvtColor(rgb_part, cv2.COLOR_BGR2YUV).astype(np.float32)

                # Aggiungi rumore alla luminanza
                luma_noise = np.random.normal(0, sigma_luma, yuv[:, :, 0].shape)
                yuv[:, :, 0] += luma_noise

                # Aggiungi rumore alla crominanza
                for c in [1, 2]:
                    chroma_noise = np.random.normal(0, sigma_chroma, yuv[:, :, c].shape)
                    yuv[:, :, c] += chroma_noise

                # Riconverti in BGR e poi in formato (3, height, width)
                yuv = np.clip(yuv, 0, img_max).astype(np.uint8)
                noisy_rgb = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
                noisy[:3] = np.transpose(noisy_rgb, (2, 0, 1)).astype(np.float32)

                # Per le bande aggiuntive (4, 5, ...), applica rumore gaussiano
                for band in range(3, bands):
                    band_noise = np.random.normal(0, sigma_luma, image[band].shape)
                    noisy[band] += band_noise
            else:
                # Per immagini con meno di 3 bande, applica rumore gaussiano
                for band in range(bands):
                    band_noise = np.random.normal(0, sigma_luma, image[band].shape)
                    noisy[band] += band_noise

            return np.clip(noisy, img_min, img_max)
        else:
            # Immagine grayscale
            noise = np.random.normal(0, sigma_luma, image.shape)
            noisy = image.astype(np.float32) + noise
            return np.clip(noisy, image.min(), image.max())
    
    def apply_noise(self, image, noise_type, intensity):
        """Applica il tipo di rumore specificato con l'intensità data."""
        if noise_type == 'gaussian':
            return self.add_gaussian_noise(image, intensity)
        elif noise_type == 'salt_pepper':
            return self.add_salt_pepper_noise(image, intensity)
        elif noise_type == 'poisson':
            return self.add_poisson_noise(image, intensity)
        elif noise_type == 'speckle':
            return self.add_speckle_noise(image, intensity)
        elif noise_type == 'motion_blur':
            return self.add_motion_blur_noise(image, intensity)
        elif noise_type == 'atmospheric':
            return self.add_atmospheric_noise(image, intensity)
        elif noise_type == 'compression':
            return self.add_compression_artifacts(image, intensity)
        elif noise_type == 'iso_noise':
            return self.add_iso_noise(image, intensity)
        else:
            raise ValueError(f"Tipo di rumore non supportato: {noise_type}")


def process_images_with_noise(input_folder, output_folder, noise_levels=10):
    """
    Processa tutte le immagini nella cartella di input aggiungendo rumore progressivo.

    Args:
        input_folder: Cartella contenente le immagini originali
        output_folder: Cartella di output per le immagini con rumore
        noise_levels: Numero di livelli di rumore (default: 10)
    """

    # Crea il generatore di rumore
    noise_gen = NoiseGenerator()

    # Crea cartella di output se non esiste
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    # Trova tutte le immagini nella cartella di input (inclusi TIFF)
    image_extensions = ['.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG', '.tif', '.tiff', '.TIF', '.TIFF']
    image_files = []

    for ext in image_extensions:
        image_files.extend(Path(input_folder).glob(f'*{ext}'))

    if not image_files:
        print(f"⚠ Nessuna immagine trovata in {input_folder}")
        return

    print(f"Trovate {len(image_files)} immagini da processare")
    print(f"Tipi di rumore: {len(noise_gen.noise_types)}")
    print(f"Livelli per tipo: {noise_levels}")
    print(f"Totale immagini da generare: {len(image_files) * len(noise_gen.noise_types) * noise_levels}")

    # Statistiche per il report
    stats = {
        'total_processed': 0,
        'total_failed': 0,
        'noise_types': {},
        'original_images': len(image_files)
    }

    # Processa ogni immagine
    for img_file in tqdm(image_files, desc="Processando immagini"):

        # Carica immagine originale usando la nuova funzione multi-banda
        try:
            original_img = load_multiband_image(img_file)
            if original_img is None:
                print(f"⚠ Impossibile caricare {img_file}")
                stats['total_failed'] += 1
                continue

            print(f"📷 Caricata {img_file.name}: shape {original_img.shape}, dtype {original_img.dtype}")

        except Exception as e:
            print(f"⚠ Errore caricando {img_file}: {e}")
            stats['total_failed'] += 1
            continue

        # Nome base del file (senza estensione)
        base_name = img_file.stem

        # Applica ogni tipo di rumore
        for noise_type in noise_gen.noise_types:

            if noise_type not in stats['noise_types']:
                stats['noise_types'][noise_type] = {'processed': 0, 'failed': 0}

            # Crea cartella per questo tipo di rumore
            noise_folder = Path(output_folder) / noise_type
            noise_folder.mkdir(exist_ok=True)

            # Applica ogni livello di intensità
            for level in range(1, noise_levels + 1):
                try:
                    # Applica rumore
                    noisy_img = noise_gen.apply_noise(original_img, noise_type, level)

                    # Nome file di output - mantieni estensione TIFF per immagini multi-banda
                    if str(img_file).lower().endswith(('.tif', '.tiff')):
                        output_filename = f"{base_name}_{noise_type}_level_{level:02d}.tif"
                    else:
                        output_filename = f"{base_name}_{noise_type}_level_{level:02d}.jpg"
                    output_path = noise_folder / output_filename

                    # Salva immagine usando la nuova funzione
                    success = save_multiband_image(noisy_img, output_path, img_file)

                    if success:
                        stats['total_processed'] += 1
                        stats['noise_types'][noise_type]['processed'] += 1
                    else:
                        print(f"⚠ Errore salvando {output_path}")
                        stats['total_failed'] += 1
                        stats['noise_types'][noise_type]['failed'] += 1

                except Exception as e:
                    print(f"⚠ Errore processando {base_name} con {noise_type} livello {level}: {e}")
                    stats['total_failed'] += 1
                    stats['noise_types'][noise_type]['failed'] += 1

    return stats


def save_processing_report(stats, output_folder):
    """Salva un report dettagliato del processing."""

    report = {
        'processing_summary': {
            'total_images_processed': stats['total_processed'],
            'total_failures': stats['total_failed'],
            'original_images': stats['original_images'],
            'success_rate': f"{(stats['total_processed'] / (stats['total_processed'] + stats['total_failed']) * 100):.1f}%" if (stats['total_processed'] + stats['total_failed']) > 0 else "0%"
        },
        'noise_types_details': stats['noise_types'],
        'noise_parameters': {
            'gaussian': 'Sigma: 5-50 (deviazione standard)',
            'salt_pepper': 'Probabilità: 0.001-0.01',
            'poisson': 'Scala: 0.1-1.0',
            'speckle': 'Varianza: 0.05-0.5',
            'motion_blur': 'Kernel size: 3-21',
            'atmospheric': 'Intensità foschia: 0.1-1.0',
            'compression': 'Qualità JPEG: 95-50',
            'iso_noise': 'Sigma luma: 5-95, chroma: 2-29'
        }
    }

    # Salva report JSON
    report_path = Path(output_folder) / 'noise_processing_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Salva report testuale
    report_txt_path = Path(output_folder) / 'noise_processing_report.txt'
    with open(report_txt_path, 'w', encoding='utf-8') as f:
        f.write("REPORT PROCESSING RUMORE IMMAGINI DRONE\n")
        f.write("=" * 50 + "\n\n")

        f.write("RIEPILOGO:\n")
        f.write(f"  Immagini originali: {stats['original_images']}\n")
        f.write(f"  Immagini processate: {stats['total_processed']}\n")
        f.write(f"  Errori: {stats['total_failed']}\n")
        f.write(f"  Tasso di successo: {report['processing_summary']['success_rate']}\n\n")

        f.write("DETTAGLI PER TIPO DI RUMORE:\n")
        for noise_type, details in stats['noise_types'].items():
            f.write(f"  {noise_type}:\n")
            f.write(f"    Processate: {details['processed']}\n")
            f.write(f"    Fallite: {details['failed']}\n")

        f.write("\nPARAMETRI RUMORE:\n")
        for noise_type, params in report['noise_parameters'].items():
            f.write(f"  {noise_type}: {params}\n")

    print(f"✓ Report salvato in: {report_path}")
    print(f"✓ Report testuale salvato in: {report_txt_path}")


def main():
    """Funzione principale."""
    parser = argparse.ArgumentParser(description='Aggiunge rumore progressivo alle immagini da drone')
    
    # Opzione progetto o percorsi manuali
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--project', help='Nome del progetto (usa struttura projects/)')
    group.add_argument('-i', '--input', help='Cartella immagini di input')
    
    parser.add_argument('-o', '--output', help='Cartella di output (ignorato se --project)')
    parser.add_argument('-l', '--levels', type=int, default=10,
                       help='Numero di livelli di rumore (default: 10)')

    args = parser.parse_args()

    # Determina percorsi di input e output
    if args.project:
        # Modalità progetto
        script_dir = Path(__file__).parent.parent
        projects_dir = script_dir / "projects"
        project_path = projects_dir / args.project
        
        if not project_path.exists():
            print(f"❌ Progetto '{args.project}' non trovato in {projects_dir}")
            print("💡 Crea il progetto con: python scripts/project_manager.py create {args.project}")
            return
        
        input_dir = project_path / "input"
        output_dir = project_path / "noisy_images"
        
        # Importa project manager per logging
        try:
            import sys
            sys.path.append(str(Path(__file__).parent))
            from project_manager import NoiseProjectManager
            project_manager = NoiseProjectManager()
        except ImportError:
            project_manager = None
        
    else:
        # Modalità tradizionale
        input_dir = args.input or 'data/original'
        output_dir = args.output or 'data/noisy/noisy_images'
        project_manager = None
        
    print("🔧 GENERATORE RUMORE PER IMMAGINI DRONE")
    print("=" * 50)
    if args.project:
        print(f"📁 Progetto: {args.project}")
        print(f"📂 Percorso: {project_path}")
    print(f"📥 Input: {input_dir}")
    print(f"📤 Output: {output_dir}")
    print(f"🎚 Livelli di rumore: {args.levels}")
    print()

    # Verifica che la cartella di input esista
    if not Path(input_dir).exists():
        print(f"⚠ Cartella di input non trovata: {input_dir}")
        if args.project:
            print(f"💡 Copia le immagini originali in: {input_dir}")
        return

    # Verifica se ci sono immagini
    image_extensions = ['.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG', '.tif', '.tiff', '.TIF', '.TIFF']
    image_files = []
    for ext in image_extensions:
        image_files.extend(Path(input_dir).glob(f'*{ext}'))
    
    if not image_files:
        print(f"⚠ Nessuna immagine trovata in {input_dir}")
        if args.project:
            print(f"💡 Copia le immagini originali in: {input_dir}")
        return

    # Processa le immagini
    stats = process_images_with_noise(input_dir, output_dir, args.levels)

    if stats:
        print("\n" + "=" * 50)
        print("✅ PROCESSING COMPLETATO!")
        print(f"✓ Immagini processate: {stats['total_processed']}")
        print(f"✗ Errori: {stats['total_failed']}")

        # Salva report
        save_processing_report(stats, output_dir)
        
        # Se modalità progetto, aggiorna metadata
        if args.project and project_manager:
            processing_details = {
                "input_images": len(image_files),
                "noise_levels": args.levels,
                "total_generated": stats['total_processed'],
                "errors": stats['total_failed'],
                "noise_types": list(stats['noise_types'].keys())
            }
            project_manager.add_processing_record(
                args.project, 
                "noise_generation", 
                processing_details
            )

        print(f"\n📁 Immagini con rumore salvate in: {output_dir}")
        print("📂 Struttura cartelle:")
        for noise_type in NoiseGenerator().noise_types:
            noise_folder = Path(output_dir) / noise_type
            if noise_folder.exists():
                file_count = len(list(noise_folder.glob("*.tif")))
                print(f"   {noise_type}/  ({file_count} files)")
        
        if args.project:
            print(f"\n🎯 Prossimo passo:")
            print(f"   python scripts/analyze_noise_metrics.py --project {args.project}")
    else:
        print("❌ Errore durante l'elaborazione")


if __name__ == "__main__":
    main()
