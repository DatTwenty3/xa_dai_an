import os
import json
import math
import sys

sys.stdout.reconfigure(encoding='utf-8')

def point_to_segment_dist(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    
    tx = x1 + t * dx
    ty = y1 + t * dy
    return math.hypot(px - tx, py - ty)

def ray_casting(px, py, poly):
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if py > min(p1y, p2y):
            if py <= max(p1y, p2y):
                if px <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (py - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or px <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def get_distance_to_boundary(px, py, geom_coords, gtype):
    # Calculate minimum distance to any boundary segment
    min_dist = float('inf')
    
    def process_polygon_coords(poly_coords):
        nonlocal min_dist
        # poly_coords is a list of rings, index 0 is outer ring
        outer_ring = poly_coords[0]
        for i in range(len(outer_ring) - 1):
            p1 = outer_ring[i]
            p2 = outer_ring[i+1]
            d = point_to_segment_dist(px, py, p1[0], p1[1], p2[0], p2[1])
            if d < min_dist:
                min_dist = d
        # handle inner rings (holes) if present
        for ring in poly_coords[1:]:
            for i in range(len(ring) - 1):
                p1 = ring[i]
                p2 = ring[i+1]
                d = point_to_segment_dist(px, py, p1[0], p1[1], p2[0], p2[1])
                if d < min_dist:
                    min_dist = d

    if gtype == "Polygon":
        process_polygon_coords(geom_coords)
    elif gtype == "MultiPolygon":
        for poly_coords in geom_coords:
            process_polygon_coords(poly_coords)
            
    return min_dist

def is_point_inside(px, py, geom_coords, gtype):
    if gtype == "Polygon":
        return ray_casting(px, py, geom_coords[0])
    elif gtype == "MultiPolygon":
        for poly_coords in geom_coords:
            if ray_casting(px, py, poly_coords[0]):
                return True
    return False

def get_polygon_bbox(geom_coords, gtype):
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = float('-inf'), float('-inf')
    
    def update_bbox(ring):
        nonlocal min_x, min_y, max_x, max_y
        for x, y in ring:
            if x < min_x: min_x = x
            if x > max_x: max_x = x
            if y < min_y: min_y = y
            if y > max_y: max_y = y
            
    if gtype == "Polygon":
        for ring in geom_coords:
            update_bbox(ring)
    elif gtype == "MultiPolygon":
        for poly_coords in geom_coords:
            for ring in poly_coords:
                update_bbox(ring)
                
    return min_x, min_y, max_x, max_y

def find_visual_center(geojson_path):
    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    features = data.get("features", [])
    if not features:
        return None
        
    feature = features[0]
    geom = feature.get("geometry", {})
    gtype = geom.get("type")
    coords = geom.get("coordinates", [])
    
    if gtype not in ["Polygon", "MultiPolygon"]:
        return None
        
    min_x, min_y, max_x, max_y = get_polygon_bbox(coords, gtype)
    
    # Run a grid search
    best_pt = None
    best_dist = -1
    
    # Try different grid resolutions
    for grid_size in [40, 80, 120]:
        step_x = (max_x - min_x) / grid_size
        step_y = (max_y - min_y) / grid_size
        
        for i in range(grid_size + 1):
            px = min_x + i * step_x
            for j in range(grid_size + 1):
                py = min_y + j * step_y
                
                if is_point_inside(px, py, coords, gtype):
                    dist = get_distance_to_boundary(px, py, coords, gtype)
                    if dist > best_dist:
                        best_dist = dist
                        best_pt = [py, px] # [lat, lng]
                        
        # If we found a point with a positive distance, we can stop or keep refining
        if best_pt is not None and best_dist > 0.0001:
            break
            
    # Fallback to centroid if no point found inside (e.g. extremely weird polygon)
    if best_pt is None:
        total_lat = 0.0
        total_lng = 0.0
        count = 0
        def sum_coords(ring):
            nonlocal total_lat, total_lng, count
            for x, y in ring:
                total_lat += y
                total_lng += x
                count += 1
        if gtype == "Polygon":
            sum_coords(coords[0])
        elif gtype == "MultiPolygon":
            for poly in coords:
                sum_coords(poly[0])
        if count > 0:
            best_pt = [total_lat / count, total_lng / count]
            
    return best_pt, best_dist

# Test on all 7 hamlets
map_data_dir = "map data"
hamlet_files = sorted([f for f in os.listdir(map_data_dir) if f.endswith(".geojson")])

overrides = {}
for filename in hamlet_files:
    name = os.path.splitext(filename)[0]
    filepath = os.path.join(map_data_dir, filename)
    center, dist = find_visual_center(filepath)
    overrides[name] = center
    print(f'"{name}": {center}, # distance to boundary: {dist:.6f}')
