#!/usr/bin/env python3
# Check exact indentation around the problematic try/except blocks

with open('browser_automation.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== EXACT INDENTATION ANALYSIS ===")
key_lines = [944, 950, 975, 978]
for line_num in key_lines:
    if line_num <= len(lines):
        line = lines[line_num - 1]
        content = line.rstrip()
        spaces = len(line) - len(line.lstrip())
        print(f"Line {line_num}: {spaces} spaces -> {repr(content)}")

print("\n=== SURROUNDING CONTEXT ===")
for i in range(942, min(len(lines), 982)):
    line_num = i + 1
    line = lines[i]
    content = line.rstrip()
    spaces = len(line) - len(line.lstrip())
    marker = ">>>" if line_num in key_lines else "   "
    print(f"{marker} {line_num:3d} ({spaces:2d}sp): {content}")
