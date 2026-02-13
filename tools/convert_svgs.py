"""
Script to convert all SVG stratagem icons to PNG format and save them in .svg_cache folder

Requirements:
    - Inkscape must be installed on your system
    - Download from: https://inkscape.org/release/
    - The script will automatically detect Inkscape on Windows, Linux, and macOS
"""

import os
from pathlib import Path
import subprocess
import sys
import shutil

def find_inkscape():
    """
    Find Inkscape executable on different platforms (Windows, Linux, macOS).
    Supports both x86_64 and ARM architectures.
    
    Returns:
        Path to Inkscape executable or None if not found
    """
    # First, check if inkscape is in PATH
    inkscape_cmd = shutil.which("inkscape")
    if inkscape_cmd:
        return inkscape_cmd
    
    # Platform-specific common installation paths
    common_paths = []
    
    if sys.platform == "win32":
        # Windows paths (supports both x86_64 and ARM64)
        common_paths = [
            r"C:\Program Files\Inkscape\bin\inkscape.exe",
            r"C:\Program Files (x86)\Inkscape\bin\inkscape.exe",
            Path.home() / "AppData" / "Local" / "Programs" / "Inkscape" / "bin" / "inkscape.exe",
        ]
    elif sys.platform == "darwin":
        # macOS paths (supports both Intel and Apple Silicon)
        common_paths = [
            "/Applications/Inkscape.app/Contents/MacOS/inkscape",
            "/usr/local/bin/inkscape",
            "/opt/homebrew/bin/inkscape",  # Homebrew on Apple Silicon
            "/usr/bin/inkscape",
        ]
    else:
        # Linux paths (supports x86_64, ARM, and other architectures)
        common_paths = [
            "/usr/bin/inkscape",
            "/usr/local/bin/inkscape",
            "/snap/bin/inkscape",  # Snap package
            "/var/lib/flatpak/exports/bin/org.inkscape.Inkscape",  # Flatpak
            Path.home() / ".local" / "bin" / "inkscape",
        ]
    
    # Check each path
    for path in common_paths:
        path_obj = Path(path) if isinstance(path, str) else path
        if path_obj.exists():
            return str(path_obj)
    
    return None

def convert_svg_to_png(svg_path, output_path, inkscape_path, width=200, height=200):
    """
    Convert an SVG file to PNG format using Inkscape
    
    Args:
        svg_path: Path to the SVG file
        output_path: Path where the PNG should be saved
        inkscape_path: Path to Inkscape executable
        width: Output width in pixels (default: 200)
        height: Output height in pixels (default: 200)
    """
    try:
        subprocess.run([
            inkscape_path,
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
    # Find Inkscape executable
    inkscape_path = find_inkscape()
    
    if not inkscape_path:
        print("=" * 60)
        print("ERROR: Inkscape not found!")
        print("=" * 60)
        print("\nThis script requires Inkscape to convert SVG files to PNG.")
        print("\nPlease install Inkscape from: https://inkscape.org/release/")
        print("\nInstallation instructions:")
        print("  • Windows: Download and run the installer")
        print("  • macOS: Download the .dmg or use 'brew install inkscape'")
        print("  • Linux: Use your package manager (apt, dnf, pacman, etc.)")
        print("           or install via Snap: 'snap install inkscape'")
        print("           or install via Flatpak: 'flatpak install flathub org.inkscape.Inkscape'")
        print("\nAfter installation, re-run this script.")
        print("=" * 60)
        sys.exit(1)
    
    print(f"Found Inkscape at: {inkscape_path}")
    print("=" * 60)
    
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
        
        if convert_svg_to_png(svg_path, output_path, inkscape_path):
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
