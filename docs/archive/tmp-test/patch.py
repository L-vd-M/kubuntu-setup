import os
import glob

files = glob.glob('tasks/*.yml')
for file in files:
    with open(file, 'r') as f:
        content = f.read()
    
    # Replace '.changed ' with '.changed | default(false) '
    # Replace '.changed\n' with '.changed | default(false)\n'
    new_content = content.replace('.changed ', '.changed | default(false) ')
    new_content = new_content.replace('.changed\n', '.changed | default(false)\n')
    
    # Clean up double defaults if we matched ones we already manually fixed
    new_content = new_content.replace('| default(false) | default(false)', '| default(false)')
    
    if content != new_content:
        with open(file, 'w') as f:
            f.write(new_content)
        print(f"Patched {file}")
