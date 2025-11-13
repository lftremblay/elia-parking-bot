#!/usr/bin/env python3
# Check the if/elif structure around line 1010

with open('browser_automation.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== IF/ELIF STRUCTURE ANALYSIS ===")
for i in range(1000, min(len(lines), 1020)):
    line_num = i + 1
    line = lines[i]
    content = line.rstrip()
    spaces = len(line) - len(line.lstrip())
    if 'if' in content or 'elif' in content or 'else' in content:
        print(f"Line {line_num}: {spaces} spaces -> {repr(content)}")

print("\n=== BROADER CONTEXT ===")
for i in range(1005, min(len(lines), 1015)):
    line_num = i + 1
    line = lines[i]
    content = line.rstrip()
    spaces = len(line) - len(line.lstrip())
    marker = ">>>" if line_num == 1010 else "   "
    print(f"{marker} {line_num:3d} ({spaces:2d}sp): {content}")
