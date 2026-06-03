import os
import json
import pyproj
import sys

# Reconfigure stdout to use utf-8 to avoid console encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Projection definitions
# Central meridian for Trà Vinh is 105.5 (105 degrees 30 minutes)
proj_vn2000 = pyproj.Proj("+proj=tmerc +lat_0=0 +lon_0=105.5 +k=0.9999 +x_0=500000 +y_0=0 +ellps=krass +towgs84=-191.9,-39.3,-111.5,-0.009288,0.019754,-0.004273,0.252906278 +units=m +no_defs")
proj_wgs84 = pyproj.Proj("+proj=latlong +datum=WGS84 +no_defs")
transformer = pyproj.Transformer.from_proj(proj_vn2000, proj_wgs84, always_xy=True)

def convert_coords(coords):
    # Recurse until we find [x, y]
    if isinstance(coords[0], (int, float)):
        x, y = coords[0], coords[1]
        # Check if coordinates are in VN-2000 (usually x ~ 500000-600000, y ~ 1000000-1100000)
        if x > 180 or y > 90 or x < -180 or y < -90:
            lng, lat = transformer.transform(x, y)
            return [lng, lat]
        else:
            return [x, y]
            
    return [convert_coords(c) for c in coords]

def process_file(filepath):
    print(f"Processing {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    modified = False
    for feature in data.get("features", []):
        geom = feature.get("geometry")
        if not geom:
            continue
            
        coords = geom.get("coordinates")
        if not coords:
            continue
            
        new_coords = convert_coords(coords)
        if new_coords != coords:
            geom["coordinates"] = new_coords
            modified = True
            
    if modified:
        # Also update crs to standard WGS84
        data["crs"] = {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            }
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Converted and saved {filepath} to WGS84.")
    else:
        print(f"File {filepath} was already in WGS84.")

def main():
    map_dir = "map data"
    for filename in os.listdir(map_dir):
        if filename.endswith(".geojson"):
            filepath = os.path.join(map_dir, filename)
            process_file(filepath)

if __name__ == "__main__":
    main()
