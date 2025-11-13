#!/usr/bin/env python3
# Fix the elif indentation on line 1010

with open('browser_automation.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 1010 (index 1009) - elif should be at the same level as if
if len(lines) > 1009:
    original = lines[1009]
    lines[1009] = lines[1009].replace('                elif method == "email":', '            elif method == "email":', 1)
    print(f"Fixed line 1010:")
    print(f"Before: {repr(original.rstrip())}")
    print(f"After:  {repr(lines[1009].rstrip())}")
    
    with open('browser_automation.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("✅ Elif indentation fix applied!")
else:
    print("❌ Line 1010 not found")
