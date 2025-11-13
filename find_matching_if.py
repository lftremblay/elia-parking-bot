#!/usr/bin/env python3
# Find the matching if statement for the elif at line 1010

with open('browser_automation.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== SEARCHING FOR MATCHING IF STATEMENT ===")
# Look backwards from line 1010 to find the matching if
for i in range(1009, -1, -1):  # Go backwards from line 1010
    line = lines[i]
    content = line.strip()
    if content.startswith('if '):
        spaces = len(line) - len(line.lstrip())
        print(f"Found matching if at line {i+1}: {spaces} spaces -> {repr(line.rstrip())}")
        print(f"Elif at line 1010 should have {spaces} spaces")
        break
