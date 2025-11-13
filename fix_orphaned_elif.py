#!/usr/bin/env python3
# Fix orphaned elif statements by converting them to if statements

with open('browser_automation.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== FIXING ORPHANED ELIF STATEMENTS ===")

# Fix line 1010 (index 1009) - change elif to if
if len(lines) > 1009:
    original = lines[1009]
    lines[1009] = lines[1009].replace('elif method == "email":', 'if method == "email":', 1)
    print(f"Fixed line 1010:")
    print(f"Before: {repr(original.rstrip())}")
    print(f"After:  {repr(lines[1009].rstrip())}")

# Fix line 1015 (index 1014) - change elif to if  
if len(lines) > 1014:
    original = lines[1014]
    lines[1014] = lines[1014].replace('elif method == "push":', 'if method == "push":', 1)
    print(f"\nFixed line 1015:")
    print(f"Before: {repr(original.rstrip())}")
    print(f"After:  {repr(lines[1014].rstrip())}")

with open('browser_automation.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("\n✅ Orphaned elif statements fixed!")
