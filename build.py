import os
import shutil
import subprocess
import sys
from pathlib import Path

# --- Configuration ---
APP_NAME = "TorrentNodeNet"
ENTRY_POINT = "desktop_app.py"
ICON_PATH = "assets/icon.ico" # Убедитесь, что иконка существует
DIST_DIR = Path("dist")
BUILD_DIR = Path("build")

def main():
    """Build the application using PyInstaller."""
    print("--- Starting build process ---")

    # Clean previous builds
    clean()

    # Create assets folder and a dummy icon if it doesn't exist
    prepare_assets()

    # Construct the PyInstaller command
    command = [
        sys.executable,  # Use the current python interpreter
        "-m", "PyInstaller",
        "--name", APP_NAME,
        "--onefile",
        "--windowed", # Use '--console' for debugging
        f"--icon={ICON_PATH}",
        "--log-level", "INFO",
        # --- Add data files and hidden imports if necessary ---
        "--hidden-import", "libtorrent",

        # --- Exclude problematic modules ---
        "--exclude-module", "pygame",
        
        # Add necessary DLLs if they are in a specific folder
        # This is often needed for libraries like libtorrent on Windows
        # "--add-binary", "path/to/your.dll;.",

        ENTRY_POINT,
    ]

    print(f"Running command: {' '.join(command)}")

    try:
        # Run PyInstaller
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("\n--- PyInstaller finished successfully ---")
        
        # Optional: post-build steps
        # E.g., copying additional files to the dist folder
        
    except subprocess.CalledProcessError as e:
        print("\n--- PyInstaller failed ---", file=sys.stderr)
        print(f"Exit Code: {e.returncode}", file=sys.stderr)
        print("\n--- STDOUT ---", file=sys.stderr)
        print(e.stdout, file=sys.stderr)
        print("\n--- STDERR ---", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
        
    print(f"\nBuild complete! Executable is at: {DIST_DIR / (APP_NAME + '.exe')}")


def clean():
    """Remove previous build artifacts."""
    print("Cleaning up old build files...")
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    
    spec_file = Path(f"{APP_NAME}.spec")
    if spec_file.exists():
        spec_file.unlink()
    
    print("Cleanup complete.")


def prepare_assets():
    """Create a dummy icon if it doesn't exist to avoid build errors."""
    icon_path = Path(ICON_PATH)
    icon_path.parent.mkdir(exist_ok=True)
    
    if not icon_path.exists():
        print(f"Warning: Icon not found at '{ICON_PATH}'. A dummy file will be created.")
        print("Build will proceed, but the .exe will have a default icon.")
        # Create a tiny dummy file. PyInstaller will use its default icon.
        try:
            from PIL import Image
            img = Image.new('RGB', (32, 32), color = 'red')
            img.save(icon_path, 'ICO')
            print(f"Created a dummy icon at '{icon_path}'.")
        except ImportError:
            print("Pillow library not found. Cannot create a dummy icon.")
            print("Please create the icon file manually or install Pillow (`pip install Pillow`).")
            # Create an empty file as a placeholder
            icon_path.touch()

if __name__ == "__main__":
    main() 