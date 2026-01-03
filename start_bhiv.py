#!/usr/bin/env python3
"""
BHIV Central Depository Startup Script
=====================================

This script starts the BHIV Central Depository system with proper initialization.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import pymongo
        import redis
        print("✅ Core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check environment configuration"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️ .env file not found")
        print("Creating .env from .env.example...")
        
        example_file = Path(".env.example")
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("✅ .env file created from example")
            print("Please edit .env with your configuration")
        else:
            print("❌ .env.example not found")
            return False
    else:
        print("✅ .env file found")
    
    return True

def start_system():
    """Start the BHIV Central Depository system"""
    print("🏛️ Starting BHIV Central Depository...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Start the main application
    print("🚀 Starting Truth Engine on port 8000...")
    try:
        # Import and run the main application
        from main import app
        import uvicorn
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=False
        )
    except KeyboardInterrupt:
        print("\n🛑 Shutting down BHIV Central Depository...")
    except Exception as e:
        print(f"❌ Failed to start system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_system()