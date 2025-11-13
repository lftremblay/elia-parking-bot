#!/usr/bin/env python3
import ast
import sys

try:
    with open('browser_automation.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Try to parse and find the exact error
    content = ''.join(lines)
    ast.parse(content)
    print("✅ Syntax OK")
    
except SyntaxError as e:
    print(f"❌ Syntax Error at line {e.lineno}: {e.msg}")
    print(f"Context:")
    start = max(0, e.lineno - 3)
    end = min(len(lines), e.lineno + 2)
    for i in range(start, end):
        marker = ">>> " if i + 1 == e.lineno else "    "
        print(f"{marker}{i+1:3d}: {lines[i].rstrip()}")
        
except Exception as e:
    print(f"❌ Other error: {e}")
