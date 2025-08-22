#!/usr/bin/env python3
"""
Web Content Analyzer - Simple Startup Script
Quick and easy way to start both backend and frontend services
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['fastapi', 'streamlit', 'uvicorn']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Install missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def start_backend():
    """Start the FastAPI backend"""
    print("\n🚀 Starting FastAPI backend...")
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ])
    
    print("✅ Backend starting on http://localhost:8000")
    return backend_process

def start_frontend():
    """Start the Streamlit frontend"""
    print("\n🎨 Starting Streamlit frontend...")
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    frontend_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", 
        "app.py", 
        "--server.port", "8501",
        "--server.headless", "true"
    ])
    
    print("✅ Frontend starting on http://localhost:8501")
    return frontend_process

def main():
    """Main startup function"""
    print("🌐 Web Content Analyzer - Startup Script")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Start services
    backend_process = None
    frontend_process = None
    
    try:
        backend_process = start_backend()
        time.sleep(3)  # Give backend time to start
        
        frontend_process = start_frontend()
        time.sleep(2)  # Give frontend time to start
        
        print("\n🎉 Services started successfully!")
        print("📍 Access points:")
        print("   • Frontend: http://localhost:8501")
        print("   • Backend API: http://localhost:8000")
        print("   • API Docs: http://localhost:8000/docs")
        print("\n⚠️  Press Ctrl+C to stop all services")
        
        # Wait for user interrupt
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        
        if backend_process:
            backend_process.terminate()
            print("✅ Backend stopped")
            
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend stopped")
            
        print("👋 Web Content Analyzer stopped successfully!")
        
    except Exception as e:
        print(f"\n❌ Error starting services: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
