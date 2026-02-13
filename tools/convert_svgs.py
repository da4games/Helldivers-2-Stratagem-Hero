"""
Script to convert all SVG stratagem icons to PNG format and save them in .svg_cache folder
"""

import os
from pathlib import Path
import subprocess

def convert_svg_to_png(svg_path, output_path, width=200, height=200):
    """
    Convert an SVG file to PNG format using Inkscape
    
    Args:
        svg_path: Path to the SVG file
        output_path: Path where the PNG should be saved
        width: Output width in pixels (default: 200)
        height: Output height in pixels (default: 200)
    """
    try:
        subprocess.run([
            r"C:\Program Files\Inkscape\bin\inkscape.exe",
            str(svg_path),
            "--export-type=png",
            f"--export-width={width}",
            f"--export-height={height}",
            f"--export-filename={output_path}"
        ], check=True, capture_output=True)
        print(f"✓ Converted: {svg_path.name} -> {output_path.name}")
        return True
    except Exception as e:
        print(f"✗ Failed to convert {svg_path.name}: {e}")
        return False

def main():
    # Define paths
    script_dir = Path(__file__).parent.parent
    icons_dir = script_dir / 'resources' / 'stratagem_icons'
    cache_dir = script_dir / '.svg_cache'
    
    # Create .svg_cache directory if it doesn't exist
    cache_dir.mkdir(exist_ok=True)
    print(f"Cache directory: {cache_dir}")
    print("-" * 60)
    
    # Find all SVG files
    svg_files = list(icons_dir.glob('*.svg'))
    
    if not svg_files:
        print("No SVG files found in stratagem_icons directory")
        return
    
    print(f"Found {len(svg_files)} SVG files to convert\n")
    
    # Convert each SVG to PNG
    converted = 0
    failed = 0
    
    for svg_path in svg_files:
        # Create output filename (replace .svg with .png)
        output_filename = svg_path.stem + '.png'
        output_path = cache_dir / output_filename
        
        if convert_svg_to_png(svg_path, output_path):
            converted += 1
        else:
            failed += 1
    
    # Print summary
    print("-" * 60)
    print(f"\nConversion complete!")
    print(f"  Successfully converted: {converted}")
    print(f"  Failed: {failed}")
    print(f"  Total: {len(svg_files)}")
    print(f"\nPNG files saved to: {cache_dir}")

if __name__ == "__main__":
    main()
