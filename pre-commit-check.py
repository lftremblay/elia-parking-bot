#!/usr/bin/env python3
"""
Pre-commit Hook - Validates syntax and critical imports before git commit
Run this before committing to prevent GitHub Actions failures
"""

import ast
import sys
import subprocess
from pathlib import Path

def check_syntax(file_path):
    """Check syntax of a single Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_playwright_imports(file_path):
    """Check for proper Playwright import handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file uses Playwright types
        playwright_types = ['Page', 'Browser', 'BrowserContext']
        uses_playwright = any(ptype in content for ptype in playwright_types)
        
        if uses_playwright:
            # Check for proper import handling
            has_playwright_import = 'from playwright.async_api import' in content
            has_try_except = 'try:' in content and 'except ImportError' in content
            
            if has_playwright_import and not has_try_except:
                return False, "Uses Playwright without safe import handling"
        
        return True, None
    except Exception as e:
        return False, f"Import check error: {str(e)}"

def get_staged_files():
    """Get list of staged Python files"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '*.py'],
            capture_output=True, text=True, check=True
        )
        return [Path(f.strip()) for f in result.stdout.splitlines() if f.strip()]
    except subprocess.CalledProcessError:
        return []

def main():
    """Pre-commit validation"""
    print("🔍 Pre-commit Validation")
    print("=" * 40)
    
    # Get staged files
    staged_files = get_staged_files()
    
    if not staged_files:
        print("✅ No Python files staged - skipping validation")
        return 0
    
    print(f"📁 Checking {len(staged_files)} staged Python files...")
    
    errors = []
    
    for file_path in staged_files:
        if not file_path.exists():
            continue
            
        relative_path = str(file_path)
        
        # Check syntax
        syntax_ok, syntax_error = check_syntax(file_path)
        if not syntax_ok:
            errors.append(f"❌ {relative_path}: SYNTAX ERROR - {syntax_error}")
            continue
        
        # Check Playwright imports
        import_ok, import_error = check_playwright_imports(file_path)
        if not import_ok:
            errors.append(f"❌ {relative_path}: IMPORT ERROR - {import_error}")
            continue
        
        print(f"✅ {relative_path}")
    
    print("\n" + "=" * 40)
    
    if errors:
        print("🚨 VALIDATION FAILED!")
        print("Fix these errors before committing:")
        for error in errors:
            print(error)
        print(f"\n❌ COMMIT BLOCKED - Fix errors and try again")
        return 1
    else:
        print("🎉 VALIDATION PASSED!")
        print("✅ Safe to commit")
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
