import json
import os
import re

def bump_version():
    # Resolve manifest path relative to script location for robust execution
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    manifest_path = os.path.join(root_dir, 'manifest.json')

    if not os.path.exists(manifest_path):
        print(f"Error: Could not find manifest.json at {manifest_path}")
        return

    with open(manifest_path, 'r') as f:
        data = json.load(f)

    version = data['header']['version']
    
    version[2] += 1
    
    # Handle version rollover: 0.1.9 -> 0.2.0
    if version[2] > 9:
        version[2] = 0
        version[1] += 1
        
        if version[1] > 9:
            version[1] = 0
            version[0] += 1

    new_version_str = f"{version[0]}.{version[1]}.{version[2]}"

    # Synchronize version string in header name (e.g., "Opus Visuals 0.1.0" -> "0.1.1")
    old_name = data['header']['name']
    new_name = re.sub(r'\d+\.\d+\.\d+', new_version_str, old_name)
    data['header']['name'] = new_name

    data['header']['version'] = version
    
    # Propagate version bump to all modules to maintain parity
    if 'modules' in data:
        for module in data['modules']:
            module['version'] = version

    with open(manifest_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Pack name updated to: '{new_name}'")
    print(f"Version bumped to: {new_version_str}")

if __name__ == "__main__":
    bump_version()
