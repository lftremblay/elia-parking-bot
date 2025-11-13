#!/usr/bin/env python3
# Examine the try block structure around the issue

with open('browser_automation.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== EXAMINING LINES 945-955 ===")
for i in range(944, min(len(lines), 955)):
    line_num = i + 1
    line = lines[i]
    print(f"{line_num:3d}: {repr(line)}")
    
print("\n=== ALL TRY/EXCEPT BLOCKS IN 940-990 RANGE ===")
for i in range(939, min(len(lines), 990)):
    line_num = i + 1
    line = lines[i].strip()
    if line.startswith('try:') or line.startswith('except'):
        print(f"{line_num:3d}: {line}")
