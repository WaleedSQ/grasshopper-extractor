"""
Parse Grasshopper GHX file to extract Rotatingslats group computation chain.
Version 2: Correct structure handling.
"""
import xml.etree.ElementTree as ET
import json
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any, Optional

def parse_ghx(filename: str):
    """Parse GHX file and extract structure."""
    tree = ET.parse(filename)
    root = tree.getroot()
    
    # Find the Definition chunk
    definition = root.find(".//chunk[@name='Definition']")
    if definition is None:
        raise ValueError("No Definition chunk found")
    
    # Extract all objects from DefinitionObjects
    objects = {}
    def_objects = definition.find(".//chunk[@name='DefinitionObjects']")
    stored_count = 0
    no_guid_count = 0
    if def_objects is not None:
        # Object chunks are direct children - use iter to get all
        obj_chunks = list(def_objects.iter("chunk"))
        obj_chunks = [chunk for chunk in obj_chunks if chunk.get("name") == "Object"]
        print(f"Found {len(obj_chunks)} object chunks")
        
        # Debug: verify we're processing all chunks
        processed_count = 0
        skipped_no_guid = 0
        skipped_scribble = 0
        for obj_chunk in obj_chunks:
            obj_guid = None
            obj_name = None
            obj_nickname = None
            obj_type = None
            instance_guid = None
            params = {}
            
            # Get GUID and name from top level (direct items of Object chunk)
            # Try both direct items and recursive search as fallback
            items_elem = obj_chunk.find("./items")
            if items_elem is not None:
                for item in items_elem.findall("./item"):
                    name = item.get("name")
                    if name == "GUID":
                        obj_guid = item.text
                    elif name == "Name":
                        obj_name = item.text
            
            # Fallback: if no GUID found in direct items, search recursively
            if not obj_guid:
                for item in obj_chunk.findall(".//item[@name='GUID']"):
                    obj_guid = item.text
                    break
            if not obj_name:
                for item in obj_chunk.findall(".//item[@name='Name']"):
                    obj_name = item.text
                    break
            
            # Get Container chunk for component details
            container = obj_chunk.find(".//chunk[@name='Container']")
            if container is not None:
                # Get properties from Container - check direct items first
                # Container has an <items> element with direct <item> children
                container_items_elem = container.find("./items")
                if container_items_elem is not None:
                    for item in container_items_elem:
                        if item.tag == "item":
                            name = item.get("name")
                            if name == "InstanceGuid":
                                instance_guid = item.text
                            elif name == "Name":
                                obj_type = item.text
                            elif name == "NickName":
                                obj_nickname = item.text
                
                # Also check recursively for any we missed
                for item in container.findall(".//item"):
                    name = item.get("name")
                    if name == "Name" and not obj_type:
                        obj_type = item.text
                    elif name == "NickName" and not obj_nickname:
                        obj_nickname = item.text
                    elif name == "InstanceGuid" and not instance_guid:
                        instance_guid = item.text
            
            # Also check for InstanceGuid anywhere in the object chunk if not found in Container
            # This needs to be done for all objects, not just those with containers
            # Search recursively in the entire object chunk
            if not instance_guid:
                # Search recursively in all chunks within this object
                # This will find InstanceGUIDs in param chunks, attributes, etc.
                # Just get the first InstanceGuid found - since we're iterating objects one at a time,
                # nested Object chunks won't be an issue
                for item in obj_chunk.findall(".//item[@name='InstanceGuid']"):
                    instance_guid = item.text
                    break
            
            # Extract parameters (inputs and outputs) - only if container exists
            if container is not None:
                # Extract parameters (inputs and outputs)
                # IMPORTANT: Find param_input/param_output chunks that are direct children of Container
                # The Container has a <chunks> element containing <chunk> elements
                # Handle both naming conventions: param_input/param_output and InputParam/OutputParam
                # Some components use ParameterData chunk which contains InputParam/OutputParam chunks
                # Use direct children only to avoid picking up nested chunks from other components
                chunks_elem = container.find("./chunks")
                param_chunks = []
                if chunks_elem is not None:
                    # Find param chunks directly in Container's chunks
                    param_chunks = chunks_elem.findall("./chunk[@name='param_input']") + chunks_elem.findall("./chunk[@name='param_output']") + chunks_elem.findall("./chunk[@name='InputParam']") + chunks_elem.findall("./chunk[@name='OutputParam']")
                    
                    # Also check ParameterData chunk for InputParam/OutputParam chunks
                    param_data_chunk = chunks_elem.find("./chunk[@name='ParameterData']")
                    if param_data_chunk is not None:
                        param_data_chunks_elem = param_data_chunk.find("./chunks")
                        if param_data_chunks_elem is not None:
                            # Find InputParam and OutputParam chunks inside ParameterData
                            nested_params = param_data_chunks_elem.findall("./chunk[@name='InputParam']") + param_data_chunks_elem.findall("./chunk[@name='OutputParam']")
                            param_chunks.extend(nested_params)
                else:
                    # Fallback: try direct children
                    param_chunks = container.findall("./chunk[@name='param_input']") + container.findall("./chunk[@name='param_output']") + container.findall("./chunk[@name='InputParam']") + container.findall("./chunk[@name='OutputParam']")
                    # Also check ParameterData
                    param_data_chunk = container.find("./chunk[@name='ParameterData']")
                    if param_data_chunk is not None:
                        param_data_chunks_elem = param_data_chunk.find("./chunks")
                        if param_data_chunks_elem is not None:
                            nested_params = param_data_chunks_elem.findall("./chunk[@name='InputParam']") + param_data_chunks_elem.findall("./chunk[@name='OutputParam']")
                            param_chunks.extend(nested_params)
                
                for param_chunk in param_chunks:
                    param_chunk_name = param_chunk.get("name", "")
                    if param_chunk_name.startswith("param_"):
                        param_name = param_chunk_name
                        param_index = param_chunk.get("index")
                    elif param_chunk_name in ["InputParam", "OutputParam"]:
                        # Convert to standard naming
                        param_name = "param_input" if param_chunk_name == "InputParam" else "param_output"
                        param_index = param_chunk.get("index")
                    else:
                        continue
                    
                    # Get param properties
                    param_data = {}
                    for item in param_chunk.findall(".//item"):
                        item_name = item.get("name")
                        if item_name in ["Name", "NickName", "Description", "InstanceGuid", "Optional", "TypeHint"]:
                            param_data[item_name] = item.text
                    
                    # Get param InstanceGuid for tracking
                    param_instance_guid = param_data.get("InstanceGuid")
                    
                    # Get param data values
                    data_chunk = param_chunk.find(".//chunk[@name='Data']")
                    param_values = []
                    if data_chunk is not None:
                        for item in data_chunk.findall(".//item"):
                            param_values.append(item.text)
                    
                    # Also check PersistentData for constant values (when no source is connected)
                    persistent_data = param_chunk.find(".//chunk[@name='PersistentData']")
                    if persistent_data is not None:
                        # Look for values in Branch -> Item chunks
                        for branch in persistent_data.findall(".//chunk[@name='Branch']"):
                            for item_chunk in branch.findall(".//chunk[@name='Item']"):
                                # Check for number, double, string, etc.
                                number_item = item_chunk.find(".//item[@name='number']")
                                if number_item is not None:
                                    param_values.append(number_item.text)
                                else:
                                    # Check for other value types
                                    for value_item in item_chunk.findall(".//item"):
                                        if value_item.get('name') not in ['TypeName']:
                                            param_values.append(value_item.text)
                    
                    # Get persistent data (constant values stored in parameter)
                    persistent_data_chunk = param_chunk.find(".//chunk[@name='PersistentData']")
                    persistent_values = []
                    if persistent_data_chunk is not None:
                        # Extract values from Branch/Item chunks
                        for branch in persistent_data_chunk.findall(".//chunk[@name='Branch']"):
                            for item_chunk in branch.findall(".//chunk[@name='Item']"):
                                # Look for value items (number, value, etc.)
                                for item in item_chunk.findall(".//item"):
                                    item_name = item.get("name")
                                    if item_name in ["number", "value", "data"]:
                                        persistent_values.append(item.text)
                                    elif item_name == "TypeName":
                                        # Store type info
                                        pass
                                # Check for vector (gh_point3d) - for Move component Motion input
                                # The vector item is a direct child of Item chunk's items element
                                items_elem = item_chunk.find("./items")
                                if items_elem is not None:
                                    vector_elem = items_elem.find(".//item[@name='vector']")
                                    if vector_elem is not None:
                                        x_elem = vector_elem.find('X')
                                        y_elem = vector_elem.find('Y')
                                        z_elem = vector_elem.find('Z')
                                        if x_elem is not None and y_elem is not None and z_elem is not None:
                                            try:
                                                x = float(x_elem.text) if x_elem.text else 0.0
                                                y = float(y_elem.text) if y_elem.text else 0.0
                                                z = float(z_elem.text) if z_elem.text else 0.0
                                                # Store as JSON string representation of vector
                                                vector_json = json.dumps([x, y, z])
                                                persistent_values.append(vector_json)
                                                # Debug: Log when we extract a vector
                                                if param_instance_guid == "3fe645ec-446c-49e2-aac5-ed0396624da0":
                                                    print(f"DEBUG: Extracted vector from PersistentData: {vector_json} for Motion param")
                                            except (ValueError, TypeError) as e:
                                                if param_instance_guid == "3fe645ec-446c-49e2-aac5-ed0396624da0":
                                                    print(f"DEBUG: Error extracting vector: {e}")
                                                pass
                        # Also check direct items in PersistentData
                        for item in persistent_data_chunk.findall(".//item"):
                            item_name = item.get("name")
                            if item_name in ["number", "value", "data"]:
                                persistent_values.append(item.text)
                    
                    # Get connections (Sources)
                    # IMPORTANT: Only search for Source items that are direct children of items element,
                    # not nested in other chunks (like PersistentData)
                    sources = []
                    # First try direct children of param_chunk's items element
                    items_elem = param_chunk.find("./items")
                    if items_elem is not None:
                        for item in items_elem.findall("./item[@name='Source']"):
                            source_guid = item.text
                            source_index = item.get("index")
                            sources.append({
                                "guid": source_guid,
                                "index": int(source_index) if source_index else None
                            })
                    # Fallback: search in param_chunk but exclude nested chunks
                    if not sources:
                        for item in param_chunk.findall("./item[@name='Source']"):
                            source_guid = item.text
                            source_index = item.get("index")
                            sources.append({
                                "guid": source_guid,
                                "index": int(source_index) if source_index else None
                            })
                    
                    # Debug: Log Series component Step input for verification
                    if instance_guid == "b785e424-ebb1-42fc-ac03-dee2d7d764b4" and (param_index == "1" or param_index == 1):
                        print(f"DEBUG: Processing Series {instance_guid[:8]}... Step input")
                        print(f"  Component: {obj_type}")
                        print(f"  Param InstanceGuid: {param_instance_guid}")
                        print(f"  param_index type: {type(param_index)}, value: {param_index}")
                        print(f"  Found {len(sources)} sources: {sources}")
                        if items_elem is not None:
                            all_source_items = items_elem.findall("./item[@name='Source']")
                            print(f"  Source items in XML: {[item.text for item in all_source_items]}")
                            # Also check the raw XML text to see what's actually there
                            source_item = items_elem.find("./item[@name='Source']")
                            if source_item is not None:
                                print(f"  Raw XML source text: '{source_item.text}'")
                        else:
                            print(f"  WARNING: items_elem is None!")
                        # Verify we're in the right container by checking the container's InstanceGuid
                        # (we already have instance_guid from the container, so just confirm)
                        print(f"  Container InstanceGuid (should match): {instance_guid}")
                    
                    # Get source parameter info
                    source_params = []
                    for item in param_chunk.findall(".//item[@name='SourceParam']"):
                        source_param = item.text
                        source_params.append(source_param)
                    
                    key = f"{param_name}_{param_index}" if param_index else param_name
                    
                    # Ensure we're not overwriting with wrong data - verify param InstanceGuid matches
                    # This helps catch cases where we might be reading from wrong param_input
                    existing_param = params.get(key)
                    if existing_param and existing_param.get("data", {}).get("InstanceGuid") != param_instance_guid:
                        print(f"WARNING: Overwriting param {key} for component {instance_guid[:8]}...")
                        print(f"  Old InstanceGuid: {existing_param.get('data', {}).get('InstanceGuid')}")
                        print(f"  New InstanceGuid: {param_instance_guid}")
                    
                    params[key] = {
                        "data": param_data,
                        "values": param_values,
                        "persistent_values": persistent_values,  # Constant values stored in parameter
                        "sources": sources,
                        "source_params": source_params
                    }
                    
                    # Debug: For Series Step input, verify we got the right source
                    if instance_guid == "b785e424-ebb1-42fc-ac03-dee2d7d764b4" and (param_index == "1" or param_index == 1) and param_name == "param_input":
                        expected_source = "20f5465a-8288-49ad-acd1-2eb24e1f8765"
                        actual_source = sources[0]["guid"] if sources else None
                        if actual_source != expected_source:
                            print(f"ERROR: Series Step input has wrong source!")
                            print(f"  Expected: {expected_source}")
                            print(f"  Actual: {actual_source}")
                            print(f"  Param InstanceGuid: {param_instance_guid}")
                            # Try to re-read from XML to verify
                            items_elem_check = param_chunk.find("./items")
                            if items_elem_check is not None:
                                source_items_check = items_elem_check.findall("./item[@name='Source']")
                                print(f"  XML Source items: {[item.text for item in source_items_check]}")
            
            # Track processing
            processed_count += 1
            
            # Store object - use InstanceGuid as primary key if available, otherwise use Object GUID
            # Skip Scribble objects (they're just labels)
            if not obj_guid:
                skipped_no_guid += 1
            elif obj_type == "Scribble" or obj_name == "Scribble":
                skipped_scribble += 1
            elif obj_guid and obj_type != "Scribble" and obj_name != "Scribble":
                # Use InstanceGuid as key if available (unique per instance)
                # Otherwise use Object GUID (shared by component type)
                key = instance_guid if instance_guid else obj_guid
                
                if key in objects:
                    # Update existing object if we have more complete data
                    if instance_guid and not objects[key].get("instance_guid"):
                        objects[key]["instance_guid"] = instance_guid
                    if not objects[key].get("guid") and obj_guid:
                        objects[key]["guid"] = obj_guid
                    if not objects[key].get("type") and obj_type:
                        objects[key]["type"] = obj_type
                    if not objects[key].get("nickname") and obj_nickname:
                        objects[key]["nickname"] = obj_nickname
                    # Merge params
                    objects[key]["params"].update(params)
                else:
                    objects[key] = {
                        "guid": obj_guid,
                        "name": obj_name,
                        "type": obj_type,
                        "nickname": obj_nickname,
                        "instance_guid": instance_guid,
                        "params": params
                    }
                    stored_count += 1
                
                # Special handling for Point On Curve: extract Container-level Source and parameter
                if obj_type == "Point On Curve" and container is not None:
                    container_items_elem = container.find("./items")
                    if container_items_elem is not None:
                        # Extract Source (can be multiple with index)
                        sources = []
                        for item in container_items_elem.findall("./item[@name='Source']"):
                            source_index = item.get("index")
                            source_guid = item.text
                            if source_guid:
                                sources.append({
                                    "guid": source_guid,
                                    "index": int(source_index) if source_index else None
                                })
                        
                        # Extract parameter value
                        parameter_item = container_items_elem.find("./item[@name='parameter']")
                        parameter_value = None
                        if parameter_item is not None:
                            try:
                                parameter_value = float(parameter_item.text) if parameter_item.text else None
                            except (ValueError, TypeError):
                                pass
                        
                        # Store in params as special entries (ensure params dict exists)
                        # Store as dict with 'sources' key to match param structure
                        if sources:
                            objects[key]["params"]["_container_source"] = {
                                "sources": sources,
                                "type": "container_source"
                            }
                        if parameter_value is not None:
                            objects[key]["params"]["_container_parameter"] = {
                                "value": parameter_value,
                                "type": "container_parameter"
                            }
        
        print(f"  Processed {processed_count} object chunks")
        print(f"  Stored {stored_count} objects")
        print(f"  Skipped: {skipped_no_guid} without GUID, {skipped_scribble} Scribble")
        print(f"  Total objects dict size: {len(objects)}")
        
        # Debug: check why we're only storing 42
        scribble_count = 0
        no_container_count = 0
        for obj_chunk in obj_chunks:
            items_elem = obj_chunk.find("./items")
            obj_guid = None
            obj_name = None
            if items_elem is not None:
                for item in items_elem:
                    if item.tag == "item":
                        name = item.get("name")
                        if name == "GUID":
                            obj_guid = item.text
                        elif name == "Name":
                            obj_name = item.text
            if obj_guid:
                if obj_name == "Scribble":
                    scribble_count += 1
                elif obj_guid not in objects:
                    # Check if it has a container
                    container = obj_chunk.find(".//chunk[@name='Container']")
                    if container is None:
                        no_container_count += 1
        print(f"  Debug: {scribble_count} Scribble objects skipped, {no_container_count} objects without Container not stored")
    
    # Extract groups - they are also Objects with type "Group"
    groups = {}
    for guid, obj in objects.items():
        if obj["type"] == "Group":
            # Extract member GUIDs from ID items
            member_guids = []
            # Need to find the Container chunk for this group object
            # Groups store member IDs in a special way
            # Let's search for the group object in the XML directly
            pass
    
    # Find groups by searching for Group objects
    # Groups are stored as Objects with type "Group"
    # For each group, we need to find its member GUIDs from the Container chunk
    if def_objects is not None:
        for obj_chunk in obj_chunks:  # Reuse the same obj_chunks list
            obj_guid = None
            instance_guid = None
            # Get GUID from direct items of Object chunk, not nested
            items_chunk = obj_chunk.find("./items")
            if items_chunk is not None:
                for item in items_chunk.findall("./item[@name='GUID']"):
                    obj_guid = item.text
                    break
            
            if not obj_guid:
                continue
                
            container = obj_chunk.find(".//chunk[@name='Container']")
            if container is not None:
                # Check if this is a Group
                name_item = container.find(".//item[@name='Name']")
                if name_item is not None and name_item.text == "Group":
                    nickname_item = container.find(".//item[@name='NickName']")
                    if nickname_item is not None:
                        nickname = nickname_item.text
                        # Get InstanceGuid as unique identifier
                        for item in container.findall(".//item[@name='InstanceGuid']"):
                            instance_guid = item.text
                            break
                        # Extract member GUIDs from ID items
                        member_guids = []
                        for item in container.findall(".//item[@name='ID']"):
                            member_guids.append(item.text)
                        
                        # Use InstanceGuid as key if available, otherwise use GUID
                        key = instance_guid if instance_guid else obj_guid
                        if key and nickname:
                            groups[key] = {
                                "guid": obj_guid,
                                "instance_guid": instance_guid,
                                "nickname": nickname,
                                "member_guids": set(member_guids)
                            }
                            print(f"Added group to dict: {nickname} (key: {key[:8]}..., GUID: {obj_guid[:8]}...)")
                            # Also update the object entry
                            if obj_guid in objects:
                                objects[obj_guid]["type"] = "Group"
    
    print(f"\nGroups dictionary now has {len(groups)} entries after loop")
    if len(groups) > 0:
        print("Sample group GUIDs in dict:")
        for gid, ginfo in list(groups.items())[:3]:
            print(f"  {gid[:8]}... -> {ginfo['nickname']}")
    
    # Build reverse connection map (target -> sources)
    connections = []
    for guid, obj in objects.items():
        for param_key, param_info in obj.get("params", {}).items():
            # Skip special entries that are not dicts
            if not isinstance(param_info, dict):
                continue
            for i, source in enumerate(param_info.get("sources", [])):
                source_param = param_info.get("source_params", [None] * len(param_info.get("sources", [])))[i] if param_info.get("source_params") else None
                connections.append({
                    "source": source["guid"],
                    "source_param": source_param,
                    "target": guid,
                    "target_param": param_key
                })
    
    return {
        "groups": groups,
        "objects": objects,
        "connections": connections
    }

def find_rotatingslats_group(data: Dict) -> Tuple[Optional[str], Optional[Dict]]:
    """Find the Rotatingslats group."""
    print(f"Searching for Rotatingslats in {len(data['groups'])} groups...")
    for group_id, group_info in data["groups"].items():
        print(f"  Checking: '{group_info['nickname']}'")
        if group_info["nickname"] == "Rotatingslats":
            print(f"  Found it! GUID: {group_id}")
            return group_id, group_info
    print("  Not found!")
    return None, None

def extract_rotatingslats_subgraph(data: Dict, group_id: str, group_info: Dict):
    """Extract the full subgraph for Rotatingslats including external inputs."""
    member_guids = group_info["member_guids"]
    
    # Group member GUIDs are InstanceGUIDs
    # Our objects dict now uses InstanceGuid as key (or Object GUID as fallback)
    # Build maps for matching
    instance_to_key = {}  # InstanceGuid -> dict key
    guid_to_key = {}      # Object GUID -> dict key (for objects without InstanceGuid)
    objects_with_instance = 0
    
    for key, obj in data["objects"].items():
        # The key might be InstanceGuid or Object GUID
        if obj.get("instance_guid"):
            instance_to_key[obj["instance_guid"]] = key
            objects_with_instance += 1
        if obj.get("guid"):
            # Object GUID can map to multiple keys (same component type, different instances)
            # Store as list to handle multiple instances
            if obj["guid"] not in guid_to_key:
                guid_to_key[obj["guid"]] = []
            if key not in guid_to_key[obj["guid"]]:  # Avoid duplicates
                guid_to_key[obj["guid"]].append(key)
    
    print(f"  Objects with InstanceGUID: {objects_with_instance} / {len(data['objects'])}")
    print(f"  InstanceGUID map size: {len(instance_to_key)}")
    
    # Find all objects in the group by matching InstanceGUIDs (group members are InstanceGUIDs)
    # But some might be Object GUIDs (component type) - need to handle both
    group_object_keys = set()
    matched_by_instance = 0
    matched_by_guid = 0
    matched_by_guid_multiple = 0
    for member_guid in member_guids:
        # Try as InstanceGuid first (this is what group members should be)
        if member_guid in instance_to_key:
            group_object_keys.add(instance_to_key[member_guid])
            matched_by_instance += 1
        # Try as Object GUID (fallback - if group lists component type instead of instance)
        elif member_guid in guid_to_key:
            # Object GUID can map to multiple instances - add all of them
            for key in guid_to_key[member_guid]:
                group_object_keys.add(key)
            matched_by_guid += 1
            if len(guid_to_key[member_guid]) > 1:
                matched_by_guid_multiple += len(guid_to_key[member_guid])
    
    print(f"  Member GUIDs matched to objects: {len(group_object_keys)} / {len(member_guids)}")
    print(f"    Matched by InstanceGUID: {matched_by_instance}, by Object GUID: {matched_by_guid} ({matched_by_guid_multiple} instances)")
    
    # Find all objects in the group
    group_objects = {key: data["objects"][key] for key in group_object_keys if key in data["objects"]}
    
    # Debug: show missing GUIDs
    matched = set()
    for mg in member_guids:
        if mg in instance_to_key or mg in guid_to_key:
            matched.add(mg)
    missing = member_guids - matched
    
    # Analyze missing GUIDs - check what types of objects they are
    if missing:
        print(f"  Missing {len(missing)} GUIDs. First 5: {list(missing)[:5]}")
        # Check if any missing GUIDs exist as InstanceGUIDs in the file
        import xml.etree.ElementTree as ET
        tree = ET.parse("core-only_fixed.ghx")
        missing_found = []
        for mg in list(missing)[:5]:
            # Use a simpler approach - find all InstanceGuid items and check their text
            for item in tree.findall(".//item[@name='InstanceGuid']"):
                if item.text == mg:
                    missing_found.append(mg)
                    break
        if missing_found:
            print(f"  Found {len(missing_found)} missing GUIDs as InstanceGUIDs in XML (extraction issue)")
    
    # Find external inputs (connections from outside the group)
    external_inputs = set()
    internal_connections = []
    
    # Build set of group object keys for connection checking
    group_object_keys_set = set(group_object_keys)
    
    for conn in data["connections"]:
        # Connections use InstanceGUIDs or Object GUIDs - need to map them to our object keys
        source_key = instance_to_key.get(conn["source"]) or guid_to_key.get(conn["source"])
        target_key = instance_to_key.get(conn["target"]) or guid_to_key.get(conn["target"])
        
        source_in_group = source_key in group_object_keys_set if source_key else False
        target_in_group = target_key in group_object_keys_set if target_key else False
        
        if source_in_group and target_in_group:
            internal_connections.append(conn)
        elif not source_in_group and target_in_group:
            # External input
            external_inputs.add(conn["source"])
            internal_connections.append(conn)
    
    # Include external input objects
    external_objects = {guid: data["objects"][guid] for guid in external_inputs if guid in data["objects"]}
    
    return {
        "group_id": group_id,
        "group_objects": group_objects,
        "external_objects": external_objects,
        "connections": internal_connections,
        "all_guids": member_guids | external_inputs
    }

if __name__ == "__main__":
    import sys
    # Use command line argument if provided, otherwise default to core-only_trimmed2.ghx
    ghx_file = sys.argv[1] if len(sys.argv) > 1 else "core-only_trimmed2.ghx"
    print(f"Parsing GHX file: {ghx_file}")
    data = parse_ghx(ghx_file)
    
    print(f"\nSummary:")
    print(f"  Found {len(data['groups'])} groups")
    print(f"  Found {len(data['objects'])} objects")
    print(f"  Found {len(data['connections'])} connections")
    
    # Debug: print all group nicknames
    print(f"\nAll groups found:")
    for gid, ginfo in data["groups"].items():
        print(f"  - {ginfo['nickname']} ({len(ginfo['member_guids'])} members)")
    
    # Find Rotatingslats group
    # Extract ALL components from the GHX, ignoring groups
    print(f"\nExtracting ALL components from GHX (ignoring groups)...")
    print(f"  Total objects: {len(data['objects'])}")
    
    # Use all objects as group_objects, no external_objects needed
    all_objects = data["objects"]
    all_connections = data["connections"]
    
    # Build all_guids set from all objects
    all_guids = set()
    for key, obj in all_objects.items():
        all_guids.add(key)
        if obj.get("instance_guid"):
            all_guids.add(obj["instance_guid"])
        if obj.get("guid"):
            all_guids.add(obj["guid"])
        # Also add parameter GUIDs
        for param_key, param_info in obj.get("params", {}).items():
            param_guid = param_info.get("data", {}).get("InstanceGuid")
            if param_guid:
                all_guids.add(param_guid)
    
    print(f"  Extracted {len(all_objects)} components")
    print(f"  Total connections: {len(all_connections)}")
    
    # Print some sample objects
    print("\nSample components:")
    for i, (guid, obj) in enumerate(list(all_objects.items())[:10]):
        print(f"  {i+1}. {obj.get('nickname', obj.get('name', 'Unknown'))} ({obj.get('type', 'Unknown')}) - {guid[:8]}...")
    
    # Save to JSON for inspection
    with open("rotatingslats_data.json", "w") as f:
        # Convert sets to lists for JSON
        json_data = {
            "group_id": None,  # No group filtering
            "group_objects": {k: {
                **v, 
                "params": {pk: {
                    **pv, 
                    "sources": pv.get("sources", [])
                } for pk, pv in v["params"].items()}
            } for k, v in all_objects.items()},
            "external_objects": {},  # No external objects when using all components
            "connections": all_connections,
            "all_guids": list(all_guids)
        }
        json.dump(json_data, f, indent=2, default=str)
    print("\nSaved to rotatingslats_data.json")

