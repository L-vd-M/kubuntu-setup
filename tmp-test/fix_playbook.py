import os, glob

setup_path = '/home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/setup.yml'
with open(setup_path, 'r') as f: 
    setup_content = f.read()

# 1. Embed the global host_user_home into vars:
if 'host_user_home:' not in setup_content: 
    setup_content = setup_content.replace('vars:\n', 'vars:\n    host_user_home: "{{ lookup(\'env\', \'SUDO_USER\') | default(lookup(\'env\', \'USER\'), true) | regex_replace(\'^\', \'/home/\') }}"\n')

# Clean up previously injected logs dynamic string
setup_content = setup_content.replace("lookup('env', 'SUDO_USER') | default(lookup('env', 'USER'), true) | regex_replace('^', '/home/')", "host_user_home")

with open(setup_path, 'w') as f: 
    f.write(setup_content)

# 2. Fix all references natively across all task chunks
target_files = glob.glob('/home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/*.yml')
for tf in target_files:
    with open(tf, 'r') as f: 
        c = f.read()
    if 'ansible_env.HOME' in c:
        with open(tf, 'w') as f: 
            f.write(c.replace('ansible_env.HOME', 'host_user_home'))

# 3. Securely unindent remaining legacy hibernation blocks by 4 spaces
hib_path = '/home/lourens/Documents/Device_Setup/PC_Setup/kubuntu-setup/tasks/hibernation.yml'
with open(hib_path, 'r') as f:
    lines = f.readlines()

new_lines = []
unindent_mode = False
for line in lines:
    if unindent_mode and line.startswith('    '):
        new_lines.append(line[4:])
    else:
        new_lines.append(line)
        if 'required_swap_gb:' in line:
            unindent_mode = True

with open(hib_path, 'w') as f:
    f.writelines(new_lines)
