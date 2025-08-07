#!/usr/bin/env python3
"""
Setup script for Event Situational Awareness System
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def activate_virtualenv():
    """Activate virtual environment if available"""
    venv_path = Path(".venv")
    if venv_path.exists() and (venv_path / "bin" / "activate").exists():
        activate_script = venv_path / "bin" / "activate"
        print(f"Activating virtual environment: {activate_script}")
        activate_command = f"source {activate_script}"
        os.system(activate_command)
        return True
    else:
        print("⚠️  No virtual environment found. Please create one using 'python -m venv venv'")
        return False

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def setup_environment():
    """Set up environment file"""
    env_template = ".env.template"
    env_file = ".env"
    
    if os.path.exists(env_file):
        print("✅ .env file already exists")
        return True
    
    if os.path.exists(env_template):
        try:
            shutil.copy(env_template, env_file)
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file and add your Google Gemini API key")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("❌ .env.template not found")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["videos", "data"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Directory '{directory}' ready")
    
    return True

def check_api_key():
    """Check if API key is configured"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key and api_key != "your_google_api_key_here":
            print("✅ Google Gemini API key configured")
            return True
        else:
            print("⚠️  Google Gemini API key not configured")
            print("   Please edit .env file and add your API key")
            return False
    except ImportError:
        print("⚠️  Cannot check API key (python-dotenv not installed yet)")
        return False

def run_basic_test():
    """Run basic system test"""
    print("🧪 Running basic system test...")
    try:
        # Test imports
        import streamlit
        print("✅ Streamlit import successful")
        
        # Test config
        from config import config
        print("✅ Config module successful")
        
        # Test agents (basic import test)
        from agents.coordinator import CoordinatorAgent
        print("✅ Agent imports successful")
        
        print("✅ Basic system test passed")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚨 Event Situational Awareness System Setup")
    print("=" * 50)
    
    success_count = 0
    total_steps = 5
    
    # Step 1: Check Python version
    if check_python_version():
        success_count += 1
    
    # Step 2: Activate virtual environment
    if activate_virtualenv():
        success_count += 1

    # Step 3: Create directories
    if create_directories():
        success_count += 1

    # Step 4: Install requirements
    if install_requirements():
        success_count += 1

    # Step 5: Setup environment
    if setup_environment():
        success_count += 1

    # Step 6: Run basic test
    if run_basic_test():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"Setup completed: {success_count}/{total_steps} steps successful")
    
    if success_count == total_steps:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file and add your Google Gemini API key")
        print("2. (Optional) Add video files to the videos/ directory")
        print("3. Run: streamlit run main.py")
    elif success_count >= 3:
        print("⚠️  Setup mostly successful with some warnings")
        print("Please check the warnings above and run: streamlit run main.py")
    else:
        print("❌ Setup failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())