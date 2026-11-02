from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

root = Path(__file__).resolve().parents[1]
assets = root / 'assets'
for source, output in ((assets/'portada.webp', assets/'portada_hd.webp'), (assets/'title_layers'/'background.webp', assets/'title_layers'/'background_hd.webp')):
    with Image.open(source) as original:
        if original.size != (1672, 941): raise ValueError('Unexpected cover dimensions')
        hd = original.convert('RGB').resize((3344, 1882), Image.Resampling.LANCZOS)
        hd = hd.filter(ImageFilter.UnsharpMask(radius=1.35, percent=185, threshold=1))
        hd = ImageEnhance.Contrast(hd).enhance(1.045)
        hd = ImageEnhance.Color(hd).enhance(1.055)
        hd.save(output, format='WEBP', quality=92, method=6)
    print('HD generated:', output)
