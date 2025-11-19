"""
Extract Panel Source connections from trimmed GHX file and update panel_sources.json.
"""
import xml.etree.ElementTree as ET
import json
import os

ghx_file = 'core-only_trimmed2.ghx'
output_file = 'panel_sources.json'

print(f"Extracting Panel Source connections from {ghx_file}...")

tree = ET.parse(ghx_file)
panel_sources = {}

# Find all Panel components
for obj_chunk in tree.findall('.//chunk[@name="Object"]'):
    instance_guid = None
    nickname = None
    obj_type = None
    source_guid = None
    
    # Get items from Container chunk
    container = obj_chunk.find('.//chunk[@name="Container"]')
    if container is None:
        continue
    
    for item in container.findall('.//item'):
        item_name = item.get('name')
        if item_name == 'InstanceGuid':
            instance_guid = item.text
        elif item_name == 'NickName':
            nickname = item.text
        elif item_name == 'Name':
            if 'Panel' in (item.text or ''):
                obj_type = 'Panel'
        elif item_name == 'Source':
            source_guid = item.text
    
    # Check if it's a Panel
    if obj_type == 'Panel' and instance_guid and source_guid:
        print(f"Found Panel: '{nickname}' ({instance_guid[:8]}...) -> Source: {source_guid[:8]}...")
        panel_sources[instance_guid] = {
            'source_guid': source_guid,
            'nickname': nickname or 'Panel'
        }

print(f"\nExtracted {len(panel_sources)} Panel Source connections")

# Load existing panel_sources.json if it exists
existing_sources = {}
if os.path.exists(output_file):
    try:
        with open(output_file, 'r') as f:
            existing_sources = json.load(f)
        print(f"Loaded {len(existing_sources)} existing Panel sources")
    except Exception as e:
        print(f"Warning: Could not load existing {output_file}: {e}")

# Merge with existing (new ones take precedence)
existing_sources.update(panel_sources)

# Save updated panel_sources.json
with open(output_file, 'w') as f:
    json.dump(existing_sources, f, indent=2)

print(f"Saved {len(existing_sources)} Panel sources to {output_file}")

# Print summary
print("\nPanel Source connections:")
for panel_guid, info in panel_sources.items():
    print(f"  {info['nickname']} ({panel_guid[:8]}...) -> {info['source_guid'][:8]}...")

