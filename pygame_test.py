import pygame
import os
import random
import sys
from pathlib import Path

# Add tools directory to path for imports
tools_dir = os.path.join(os.path.dirname(__file__), "tools")
if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)

from tools.convert_svgs import find_inkscape, convert_svg_to_png

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Image Display")

# Get paths to resource directories
stratagem_icons_dir = os.path.join(os.path.dirname(__file__), "recources", "stratagem_icons")
arrows_dir = os.path.join(os.path.dirname(__file__), "recources", "arrows")
cache_dir = os.path.join(os.path.dirname(__file__), ".svg_cache")


class ImageLoader:
    """Loads and scales images for pygame, with SVG support and caching"""
    
    def __init__(self, search_dirs=None):
        """
        Initialize the ImageLoader
        
        Args:
            search_dirs: List of directories to search for images. If None, uses default dirs.
        """
        self.search_dirs = search_dirs or [stratagem_icons_dir, arrows_dir]
        self.cache_dir = cache_dir
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _convert_svg_to_png(self, svg_path):
        """Convert SVG file to PNG and cache it using shared converter"""
        svg_name = os.path.basename(svg_path)
        cache_file = os.path.join(self.cache_dir, svg_name.replace('.svg', '.png'))
        
        # Check if PNG is already cached
        if not os.path.exists(cache_file):
            # Use the shared convert_svg_to_png function
            # It will auto-detect Inkscape if inkscape_path is None
            convert_svg_to_png(svg_path, cache_file, inkscape_path=None)
        
        return cache_file
    
    def _find_image(self, filename):
        """Find image file in search directories"""
        for directory in self.search_dirs:
            path = os.path.join(directory, filename)
            if os.path.exists(path):
                return path
        raise FileNotFoundError(f"Image '{filename}' not found in search directories")
    
    def load(self, filename, size=None, scale=None):
        """
        Load and scale an image
        
        Args:
            filename: Name of the image file (e.g., 'Stratagem_Arrow_Up.svg')
            size: Tuple (width, height) to scale to. If provided, overrides scale.
            scale: Float multiplier for scaling (e.g., 2.0 for 2x). Ignored if size is provided.
        
        Returns:
            pygame.Surface ready to blit to screen
        """
        # Find the image file
        image_path = self._find_image(filename)
        
        # Load image
        if filename.endswith('.svg'):
            png_path = self._convert_svg_to_png(image_path)
            img = pygame.image.load(png_path).convert_alpha()
        else:
            img = pygame.image.load(image_path).convert_alpha()
        
        # Scale image
        if size is not None:
            img = pygame.transform.scale(img, size)
        elif scale is not None and scale != 1.0:
            img = pygame.transform.scale_by(img, scale)
        
        return img


# Initialize loader
loader = ImageLoader()

# Get all available icons and arrows
stratagem_files = [f for f in os.listdir(stratagem_icons_dir) if f.endswith(('.png', '.svg'))]
arrow_files = os.listdir(arrows_dir)

# Select random files
random_stratagem = random.choice(stratagem_files)
random_arrow = random.choice(arrow_files)

print(f"Loading stratagem: {random_stratagem}")
print(f"Loading arrow: {random_arrow}")

try:
    stratagem_path = os.path.join(stratagem_icons_dir, random_stratagem)
    arrow_path = os.path.join(arrows_dir, random_arrow)
    
    stratagem_scaled = loader.load(random_stratagem, size=(50, 50))
    arrow_scaled = loader.load(random_arrow, size=(50, 50))
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        screen.blit(stratagem_scaled, (50, 50))  # draw stratagem icon
        screen.blit(arrow_scaled, (150, 50))  # draw arrow
        pygame.display.flip()

except Exception as e:
    print(f"Error loading images: {e}")
    pygame.quit()
    raise

pygame.quit()