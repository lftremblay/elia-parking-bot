#!/usr/bin/env python3
# Analyze the function structure around the orphaned elif statements

with open('browser_automation.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== FUNCTION STRUCTURE ANALYSIS ===")
# Look for function definitions and the problematic elif statements
for i in range(1000, min(len(lines), 1020)):
    line_num = i + 1
    line = lines[i]
    content = line.rstrip()
    if 'def ' in content or 'elif' in content or 'return False' in content:
        spaces = len(line) - len(line.lstrip())
        print(f"Line {line_num}: {spaces} spaces -> {repr(content)}")

print("\n=== LOOKING FOR FUNCTION START ===")
# Find the function that contains these elif statements
for i in range(970, -1, -1):
    line = lines[i]
    content = line.strip()
    if content.startswith('def '):
        print(f"Function starts at line {i+1}: {repr(line.rstrip())}")
        break
