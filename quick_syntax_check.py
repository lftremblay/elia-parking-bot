#!/usr/bin/env python3
"""
Quick Syntax Check - Validates all Python files for syntax errors
"""

import ast
import os
from pathlib import Path

def check_syntax(file_path):
    """Check syntax of a single Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST to check syntax
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Check all Python files for syntax errors"""
    print("🔍 Quick Syntax Check for All Python Files")
    print("=" * 50)
    
    # Find all Python files
    python_files = list(Path('.').rglob('*.py'))
    
    # Exclude common directories
    exclude_dirs = {'__pycache__', '.git', '.venv', '.venv310', 'node_modules'}
    python_files = [f for f in python_files if not any(exclude in str(f) for exclude in exclude_dirs)]
    
    print(f"📁 Checking {len(python_files)} Python files...")
    
    errors = []
    valid_files = 0
    
    for file_path in sorted(python_files):
        is_valid, error = check_syntax(file_path)
        relative_path = str(file_path)
        
        if is_valid:
            print(f"✅ {relative_path}")
            valid_files += 1
        else:
            print(f"❌ {relative_path}")
            print(f"   Error: {error}")
            errors.append((relative_path, error))
    
    print("\n" + "=" * 50)
    print("📊 SYNTAX CHECK RESULTS")
    print("=" * 50)
    print(f"✅ Valid files: {valid_files}")
    print(f"❌ Invalid files: {len(errors)}")
    print(f"📈 Success rate: {valid_files/len(python_files)*100:.1f}%")
    
    if errors:
        print(f"\n🚨 SYNTAX ERRORS FOUND:")
        for file_path, error in errors:
            print(f"❌ {file_path}: {error}")
        print(f"\n❌ FIX THESE ERRORS BEFORE DEPLOYING TO GITHUB!")
        return 1
    else:
        print(f"\n🎉 EXCELLENT! All files have valid syntax!")
        print("✅ Ready for GitHub deployment")
        return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
