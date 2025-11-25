# Enhanced Evaluation Results Format

## Overview
The evaluation results now include component metadata (type, nickname, position) to make it easier to identify which component each result belongs to.

## New Structure

### Before (Old Format):
```json
{
  "577ce3f3-2b5e-4a55-ae60-c5c3c6c12e3c": {
    "Point": {
      "branches": {
        "(0,)": [[0, -2, 7]]
      },
      "branch_count": 1,
      "item_count": 1
    }
  }
}
```

### After (Enhanced Format): ✅
```json
{
  "577ce3f3-2b5e-4a55-ae60-c5c3c6c12e3c": {
    "component_info": {
      "guid": "577ce3f3-2b5e-4a55-ae60-c5c3c6c12e3c",
      "type": "Construct Point",
      "nickname": "p1",
      "position": {
        "x": 10672.0,
        "y": 2894.0
      }
    },
    "outputs": {
      "Point": {
        "branches": {
          "(0,)": [[0, -2, 7]]
        },
        "branch_count": 1,
        "item_count": 1
      }
    }
  }
}
```

## Benefits

✅ **Easy Identification**: See component type and nickname at a glance  
✅ **Spatial Context**: Know where component is located (x, y position)  
✅ **Better Debugging**: Quickly identify which component has issues  
✅ **Documentation**: Results file is self-documenting  
✅ **Automatic**: Generated automatically by evaluator  

## Component Info Fields

| Field | Description | Example |
|-------|-------------|---------|
| `guid` | Unique component identifier | `"577ce3f3-2b5e-4a55-ae60-c5c3c6c12e3c"` |
| `type` | Component type name | `"Construct Point"` |
| `nickname` | Component nickname in Grasshopper | `"p1"` |
| `position.x` | X coordinate in canvas | `10672.0` |
| `position.y` | Y coordinate in canvas | `2894.0` |

## Example Components

### Construct Point
```json
{
  "component_info": {
    "type": "Construct Point",
    "nickname": "Construct Point",
    "position": {"x": 10368.0, "y": 2981.0}
  },
  "outputs": {
    "Point": {
      "branches": {"(0,)": [[0, 4.5, 4.0]]},
      "item_count": 1
    }
  }
}
```

### Vector 2Pt
```json
{
  "component_info": {
    "type": "Vector 2Pt",
    "nickname": "Vector 2Pt",
    "position": {"x": 10838.0, "y": 2782.0}
  },
  "outputs": {
    "Vector": {
      "branches": {"(0,)": [[0.0, 0.07, -3.7]]},
      "item_count": 1
    }
  }
}
```

### Move Component
```json
{
  "component_info": {
    "type": "Move",
    "nickname": "Slats original",
    "position": {"x": 11109.0, "y": 2822.0}
  },
  "outputs": {
    "Geometry": {
      "branches": {
        "(0,)": [
          {"corners": [[0, 0.07, 3.8], ...], "plane": ""}
        ]
      },
      "item_count": 1
    }
  }
}
```

## Usage Tips

### Finding Components by Nickname
```python
import json

with open('rotatingslats_evaluation_results.json', 'r') as f:
    results = json.load(f)

# Find all "Move" components
moves = {guid: data for guid, data in results.items() 
         if data['component_info']['type'] == 'Move'}

# Find by nickname
vector = next(data for guid, data in results.items() 
              if data['component_info']['nickname'] == 'Vector 2Pt')
```

### Sorting by Position
```python
# Sort by Y position (top to bottom)
sorted_components = sorted(
    results.items(),
    key=lambda x: x[1]['component_info']['position']['y']
)
```

### Quick Summary
```python
for guid, data in results.items():
    info = data['component_info']
    print(f"{info['type']}: {info['nickname']} - "
          f"{len(data['outputs'])} output(s)")
```

## File Updates

✅ **`rotatingslats_evaluation_results.json`** - Now includes component metadata  
✅ **`gh_evaluator_wired.py`** - Automatically generates enhanced format  
✅ **All 56 components** - Have complete metadata  

---

*Enhanced Format Added: November 22, 2025*  
*Status: Active ✅*

