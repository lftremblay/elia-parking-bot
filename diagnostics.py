"""
Diagnostics and Health Check Script
Verifies system requirements and configuration
"""

import sys
import subprocess
import json
from pathlib import Path
from loguru import logger


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        logger.success(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        logger.error(f"❌ Python {version.major}.{version.minor} - Need 3.8+")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    required = [
        'playwright',
        'loguru',
        'cryptography',
        'pyotp',
        'requests',
        'schedule',
        'opencv-python',
        'numpy',
        'pillow'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            logger.success(f"✅ {package}")
        except ImportError:
            logger.error(f"❌ {package} - Missing")
            missing.append(package)
    
    return len(missing) == 0, missing


def check_playwright_browsers():
    """Check if Playwright browsers are installed"""
    try:
        result = subprocess.run(
            ['playwright', 'install', '--dry-run', 'chromium'],
            capture_output=True,
            text=True
        )
        
        if 'already installed' in result.stdout.lower() or result.returncode == 0:
            logger.success("✅ Playwright Chromium")
            return True
        else:
            logger.error("❌ Playwright Chromium - Not installed")
            return False
    except Exception as e:
        logger.error(f"❌ Playwright check failed: {e}")
        return False


def check_configuration():
    """Check if configuration files exist and are valid"""
    checks = {
        'config.json': False,
        '.env': False
    }
    
    # Check config.json
    if Path('config.json').exists():
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            required_keys = ['elia', 'schedules', 'retry']
            if all(key in config for key in required_keys):
                logger.success("✅ config.json - Valid")
                checks['config.json'] = True
            else:
                logger.warning("⚠️ config.json - Missing required keys")
        except json.JSONDecodeError:
            logger.error("❌ config.json - Invalid JSON")
    else:
        logger.warning("⚠️ config.json - Not found (run --setup)")
    
    # Check .env
    if Path('.env').exists():
        with open('.env', 'r') as f:
            env_content = f.read()
        
        if 'ELIA_PASSWORD=' in env_content and 'YOUR_PASSWORD_HERE' not in env_content:
            logger.success("✅ .env - Configured")
            checks['.env'] = True
        else:
            logger.warning("⚠️ .env - Password not set")
    else:
        logger.warning("⚠️ .env - Not found (run --setup)")
    
    return all(checks.values())


def check_directories():
    """Check if required directories exist"""
    dirs = ['logs', 'screenshots', 'session_data', 'browser_data']
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            logger.success(f"✅ {dir_name}/")
        else:
            logger.warning(f"⚠️ {dir_name}/ - Creating...")
            dir_path.mkdir(exist_ok=True)
    
    return True


def check_windows_tasks():
    """Check if Windows tasks are configured"""
    try:
        result = subprocess.run(
            ['schtasks', '/Query', '/TN', 'EliaBot\\EliaBot_Executive'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.success("✅ Windows Task: EliaBot_Executive")
        else:
            logger.info("ℹ️ Windows Task: EliaBot_Executive - Not configured")
        
        result = subprocess.run(
            ['schtasks', '/Query', '/TN', 'EliaBot\\EliaBot_Regular'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.success("✅ Windows Task: EliaBot_Regular")
        else:
            logger.info("ℹ️ Windows Task: EliaBot_Regular - Not configured")
        
        return True
    except Exception as e:
        logger.warning(f"⚠️ Could not check Windows tasks: {e}")
        return False


def run_diagnostics():
    """Run all diagnostic checks"""
    print("=" * 60)
    print("🔍 Elia Parking Bot V4 - System Diagnostics")
    print("=" * 60)
    print()
    
    results = {}
    
    print("📋 System Requirements:")
    results['python'] = check_python_version()
    print()
    
    print("📦 Python Dependencies:")
    deps_ok, missing = check_dependencies()
    results['dependencies'] = deps_ok
    if missing:
        print(f"\n⚠️ Install missing packages: pip install {' '.join(missing)}")
    print()
    
    print("🌐 Playwright Browsers:")
    results['playwright'] = check_playwright_browsers()
    if not results['playwright']:
        print("⚠️ Install browsers: playwright install chromium")
    print()
    
    print("⚙️ Configuration:")
    results['config'] = check_configuration()
    if not results['config']:
        print("⚠️ Run setup: python main.py --setup")
    print()
    
    print("📁 Directories:")
    results['directories'] = check_directories()
    print()
    
    print("🪟 Windows Scheduled Tasks:")
    results['tasks'] = check_windows_tasks()
    print()
    
    print("=" * 60)
    
    if all(results.values()):
        print("✅ All checks passed! System ready.")
        print("\n🚀 Next step: python main.py --test-auth")
        return 0
    else:
        print("⚠️ Some checks failed. See details above.")
        print("\n💡 Quick fix:")
        print("   1. pip install -r requirements.txt")
        print("   2. playwright install chromium")
        print("   3. python main.py --setup")
        return 1


if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stdout, format="{message}", level="INFO")
    
    exit_code = run_diagnostics()
    sys.exit(exit_code)
