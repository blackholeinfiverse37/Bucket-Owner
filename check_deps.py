#!/usr/bin/env python3
"""
BHIV Bucket Dependencies Check
=============================

Verifies all required dependencies are installed and working.
"""

import sys
import importlib
import subprocess

REQUIRED_PACKAGES = [
    ('fastapi', 'FastAPI'),
    ('uvicorn', 'Uvicorn'),
    ('pydantic', 'Pydantic'),
    ('pymongo', 'PyMongo'),
    ('redis', 'Redis'),
    ('python_dotenv', 'python-dotenv'),
    ('yaml', 'PyYAML'),
]

def check_package(package_name, display_name):
    """Check if a package is installed and importable"""
    try:
        importlib.import_module(package_name)
        print(f"OK {display_name}")
        return True
    except ImportError:
        print(f"MISSING {display_name} - NOT INSTALLED")
        return False

def install_missing_packages():
    """Install missing packages"""
    print("\nInstalling missing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True, text=True)
        print("OK Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR Failed to install dependencies: {e}")
        return False

def main():
    print("BHIV Bucket Dependencies Check")
    print("=" * 40)
    
    missing_packages = []
    
    for package_name, display_name in REQUIRED_PACKAGES:
        if not check_package(package_name, display_name):
            missing_packages.append(display_name)
    
    if missing_packages:
        print(f"\nWARNING Missing packages: {', '.join(missing_packages)}")
        
        response = input("\nInstall missing packages? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            if install_missing_packages():
                print("\nOK All dependencies are now installed!")
                return True
            else:
                print("\nERROR Failed to install dependencies")
                return False
        else:
            print("\nERROR Cannot proceed without required dependencies")
            return False
    else:
        print("\nOK All required dependencies are installed!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)