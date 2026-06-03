import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def ray_casting(point, poly):
    x, y = point
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def is_point_in_geojson(point, geojson):
    features = geojson.get("features", [])
    for feature in features:
        geom = feature.get("geometry", {})
        gtype = geom.get("type")
        coords = geom.get("coordinates", [])
        if gtype == "Polygon":
            if ray_casting(point, coords[0]):
                return True
        elif gtype == "MultiPolygon":
            for poly in coords:
                if ray_casting(point, poly[0]):
                    return True
    return False

# Load compiled config centers
config_path = "map data/compiled-config.json"
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

for hamlet in config["hamlets"]:
    name = hamlet["name"]
    center = hamlet["center"] # [lat, lng]
    geojson_path = f"map data/{name}.geojson"
    if not os.path.exists(geojson_path):
        print(f"{name}: GeoJSON file not found at {geojson_path}")
        continue
    with open(geojson_path, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)
    
    # Point is [lng, lat] for ray casting
    point = [center[1], center[0]]
    inside = is_point_in_geojson(point, geojson_data)
    print(f"Hamlet: {name}")
    print(f"  Center: {center}")
    print(f"  Is center inside boundary? {inside}")
