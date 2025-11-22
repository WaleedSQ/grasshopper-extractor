"""Check Number of slats slider value"""
import json

with open('rotatingslats_inputs.json') as f:
    inputs = json.load(f)

slider_guid = "537142d8-e672-4d12-8254-46dbe1e3c7ef"

if slider_guid in inputs:
    slider = inputs[slider_guid]
    print(f"Number of slats slider:")
    print(f"  Value: {slider['data']}")
else:
    print(f"Slider {slider_guid[:8]}... NOT found in external inputs")
    print(f"\nThis slider is likely inside the Rotatingslats group")
    print(f"but our isolation considers it external")

