"""
Trace the exact GHX chain for Move → Area → Centroid with zero assumptions.
"""

import json
import xml.etree.ElementTree as ET

# Component instance GUIDs from GHX
FIRST_MOVE_GUID = 'ddb9e6ae-7d3e-41ae-8c75-fc726c984724'
POLAR_ARRAY_GUID = '7ad636cc-e506-4f77-bb82-4a86ba2a3fea'
LIST_ITEM_GUID = '27933633-dbab-4dc0-a4a2-cfa309c03c45'
SECOND_MOVE_GUID = '0532cbdf-875b-4db9-8c88-352e21051436'
AREA_GUID = '3bd2c1d3-149d-49fb-952c-8db272035f9e'

# Output parameter GUIDs
FIRST_MOVE_OUTPUT = '47af807c-369d-4bd2-bbbb-d53a4605f8e6'
POLAR_ARRAY_OUTPUT = '1a00d7ad-1003-4dfa-a933-6a7a60dfb0b1'
LIST_ITEM_OUTPUT = 'a72418c4-eb29-4226-9dea-f076720da34f'
SECOND_MOVE_OUTPUT = '4218a4e5-b5a7-477b-b7e2-dfc59ff7b896'
AREA_CENTROID_OUTPUT = '01fd4f89-2b73-4e61-a51f-9c3df0c876fa'

# Motion input GUIDs
FIRST_MOVE_MOTION_SOURCE = '07dcee6c-9ef1-4893-a77f-18130fa2c9ea'  # Vector 2Pt output
SECOND_MOVE_MOTION_SOURCE = 'd0668a07-838c-481c-88eb-191574362cc2'  # Amplitude output

def parse_ghx_wiring():
    """Parse GHX to extract exact wiring"""
    tree = ET.parse('core-only_trimmed2.ghx')
    root = tree.getroot()
    
    print("=" * 80)
    print("EXACT GHX WIRING FOR MOVE -> AREA -> CENTROID CHAIN")
    print("=" * 80)
    print()
    
    # Find all components
    components = {}
    for obj in root.findall(".//chunk[@name='Object']"):
        container = obj.find(".//chunk[@name='Container']")
        if container is not None:
            instance_guid_elem = container.find("./items/item[@name='InstanceGuid']")
            if instance_guid_elem is not None:
                instance_guid = instance_guid_elem.text
                name_elem = container.find("./items/item[@name='Name']")
                name = name_elem.text if name_elem is not None else "Unknown"
                nickname_elem = container.find("./items/item[@name='NickName']")
                nickname = nickname_elem.text if nickname_elem is not None else ""
                components[instance_guid] = {'name': name, 'nickname': nickname, 'obj': obj}
    
    # Trace chain
    print("1. FIRST MOVE 'Slats original' (ddb9e6ae-7d3e-41ae-8c75-fc726c984724):")
    print("-" * 80)
    if FIRST_MOVE_GUID in components:
        comp = components[FIRST_MOVE_GUID]
        print(f"   Name: {comp['name']}, Nickname: {comp['nickname']}")
        # Find Motion input source
        motion_source = None
        for param_input in comp['obj'].findall(".//chunk[@name='param_input']"):
            name_elem = param_input.find(".//item[@name='Name']")
            if name_elem is not None and name_elem.text == 'Motion':
                source_elem = param_input.find(".//item[@name='Source']")
                if source_elem is not None:
                    motion_source = source_elem.get('index')
                    source_guid = source_elem.text
                    print(f"   Motion input source: {source_guid}")
                    print(f"   Motion PersistentData: [0, 0, 10] (should be overridden by source)")
        # Find Geometry output
        for param_output in comp['obj'].findall(".//chunk[@name='param_output']"):
            name_elem = param_output.find(".//item[@name='Name']")
            if name_elem is not None and name_elem.text == 'Geometry':
                guid_elem = param_output.find(".//item[@name='InstanceGuid']")
                if guid_elem is not None:
                    print(f"   Geometry output GUID: {guid_elem.text}")
    print()
    
    print("2. POLAR ARRAY (7ad636cc-e506-4f77-bb82-4a86ba2a3fea):")
    print("-" * 80)
    if POLAR_ARRAY_GUID in components:
        comp = components[POLAR_ARRAY_GUID]
        print(f"   Name: {comp['name']}, Nickname: {comp['nickname']}")
        # Find Geometry input source
        for param_input in comp['obj'].findall(".//chunk[@name='param_input']"):
            name_elem = param_input.find(".//item[@name='Name']")
            if name_elem is not None and name_elem.text == 'Geometry':
                source_elem = param_input.find(".//item[@name='Source']")
                if source_elem is not None:
                    print(f"   Geometry input source: {source_elem.text}")
        # Find Count and Angle
        for param_input in comp['obj'].findall(".//chunk[@name='param_input']"):
            name_elem = param_input.find(".//item[@name='Name']")
            if name_elem is not None:
                if name_elem.text == 'Count':
                    persistent = param_input.find(".//chunk[@name='PersistentData']")
                    if persistent is not None:
                        item = persistent.find(".//chunk[@name='Item']")
                        if item is not None:
                            number = item.find(".//item[@name='number']")
                            if number is not None:
                                print(f"   Count: {number.text}")
                elif name_elem.text == 'Angle':
                    persistent = param_input.find(".//chunk[@name='PersistentData']")
                    if persistent is not None:
                        item = persistent.find(".//chunk[@name='Item']")
                        if item is not None:
                            number = item.find(".//item[@name='number']")
                            if number is not None:
                                print(f"   Angle: {number.text} radians")
        # Find Geometry output
        for param_output in comp['obj'].findall(".//chunk[@name='param_output']"):
            name_elem = param_output.find(".//item[@name='Name']")
            if name_elem is not None and name_elem.text == 'Geometry':
                guid_elem = param_output.find(".//item[@name='InstanceGuid']")
                if guid_elem is not None:
                    print(f"   Geometry output GUID: {guid_elem.text}")
    print()
    
    print("3. LIST ITEM (27933633-dbab-4dc0-a4a2-cfa309c03c45):")
    print("-" * 80)
    if LIST_ITEM_GUID in components:
        comp = components[LIST_ITEM_GUID]
        print(f"   Name: {comp['name']}, Nickname: {comp['nickname']}")
        # Find List input source
        for param_input in comp['obj'].findall(".//chunk[@name='InputParam']"):
            name_elem = param_input.find(".//item[@name='Name']")
            if name_elem is not None and name_elem.text == 'List':
                source_elem = param_input.find(".//item[@name='Source']")
                if source_elem is not None:
                    print(f"   List input source: {source_elem.text}")
        # Find Index and Wrap
        for param_input in comp['obj'].findall(".//chunk[@name='InputParam']"):
            name_elem = param_input.find(".//item[@name='Name']")
            if name_elem is not None:
                if name_elem.text == 'Index':
                    persistent = param_input.find(".//chunk[@name='PersistentData']")
                    if persistent is not None:
                        item = persistent.find(".//chunk[@name='Item']")
                        if item is not None:
                            number = item.find(".//item[@name='number']")
                            if number is not None:
                                print(f"   Index: {number.text}")
                elif name_elem.text == 'Wrap':
                    persistent = param_input.find(".//chunk[@name='PersistentData']")
                    if persistent is not None:
                        item = persistent.find(".//chunk[@name='Item']")
                        if item is not None:
                            boolean = item.find(".//item[@name='boolean']")
                            if boolean is not None:
                                print(f"   Wrap: {boolean.text}")
        # Find Item output
        for param_output in comp['obj'].findall(".//chunk[@name='OutputParam']"):
            name_elem = param_output.find(".//item[@name='Name']")
            if name_elem is not None and name_elem.text == 'Item':
                guid_elem = param_output.find(".//item[@name='InstanceGuid']")
                if guid_elem is not None:
                    print(f"   Item output GUID: {guid_elem.text}")
    print()
    
    print("4. SECOND MOVE 'Slats original' (0532cbdf-875b-4db9-8c88-352e21051436):")
    print("-" * 80)
    if SECOND_MOVE_GUID in components:
        comp = components[SECOND_MOVE_GUID]
        print(f"   Name: {comp['name']}, Nickname: {comp['nickname']}")
        # Find Geometry input source
        for param_input in comp['obj'].findall(".//chunk[@name='param_input']"):
            name_elem = param_input.find(".//item[@name='Name']")
            if name_elem is not None and name_elem.text == 'Geometry':
                source_elem = param_input.find(".//item[@name='Source']")
                if source_elem is not None:
                    print(f"   Geometry input source: {source_elem.text}")
        # Find Motion input source
        for param_input in comp['obj'].findall(".//chunk[@name='param_input']"):
            name_elem = param_input.find(".//item[@name='Name']")
            if name_elem is not None and name_elem.text == 'Motion':
                source_elem = param_input.find(".//item[@name='Source']")
                if source_elem is not None:
                    print(f"   Motion input source: {source_elem.text}")
                persistent = param_input.find(".//chunk[@name='PersistentData']")
                if persistent is not None:
                    item = persistent.find(".//chunk[@name='Item']")
                    if item is not None:
                        vector = item.find(".//item[@name='vector']")
                        if vector is not None:
                            x = vector.find(".//X")
                            y = vector.find(".//Y")
                            z = vector.find(".//Z")
                            if x is not None and y is not None and z is not None:
                                print(f"   Motion PersistentData: [{x.text}, {y.text}, {z.text}] (should be overridden by source)")
        # Find Geometry output
        for param_output in comp['obj'].findall(".//chunk[@name='param_output']"):
            name_elem = param_output.find(".//item[@name='Name']")
            if name_elem is not None and name_elem.text == 'Geometry':
                guid_elem = param_output.find(".//item[@name='InstanceGuid']")
                if guid_elem is not None:
                    print(f"   Geometry output GUID: {guid_elem.text}")
    print()
    
    print("5. AREA (3bd2c1d3-149d-49fb-952c-8db272035f9e):")
    print("-" * 80)
    if AREA_GUID in components:
        comp = components[AREA_GUID]
        print(f"   Name: {comp['name']}, Nickname: {comp['nickname']}")
        # Find Geometry input source
        for param_input in comp['obj'].findall(".//chunk[@name='InputParam']"):
            name_elem = param_input.find(".//item[@name='Name']")
            if name_elem is not None and name_elem.text == 'Geometry':
                source_elem = param_input.find(".//item[@name='Source']")
                if source_elem is not None:
                    print(f"   Geometry input source: {source_elem.text}")
        # Find Centroid output
        for param_output in comp['obj'].findall(".//chunk[@name='OutputParam']"):
            name_elem = param_output.find(".//item[@name='Name']")
            if name_elem is not None and name_elem.text == 'Centroid':
                guid_elem = param_output.find(".//item[@name='InstanceGuid']")
                if guid_elem is not None:
                    print(f"   Centroid output GUID: {guid_elem.text}")
    print()
    
    print("=" * 80)
    print("CHAIN SUMMARY:")
    print("=" * 80)
    print("First Move -> Polar Array -> List Item (Index=0, Wrap=true) -> Second Move -> Area -> Centroid")
    print()
    print("Key observations:")
    print("  - Second Move Motion input has ONLY Amplitude as source (d0668a07...)")
    print("  - Second Move Motion has PersistentData [0, 0, 10] (should be overridden)")
    print("  - List Item extracts Index=0 from Polar Array output")
    print("  - Expected: 10 centroids with Y=-27.416834, Z=3.8, 3.722222, ...")

if __name__ == '__main__':
    parse_ghx_wiring()

