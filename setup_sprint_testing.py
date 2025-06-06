#!/usr/bin/env python3
"""
Setup script for testing the Sprint Domain Expert LLM.

This script ensures all requirements are met before testing.
"""

import subprocess
import sys
import requests
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        logger.error(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible. Need Python 3.8+")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = ["requests", "asyncio"]
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} is available")
        except ImportError:
            missing.append(package)
            logger.warning(f"❌ {package} is missing")
    
    if missing:
        logger.info("Installing missing dependencies...")
        for package in missing:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    return len(missing) == 0

def check_ollama_installation():
    """Check if Ollama is installed and running."""
    try:
        # Check if Ollama command exists
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ Ollama is installed: {result.stdout.strip()}")
        else:
            logger.warning("❌ Ollama command not found")
            return False
            
        # Check if Ollama server is running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Ollama server is running")
            return True
        else:
            logger.warning("❌ Ollama server is not responding")
            return False
            
    except FileNotFoundError:
        logger.error("❌ Ollama is not installed")
        logger.info("Please install Ollama from: https://ollama.ai/")
        return False
    except requests.exceptions.RequestException:
        logger.warning("❌ Ollama server is not running")
        logger.info("Please start Ollama server with: ollama serve")
        return False

def check_sprint_model():
    """Check if the sprint domain expert model is loaded in Ollama."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]
            
            if "gpt2-enhanced" in model_names:
                logger.info("✅ Sprint domain expert model 'gpt2-enhanced' is loaded")
                return True
            else:
                logger.warning(f"❌ Model 'gpt2-enhanced' not found in Ollama")
                logger.info(f"Available models: {model_names}")
                logger.info("To load your model, run:")
                logger.info("  ollama create gpt2-enhanced -f /path/to/your/Modelfile")
                return False
        else:
            logger.error("❌ Cannot check Ollama models")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to check models: {e}")
        return False

def check_project_structure():
    """Check if the Four-Sided Triangle project structure is correct."""
    required_paths = [
        "app/models/domain_knowledge.py",
        "app/models/config/model_pipeline.py",
        "app/models/__init__.py"
    ]
    
    missing_paths = []
    for path in required_paths:
        if not Path(path).exists():
            missing_paths.append(path)
            logger.warning(f"❌ Missing: {path}")
        else:
            logger.info(f"✅ Found: {path}")
    
    if missing_paths:
        logger.error("❌ Project structure is incomplete")
        return False
    else:
        logger.info("✅ Project structure is correct")
        return True

def create_modelfile_template():
    """Create a template Modelfile for the sprint domain expert."""
    modelfile_content = """# Modelfile for Sprint Domain Expert
FROM /path/to/your/models/domain_llm/gpt2-enhanced

# Set parameters
PARAMETER temperature 0.1
PARAMETER num_predict 1024
PARAMETER top_k 40
PARAMETER top_p 0.9

# System prompt for sprint running expertise
SYSTEM You are a sprint running domain expert trained on 100+ academic publications. Provide evidence-based, technical responses about sprint biomechanics, training methodologies, and performance optimization. Always cite relevant scientific principles and practical applications.

# Template for sprint running queries
TEMPLATE \"\"\"
Query: {{ .Prompt }}

As a sprint running domain expert, please provide:
1. Relevant biomechanical principles
2. Key performance metrics and relationships  
3. Training methodologies
4. Academic evidence and references
5. Practical applications

Response:
\"\"\"
"""
    
    modelfile_path = Path("Modelfile.sprint-expert")
    with open(modelfile_path, "w") as f:
        f.write(modelfile_content)
    
    logger.info(f"📁 Created Modelfile template: {modelfile_path}")
    logger.info("📝 Edit the FROM path to point to your actual model location")
    logger.info("📝 Then run: ollama create gpt2-enhanced -f Modelfile.sprint-expert")

def main():
    """Run all setup checks."""
    print("🔧 Sprint Domain Expert Setup Check")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Ollama Installation", check_ollama_installation),
        ("Project Structure", check_project_structure),
        ("Sprint Model", check_sprint_model)
    ]
    
    results = {}
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        try:
            result = check_func()
            results[check_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            logger.error(f"❌ {check_name} check failed: {e}")
            results[check_name] = False
            all_passed = False
    
    print("\n" + "=" * 50)
    print("📋 SETUP SUMMARY")
    print("=" * 50)
    
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name:20} {status}")
    
    if all_passed:
        print("\n🎉 All checks passed! Ready to test your sprint domain expert.")
        print("🚀 Run: python test_sprint_expert.py")
    else:
        print("\n⚠️  Some checks failed. Please address the issues above.")
        
        if not results.get("Sprint Model", True):
            print("\n💡 To set up your model:")
            create_modelfile_template()
    
    return all_passed

if __name__ == "__main__":
    main() 