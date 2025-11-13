#!/usr/bin/env python3
# Fix the indentation issue on line 978

with open('browser_automation.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 978 (index 977) - change from 8 spaces to 16 spaces
if len(lines) > 977:
    original = lines[977]
    lines[977] = lines[977].replace('        except Exception as e:', '                except Exception as e:', 1)
    print(f"Fixed line 978:")
    print(f"Before: {repr(original.rstrip())}")
    print(f"After:  {repr(lines[977].rstrip())}")
    
    with open('browser_automation.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("✅ Indentation fix applied!")
else:
    print("❌ Line 978 not found")
