#!/usr/bin/env python3
# Examine the exact issue around line 973

with open('browser_automation.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== EXAMINING LINES 970-980 ===")
for i in range(969, min(len(lines), 980)):
    line_num = i + 1
    line = lines[i]
    print(f"{line_num:3d}: {repr(line)}")
    
print("\n=== LOOKING FOR TRY BLOCKS ===")
for i in range(960, min(len(lines), 990)):
    line_num = i + 1
    line = lines[i].strip()
    if line.startswith('try:') or line.startswith('except'):
        print(f"{line_num:3d}: {line}")
