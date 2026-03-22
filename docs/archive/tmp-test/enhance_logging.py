import re, glob

# Regex to safely extract the installation register variable and the component name
# e.g., line: "✓ Nano text editor - Status: {{ 'Installed' if nano_install.changed | default(false) else 'Already installed' }}"
# or line: "✓ Htop system monitor - Status: {{ htop_install.changed | default(false) | ternary('Installed', 'Already installed') }}"

files = glob.glob('/home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/*.yml')

for f_path in files:
    with open(f_path, 'r') as f:
        content = f.read()

    # We dynamically find all `lineinfile` blocks pointing to `path: "{{ log_file }}"` 
    # and aggressively upgrade their logging structure.
    lines = content.split('\n')
    new_lines = []
    
    for row in lines:
        if "line:" in row and "✓" in row and "Status:" in row and ("changed" in row or "Installed" in row):
            # Extract component name and the jinja variable (e.g. `chrome_install`)
            component_match = re.search(r'✓ (.*?) - Status:', row)
            var_match = re.search(r'\{\{ *([a-zA-Z0-9_]+)\.changed', row)
            
            if component_match and var_match:
                comp_name = component_match.group(1)
                var_name = var_match.group(1)
                
                # Natively inject the enhanced robust logger
                indent = row.split("line:")[0]
                new_row = f'{indent}line: "{{% if {var_name}.failed | default(false) %}}✗ {comp_name} - Status: Failed{{% else %}}✓ {comp_name} - Status: {{{{ {var_name}.changed | default(false) | ternary(\'Installed/Updated\', \'Already installed\') }}}}{{% endif %}}"'
                new_lines.append(new_row)
            else:
                new_lines.append(row)
        else:
            new_lines.append(row)

    with open(f_path, 'w') as f:
        f.write('\n'.join(new_lines))
