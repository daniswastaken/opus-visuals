import json
import os
import re
import zipfile

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

    # Zip the project directory into an .mcpack file
    pack_name = new_name.replace(' ', '-')
    mcpack_filename = f"{pack_name}.mcpack"
    
    # Remove any existing .mcpack files
    for file in os.listdir(root_dir):
        if file.endswith('.mcpack'):
            os.remove(os.path.join(root_dir, file))
            print(f"Removed old pack: {file}")

    excluded_items = ['.git', '.tools', '.env', '__pycache__', '.agents', '.gitignore']
    
    with zipfile.ZipFile(mcpack_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(root_dir):
            # Exclude development files/folders
            dirs[:] = [d for d in dirs if d not in excluded_items]
            
            for file in files:
                if file in excluded_items or file.endswith('.mcpack') or file.endswith('.pyc'):
                    continue
                
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, root_dir)
                zipf.write(file_path, arcname)
    
    print(f"Pack created: {mcpack_filename}")
    print(f"Excluded items: {', '.join(excluded_items)}")

if __name__ == "__main__":
    bump_version()
