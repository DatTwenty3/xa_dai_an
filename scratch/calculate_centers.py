import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def get_centroid(geojson_path):
    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    features = data.get("features", [])
    if not features:
        return None
        
    geom = features[0].get("geometry", {})
    coords = geom.get("coordinates", [])
    gtype = geom.get("type")
    
    if gtype == "Polygon":
        poly = coords[0]
    elif gtype == "MultiPolygon":
        poly = coords[0][0]
    else:
        return None
        
    lats = [pt[1] for pt in poly]
    lngs = [pt[0] for pt in poly]
    
    avg_lat = sum(lats) / len(lats)
    avg_lng = sum(lngs) / len(lngs)
    
    return [avg_lat, avg_lng]

map_data_dir = r"d:\4. code\xa_cau_ke\map data"
for name in ["Ấp Thông Thảo", "Ấp Giồng Dầu"]:
    file_path = os.path.join(map_data_dir, f"{name}.geojson")
    if os.path.exists(file_path):
        centroid = get_centroid(file_path)
        print(f"{name} centroid: {centroid}")
