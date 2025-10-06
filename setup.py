#!/usr/bin/env python3
"""
Setup script for the Transcript Agent
"""

import os
import shutil
import sys

def setup_config():
    """Set up configuration files"""
    print("Setting up configuration files...")
    
    # Check if config.json exists, if not create from template
    if not os.path.exists("config.json"):
        if os.path.exists("config.json.template"):
            shutil.copy("config.json.template", "config.json")
            print("✅ Created config.json from template")
            print("⚠️  Please edit config.json with your Azure service credentials")
        else:
            print("❌ config.json.template not found")
    else:
        print("✅ config.json already exists")
    
    # Check if .env exists, if not create from template
    if not os.path.exists(".env"):
        if os.path.exists(".env.template"):
            shutil.copy(".env.template", ".env")
            print("✅ Created .env from template")
            print("⚠️  Please edit .env with your Azure service credentials")
        else:
            print("❌ .env.template not found")
    else:
        print("✅ .env already exists")

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\nChecking dependencies...")
    
    required_packages = [
        "azure.ai.documentintelligence",
        "azure.core.credentials", 
        "openai",
        "dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies are installed!")
        return True

def main():
    """Main setup function"""
    print("🚀 Transcript Agent Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("transcript_processor.py"):
        print("❌ Please run this script from the TranscriptAgent directory")
        return 1
    
    # Set up configuration
    setup_config()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    print("\n" + "=" * 50)
    print("📋 Next Steps:")
    print("1. Edit config.json or .env with your Azure service credentials")
    print("2. Test with: python transcript_processor.py --help")
    print("3. Process a transcript: python transcript_processor.py path/to/transcript.pdf")
    
    if not deps_ok:
        print("4. Install missing dependencies: pip install -r requirements.txt")
    
    print("\n📖 See README.md for detailed instructions")
    
    return 0

if __name__ == "__main__":
    exit(main())