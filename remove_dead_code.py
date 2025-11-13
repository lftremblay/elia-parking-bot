#!/usr/bin/env python3
# Remove unreachable dead code after return False

with open('browser_automation.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== REMOVING UNREACHABLE DEAD CODE ===")

# Find the return False line and remove everything after it until we find the next function
start_removal = None
end_removal = None

for i in range(len(lines)):
    line = lines[i].strip()
    if line == "return False" and i > 1000:  # The return False around line 1008
        start_removal = i + 1  # Start removing from the line after return False
        print(f"Found return False at line {i+1}, starting removal from line {start_removal+1}")
        break

if start_removal:
    # Find the next function definition or the end of file
    for i in range(start_removal, len(lines)):
        line = lines[i].strip()
        if line.startswith("def ") or line.startswith("async def "):
            end_removal = i
            print(f"Found next function at line {i+1}, ending removal at line {i}")
            break
    else:
        end_removal = len(lines)
        print(f"No next function found, removing until end of file (line {len(lines)})")
    
    # Remove the dead code
    if end_removal > start_removal:
        removed_lines = lines[start_removal:end_removal]
        print(f"\nRemoving {len(removed_lines)} lines of dead code:")
        for i, line in enumerate(removed_lines):
            line_num = start_removal + i + 1
            print(f"  Line {line_num}: {repr(line.rstrip())}")
        
        # Keep only the valid lines
        new_lines = lines[:start_removal] + lines[end_removal:]
        
        with open('browser_automation.py', 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"\n✅ Dead code removed! File reduced from {len(lines)} to {len(new_lines)} lines")
    else:
        print("❌ No dead code to remove")
else:
    print("❌ Could not find return False statement")
