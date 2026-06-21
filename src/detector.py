"""
detector.py
Modul untuk menangani pemrosesan citra tahap awal (Region Proposal / Localization).
Saat ini menggunakan U-Net dari pustaka `rembg` untuk menghapus latar belakang
(buah, tanah, ranting) agar model CNN hanya fokus pada daun.
"""

from PIL import Image

try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    print("WARNING: Pustaka 'rembg' belum diinstal. Fitur AI Background Removal dinonaktifkan.")

def remove_background(image: Image.Image) -> Image.Image:
    """
    Menghapus latar belakang dari gambar menggunakan model U-Net (rembg).
    Mengembalikan gambar berupa objek utama (daun) dengan latar belakang solid hitam.
    """
    if not REMBG_AVAILABLE:
        return image
    
    # Proses remove background
    output_image = remove(image)
    
    # Karena output RGBA (transparan), kita ubah ke RGB dengan background hitam.
    # Model PlantVillage CNN lebih mudah memproses background solid daripada transparan.
    background = Image.new("RGB", output_image.size, (0, 0, 0))
    if output_image.mode == 'RGBA':
        background.paste(output_image, mask=output_image.split()[3]) 
    else:
        background.paste(output_image)
        
    return background
