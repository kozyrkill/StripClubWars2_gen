"""
Image processing utilities
"""
from PIL import Image, ImageOps
from rembg import remove
from typing import Tuple
from .config import Config

class ImageProcessor:
    """Handles image processing operations"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
    
    def remove_background(self, image: Image.Image) -> Image.Image:
        """Remove background from image"""
        try:
            # Convert to bytes for rembg
            import io
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Remove background
            result_bytes = remove(img_bytes.read())
            
            # Convert back to PIL Image
            return Image.open(io.BytesIO(result_bytes))
        except Exception as e:
            print(f"⚠️ Background removal failed: {e}")
            return image
    
    def resize_image(self, image: Image.Image, target_size: Tuple[int, int], 
                    maintain_aspect: bool = True) -> Image.Image:
        """Resize image to target size"""
        if maintain_aspect:
            # Use thumbnail to maintain aspect ratio
            image.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            # Create new image with target size and paste centered
            new_image = Image.new('RGBA', target_size, (0, 0, 0, 0))
            paste_x = (target_size[0] - image.width) // 2
            paste_y = (target_size[1] - image.height) // 2
            new_image.paste(image, (paste_x, paste_y))
            return new_image
        else:
            # Direct resize without maintaining aspect ratio
            return image.resize(target_size, Image.Resampling.LANCZOS)
    
    def process_headshot(self, image: Image.Image) -> Image.Image:
        """Process headshot image"""
        # Resize to target headshot size
        processed = self.resize_image(image, self.config.HEAD_TARGET_SIZE)
        
        # Ensure proper format
        if processed.mode != 'RGBA':
            processed = processed.convert('RGBA')
            
        return processed
    
    def process_body_image(self, image: Image.Image, remove_bg: bool = True) -> Image.Image:
        """Process body image"""
        processed = image
        
        # Remove background if requested
        if remove_bg:
            processed = self.remove_background(processed)
        
        # Resize to target body size
        processed = self.resize_image(processed, self.config.BODY_TARGET_SIZE)
        
        # Ensure proper format
        if processed.mode != 'RGBA':
            processed = processed.convert('RGBA')
            
        return processed
    
    def optimize_for_game(self, image: Image.Image) -> Image.Image:
        """Optimize image for game use"""
        # Convert to RGBA if needed
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Optimize file size while maintaining quality
        # This could include palette optimization for smaller files
        return image
