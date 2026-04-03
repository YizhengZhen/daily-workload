#!/usr/bin/env python3
"""
Setup script for Daily Research Tracker.
Helps install dependencies and configure the system.
"""
import os
import sys
import subprocess
import yaml
from pathlib import Path


def check_python_version():
    """Check Python version compatibility."""
    import platform
    version = platform.python_version_tuple()
    major, minor = int(version[0]), int(version[1])
    
    if major < 3 or (major == 3 and minor < 10):
        print(f"❌ Python 3.10+ required. Found Python {major}.{minor}")
        return False
    print(f"✅ Python {major}.{minor} detected")
    return True


def install_dependencies():
    """Install required Python packages."""
    print("\n📦 Installing dependencies...")
    
    dependencies = [
        "feedparser>=6.0.0",
        "requests>=2.28.0",
        "PyYAML>=6.0",
        "langchain>=0.3.20",
        "langchain-openai>=0.3.9",
        "tqdm>=4.67.1",
        "python-dateutil>=2.8.0",
        "pydantic>=2.0.0",
        "jinja2>=3.0.0",
    ]
    
    try:
        # Try using pip
        for dep in dependencies:
            print(f"  Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
        
        print("✅ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("\nYou can try manual installation:")
        print("  pip install " + " ".join(dependencies))
        return False


def check_config_files():
    """Check if required configuration files exist."""
    print("\n⚙️  Checking configuration files...")
    
    required_files = [
        ("rss_sources.txt", "RSS feed URLs"),
        ("config.yaml", "Main configuration"),
        ("research_directions.md", "Research directions"),
    ]
    
    all_exist = True
    for filename, description in required_files:
        if os.path.exists(filename):
            print(f"  ✅ {filename} found")
        else:
            print(f"  ⚠️  {filename} missing ({description})")
            all_exist = False
    
    if not all_exist:
        print("\nSome configuration files are missing.")
        print("Please create them based on the examples in the repository.")
    
    return all_exist


def validate_rss_feeds():
    """Validate RSS feed URLs in rss_sources.txt."""
    print("\n🔗 Validating RSS feeds...")
    
    if not os.path.exists("rss_sources.txt"):
        print("  ❌ rss_sources.txt not found")
        return False
    
    with open("rss_sources.txt", "r", encoding='utf-8') as f:
        lines = f.readlines()
    
    valid_urls = 0
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Basic URL validation
        if line.startswith('http://') or line.startswith('https://'):
            print(f"  ✅ Line {i}: Valid URL format")
            valid_urls += 1
        else:
            print(f"  ⚠️  Line {i}: Invalid URL format - {line}")
    
    print(f"\n  Total valid RSS feeds: {valid_urls}")
    return valid_urls > 0


def check_api_keys():
    """Check if API keys are configured."""
    print("\n🔐 Checking API configuration...")
    
    # Check environment variables
    api_key = os.environ.get('OPENAI_API_KEY')
    base_url = os.environ.get('OPENAI_BASE_URL')
    
    if api_key:
        print(f"  ✅ OPENAI_API_KEY found (length: {len(api_key)})")
    else:
        print("  ⚠️  OPENAI_API_KEY not set in environment")
        print("     Set it with: export OPENAI_API_KEY='your-key'")
    
    if base_url:
        print(f"  ✅ OPENAI_BASE_URL found: {base_url}")
    else:
        print("  ⚠️  OPENAI_BASE_URL not set in environment")
        print("     Set it with: export OPENAI_BASE_URL='https://api.deepseek.com'")
    
    # Check config.yaml for model settings
    if os.path.exists("config.yaml"):
        with open("config.yaml", "r", encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if config and 'llm' in config:
            model = config['llm'].get('model_name', 'Not specified')
            print(f"  📋 Configured model: {model}")
    
    return bool(api_key and base_url)


def create_directory_structure():
    """Create necessary directory structure."""
    print("\n📁 Creating directory structure...")
    
    directories = [
        "data",
        "website",
        "website/css",
        "website/js",
        "website/data",
        "obsidian",
        ".github/workflows",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {directory}")
    
    print("✅ Directory structure created")


def test_basic_functionality():
    """Test basic functionality of the system."""
    print("\n🧪 Testing basic functionality...")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Python imports
    total_tests += 1
    try:
        import feedparser
        import requests
        import yaml
        print("  ✅ Python imports work")
        tests_passed += 1
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
    
    # Test 2: Config loading
    total_tests += 1
    if os.path.exists("config.yaml"):
        try:
            with open("config.yaml", "r", encoding='utf-8') as f:
                config = yaml.safe_load(f)
            print("  ✅ Config file can be loaded")
            tests_passed += 1
        except Exception as e:
            print(f"  ❌ Config loading failed: {e}")
    else:
        print("  ⚠️  Config file not found (skipping)")
    
    # Test 3: Script imports
    total_tests += 1
    try:
        sys.path.insert(0, os.getcwd())
        from structure import PaperAnalysis
        print(" ✅ Local module imports work")
        tests_passed += 1
    except ImportError as e:
        print(f"  ❌ Local import failed: {e}")
    
    print(f"\n  Tests passed: {tests_passed}/{total_tests}")
    return tests_passed == total_tests


def show_next_steps():
    """Show next steps for the user."""
    print("\n" + "="*60)
    print("🚀 SETUP COMPLETE - NEXT STEPS")
    print("="*60)
    print("\n1. Configure RSS feeds:")
    print("   • Edit rss_sources.txt with your preferred RSS URLs")
    print("   • Add arXiv categories (e.g., http://export.arxiv.org/rss/cs.CL)")
    print("   • Add journal RSS feeds (Nature, Science, APS, etc.)")
    
    print("\n2. Set research directions:")
    print("   • Edit research_directions.md with your research interests")
    print("   • Use bullet points for different research areas")
    
    print("\n3. Configure API access:")
    print("   • Set OPENAI_API_KEY environment variable")
    print("   • Set OPENAI_BASE_URL (e.g., https://api.deepseek.com)")
    print("   • Or edit config.yaml with your API settings")
    
    print("\n4. Test the system:")
    print("   • Run: python fetch_rss.py (to test RSS fetching)")
    print("   • Run: python -c \"from structure import PaperAnalysis; print('OK')\"")
    
    print("\n5. For GitHub Actions:")
    print("   • Add OPENAI_API_KEY and OPENAI_BASE_URL as repository secrets")
    print("   • Enable GitHub Pages for the repository")
    print("   • The workflow will run daily at 02:00 UTC")
    
    print("\n6. For local testing:")
    print("   • Create a virtual environment: python -m venv .venv")
    print("   • Activate it and install dependencies")
    print("   • Run the full pipeline manually")
    
    print("\n📚 Documentation:")
    print("   • See README.md for detailed instructions")
    print("   • Check config.yaml for all configuration options")
    print("\n" + "="*60)


def main():
    """Main setup function."""
    print("="*60)
    print("Daily Research Tracker - Setup Script")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Please upgrade Python to version 3.10 or higher")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Create directory structure
    create_directory_structure()
    
    # Check configuration
    check_config_files()
    validate_rss_feeds()
    check_api_keys()
    
    # Test functionality
    test_basic_functionality()
    
    # Show next steps
    show_next_steps()


if __name__ == "__main__":
    main()