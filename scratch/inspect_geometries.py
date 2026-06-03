import os
import json
import sys

# Reconfigure stdout to use utf-8 to avoid console encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

map_dir = "map data"
for filename in os.listdir(map_dir):
    if filename.endswith(".geojson"):
        filepath = os.path.join(map_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        features = data.get("features", [])
        print(f"File: {filename}")
        print(f"  Number of features: {len(features)}")
        for idx, feat in enumerate(features):
            geom = feat.get("geometry", {})
            gtype = geom.get("type")
            props = feat.get("properties", {})
            # Sample coords size
            coords = geom.get("coordinates", [])
            print(f"    Feature {idx}: Type={gtype}, Properties={list(props.keys())}, Coordinate structures: {len(coords)}")
