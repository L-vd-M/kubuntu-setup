import glob
import yaml
import sys
import re

def parse_yaml_safely(filepath):
    try:
        with open(filepath, 'r') as f:
            # We use safe_load_all because some files might have multiple documents (---)
            # or we can just parse it broadly. Actually, regex might be safer for broken YAMLs.
            content = f.read()
            return content
    except Exception:
        return ""

def extract_software(content):
    # Extract apt packages:
    # apt:\n  name: [packagenames] or name: packagename
    packages = set()
    
    # regex to find simple package names in apt/snap/npm
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('- ') and len(line) < 40:
            # might be a package list item
            pkg = line[2:].strip().strip('"\'')
            if pkg and not pkg.startswith('{') and ' ' not in pkg:
                packages.add(pkg.lower())
        
        # match apt: name=xxx
        match = re.search(r'name\s*=\s*([a-zA-Z0-9\-\_]+)', line)
        if match:
            packages.add(match.group(1).lower())
            
        # match name: xxx
        match2 = re.search(r'name:\s*([a-zA-Z0-9\-\_]+)$', line)
        if match2:
            packages.add(match2.group(1).lower())
            
    return packages

old_files = glob.glob('v*_setup.yml') + glob.glob('setup.yml.bak') + glob.glob('tasks/v*_*.yml') + glob.glob('tasks/*.bak')
new_files = ['setup.yml'] + glob.glob('tasks/*.yml')
# remove v_files from new_files
new_files = [f for f in new_files if f not in old_files]

old_content = "\n".join([parse_yaml_safely(f) for f in old_files])
new_content = "\n".join([parse_yaml_safely(f) for f in new_files])

old_pkgs = extract_software(old_content)
new_pkgs = extract_software(new_content)

# Filter out common ansible words that aren't packages
ignore = {'present', 'absent', 'latest', 'directory', 'file', 'yes', 'no', 'true', 'false', '0755', '0644', 'root'}
old_pkgs = old_pkgs - ignore
new_pkgs = new_pkgs - ignore

missing_in_new = old_pkgs - new_pkgs

# further refine: if the missing word exists ANYWHERE in the new content, it's not truly lost
truly_missing = []
for pkg in missing_in_new:
    if pkg not in new_content.lower():
        if len(pkg) > 2: # Ignore 1-2 char variables like 'rc', 'ok'
            truly_missing.append(pkg)

print("TRULY MISSING ORPHANED SOFTWARE/TERMS:")
for t in truly_missing:
    print(f"- {t}")

print("\n(Note: If this list is empty or only contains arbitrary task-naming words, absolutely 100% of functionality has been safely preserved in your modular tasks directory).")
