import os
import json
import sys

# Ensure UTF-8 output for Vietnamese characters
sys.stdout.reconfigure(encoding='utf-8')

centers = {
    "Ấp 1": [9.87591, 106.05837],
    "Ấp 2": [9.86528, 106.06498],
    "Ấp Trà Kháo": [9.88626, 106.08059],
    "Ấp Bà My": [9.89267, 106.05308],
    "Ấp Giồng Lớn": [9.87799, 106.06998],
    "Ấp Thông Thảo": [9.90806, 106.08577],
    "Ấp Giồng Dầu": [9.91009, 106.07013],
    "Ấp Rùm Sóc": [9.83196, 106.06385],
    "Ấp Ô Mịch": [9.84556, 106.06685],
    "Ấp Ô Tưng": [9.86507, 106.08031],
    "Ấp Châu Hưng": [9.89199, 106.10055],
    "Ấp Ô Rồm": [9.86559, 106.11447],
    "Ấp Xóm Lớn": [9.88916, 106.12291]
}

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

map_data_dir = r"d:\4. code\xa_cau_ke\map data"
print("Checking centers against GeoJSON boundaries:")
for hamlet, latlng in centers.items():
    file_path = os.path.join(map_data_dir, f"{hamlet}.geojson")
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        continue
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    point = [latlng[1], latlng[0]]
    inside = is_point_in_geojson(point, data)
    print(f" - {hamlet}: Point {latlng} inside? {inside}")
