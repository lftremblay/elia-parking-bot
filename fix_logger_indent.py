#!/usr/bin/env python3
# Fix the logger indentation on line 979

with open('browser_automation.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 979 (index 978) - add proper indentation for logger.debug
if len(lines) > 978:
    original = lines[978]
    lines[978] = lines[978].replace('                logger.debug(f"Could not get page title/URL: {e}")', '                    logger.debug(f"Could not get page title/URL: {e}")', 1)
    print(f"Fixed line 979:")
    print(f"Before: {repr(original.rstrip())}")
    print(f"After:  {repr(lines[978].rstrip())}")
    
    with open('browser_automation.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("✅ Logger indentation fix applied!")
else:
    print("❌ Line 979 not found")
