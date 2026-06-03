import os
import re

workspace = r"d:\4. code\xa_cau_ke"
css_path = os.path.join(workspace, "css", "style.css")
js_path = os.path.join(workspace, "js", "app.js")

# 1. Update css/style.css
if os.path.exists(css_path):
    print("Updating css/style.css...")
    with open(css_path, 'r', encoding='utf-8') as f:
        css = f.read()
    
    orig1 = "font-size: 12.48px;"
    repl1 = "font-size: 14.98px;"
    orig2 = "font-size: 9.36px;"
    repl2 = "font-size: 11.23px;"
    
    if orig1 in css:
        css = css.replace(orig1, repl1)
        print(f"  Replaced '{orig1}' with '{repl1}'")
    if orig2 in css:
        css = css.replace(orig2, repl2)
        print(f"  Replaced '{orig2}' with '{repl2}'")
        
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)

# 2. Update js/app.js
if os.path.exists(js_path):
    print("\nUpdating js/app.js...")
    with open(js_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = []
    updated_count = 0
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # New Hamlet Labels (lines 1060-1115)
        if 1060 <= line_num <= 1115:
            if 'fontSize' in line:
                orig_line = line.strip()
                def replacer(match):
                    val = float(match.group(1))
                    new_val = val * 1.2
                    return f"{new_val:.2f}".rstrip('0').rstrip('.') + "px"
                new_line = re.sub(r'([\d.]+)px', replacer, line)
                new_lines.append(new_line)
                print(f"  Line {line_num} (New Label): {orig_line}  -->  {new_line.strip()}")
                updated_count += 1
                continue
                
        # Old Hamlet Labels (lines 1120-1150)
        if 1120 <= line_num <= 1150:
            if 'fontSize' in line:
                orig_line = line.strip()
                def replacer(match):
                    val = float(match.group(1))
                    new_val = val * 1.2
                    return f"{new_val:.2f}".rstrip('0').rstrip('.') + "px"
                new_line = re.sub(r'([\d.]+)px', replacer, line)
                new_lines.append(new_line)
                print(f"  Line {line_num} (Old Label): {orig_line}  -->  {new_line.strip()}")
                updated_count += 1
                continue
                
        new_lines.append(line)
        
    with open(js_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        
    print(f"Successfully updated {updated_count} lines in js/app.js.")
