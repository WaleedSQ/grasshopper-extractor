"""
Verify that all external inputs have been extracted from GHX.
"""
import json

# Load external inputs
with open('external_inputs.json', 'r') as f:
    external_inputs = json.load(f)

# Check for placeholders (None values)
placeholders = []
for guid, info in external_inputs.items():
    if isinstance(info, dict):
        value = info.get('value')
        if value is None:
            placeholders.append({
                'guid': guid,
                'type': info.get('type', 'Unknown'),
                'note': info.get('note', '')
            })

print("External Inputs Summary:")
print(f"Total entries: {len(external_inputs)}")
print(f"Placeholders (None values): {len(placeholders)}")
print()

if placeholders:
    print("Placeholders (external geometry inputs - no values in GHX):")
    for p in placeholders:
        print(f"  {p['guid'][:8]}... ({p['type']}): {p['note']}")
    print()
    print("Note: These are external geometry inputs from Rhino.")
    print("They don't have values in the GHX file and need to be provided at runtime.")
else:
    print("All external inputs have values!")

print()
print("Key External Inputs:")
key_inputs = {
    'c4c92669-f802-4b5f-b3fb-61b8a642dc0a': 'MD Slider',
    'e5d1f3af-f59d-40a8-aa35-162cf16c9594': 'Value List (Orientations)',
    '12d02e9b-6145-4953-8f48-b184902a818f': 'Point',
    '8fec620f-ff7f-4b94-bb64-4c7fce2fcb34': 'Surface'
}

for guid, name in key_inputs.items():
    if guid in external_inputs:
        info = external_inputs[guid]
        if isinstance(info, dict):
            value = info.get('value')
            print(f"  {name} ({guid[:8]}...): {value}")
        else:
            print(f"  {name} ({guid[:8]}...): {info}")
    else:
        print(f"  {name} ({guid[:8]}...): NOT FOUND")

