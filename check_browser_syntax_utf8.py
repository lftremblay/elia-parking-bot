#!/usr/bin/env python3
import ast

try:
    with open('browser_automation.py', 'r', encoding='utf-8') as f:
        content = f.read()
    ast.parse(content)
    print("✅ browser_automation.py - Syntax OK")
except SyntaxError as e:
    print(f"❌ browser_automation.py - Line {e.lineno}: {e.msg}")
except Exception as e:
    print(f"❌ browser_automation.py - Error: {e}")
