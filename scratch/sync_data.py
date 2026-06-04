import os
import json
import re
import math
import sys

# Reconfigure stdout to use utf-8 to avoid console encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Curated list of high-contrast beautiful colors for hamlets
PALETTE = [
    "#ff4d4d",  # Neon Coral Red
    "#ff9f0a",  # Neon Gold
    "#30d158",  # Bright Lime Green
    "#0a84ff",  # Vibrant Blue
    "#5e5ce6",  # Electric Indigo
    "#bf5af2",  # Electric Purple
    "#ff375f",  # Vivid Rose Pink
    "#64d2ff",  # Bright Sky Blue
    "#ffd60a",  # Vibrant Yellow
    "#00e5ff",  # Radiant Cyan
    "#a78bfa",  # Soft Lavender
    "#34d399",  # Vibrant Emerald Green
    "#f43f5e",  # Vibrant Pink-Red
    "#fa97d8",  # Bright Pink
    "#e28743",  # Copper Orange
    "#76b5c5"   # Pastel Teal
]

def clean_value(val):
    if val is None:
        return ""
    return str(val).strip()

def parse_float(val, default=0.0):
    try:
        return float(str(val).replace(",", "."))
    except (TypeError, ValueError):
        return default

def parse_int(val, default=0):
    try:
        return int(float(str(val).replace(",", ".")))
    except (TypeError, ValueError):
        return default

def flatten_coordinates(coords):
    """Recursively flattens coordinates list into list of [lng, lat] pairs."""
    if not coords:
        return []
    if isinstance(coords[0], (int, float)):
        return [coords]
    
    flat = []
    # If the first element is a list, check its elements
    if isinstance(coords[0], list):
        if len(coords[0]) > 0 and isinstance(coords[0][0], (int, float)):
            # This is a list of [lng, lat] pairs
            return coords
        else:
            # Nested list, recurse
            for sub in coords:
                flat.extend(flatten_coordinates(sub))
    return flat

def calculate_geojson_center(data):
    """Calculates the geometric centroid of all coordinates across all features in a geojson dict."""
    features = data.get("features", [])
    total_lat = 0.0
    total_lng = 0.0
    count = 0
    
    for feat in features:
        geom = feat.get("geometry", {})
        coords = geom.get("coordinates", [])
        flat_coords = flatten_coordinates(coords)
        for lng, lat in flat_coords:
            total_lat += lat
            total_lng += lng
            count += 1
            
    if count == 0:
        return None
    return [total_lat / count, total_lng / count]

def calculate_polygon_center(geometry):
    """Calculates the geometric centroid of a geometry object."""
    coords = geometry.get("coordinates", [])
    flat_coords = flatten_coordinates(coords)
    total_lat = 0.0
    total_lng = 0.0
    count = 0
    for lng, lat in flat_coords:
        total_lat += lat
        total_lng += lng
        count += 1
    if count == 0:
        return None
    return [total_lat / count, total_lng / count]

def main():
    print("=== STARTING DATA SYNCHRONIZATION ===")
    
    # 1. Load config
    config_path = "commune-config.json"
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found!")
        sys.exit(1)
        
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    commune_name = config.get("commune_name", "Cầu Kè")
    province_name = config.get("province_name", "Vĩnh Long")
    year = config.get("year", "2026")
    month = config.get("month", "5")
    company_name = config.get("company_name", "CÔNG TY ÂU LẠC")
    default_zoom = config.get("default_zoom", 13)
    
    print(f"Commune: {commune_name}, Province: {province_name}")
    
    # 2. Scan map data for new hamlets
    geojson_dir = "map data"
    if not os.path.exists(geojson_dir):
        print(f"Error: Directory '{geojson_dir}' not found!")
        sys.exit(1)
        
    new_hamlet_files = sorted([f for f in os.listdir(geojson_dir) if f.endswith(".geojson")])
    print(f"Found {len(new_hamlet_files)} hamlet GeoJSON file(s) in '{geojson_dir}'")
    
    hamlets_list = []
    merged_sources_map = {}
    
    total_area_ha = 0.0
    total_pop = 0
    total_households = 0
    
    all_latitudes = []
    all_longitudes = []
    
    for idx, filename in enumerate(new_hamlet_files):
        filepath = os.path.join(geojson_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        features = data.get("features", [])
        if not features:
            print(f"  Warning: No features in {filename}, skipping.")
            continue
            
        # Get first feature properties as representative properties
        feature = features[0]
        props = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        
        # Determine name: 'ten' prop first, then file name without extension
        name = props.get("ten") or os.path.splitext(filename)[0]
        code = props.get("ma") or props.get("id") or f"ap_{idx+1}"
        
        # Safe statistics parser
        area_ha = parse_float(props.get("dien_tich_ha") or props.get("dien_tich_sau_sap_nhap_ha") or 0.0)
        pop = parse_int(props.get("dan_so") or props.get("so_dan_sau_sap_nhap") or 0)
        households = parse_int(props.get("so_ho") or props.get("so_ho_sau_sap_nhap") or 0)
        sap_nhap_tu = props.get("sap_nhap_tu") or [name]
        if not isinstance(sap_nhap_tu, list):
            sap_nhap_tu = [clean_value(sap_nhap_tu)]
            
        # Sum statistics
        total_area_ha += area_ha
        total_pop += pop
        total_households += households
        
        # Calculate centroid center (use properties override if available)
        center = props.get("center") or props.get("label_center")
        if center:
            print(f"  Using custom center override for {name}: {center}")
        else:
            center = calculate_geojson_center(data)
            
        if not center:
            # Fallback to general center if centroid calculation failed
            center = [9.914, 106.08]
            print(f"  Warning: Could not calculate center for {name}, using default center.")
        
        all_latitudes.append(center[0])
        all_longitudes.append(center[1])
            
        # Select color from palette
        color = PALETTE[idx % len(PALETTE)]
        
        # Build properties structure matching application requirements
        compiled_props = {
            "ten": name,
            "ma": str(code),
            "loai": props.get("loai") or "Ấp",
            "dien_tich_ha": str(area_ha),
            "dien_tich_km2": f"{(area_ha / 100.0):.4f}",
            "dan_so": str(pop),
            "so_ho": str(households),
            "mat_do_km2": f"{(pop / (area_ha / 100.0)):.2f}" if area_ha > 0 else "0",
            "sap_nhap_tu": sap_nhap_tu
        }
        
        hamlets_list.append({
            "name": name,
            "ma": str(code),
            "file": filename,
            "center": center,
            "color": color,
            "properties": compiled_props
        })
        
        merged_sources_map[name] = sap_nhap_tu
        print(f"  Processed hamlet: {name} (Code: {code}, Center: {center}, Color: {color})")

    # 3. Scan old hamlet boundaries in ranh gioi ap cu
    old_hamlet_dir = os.path.join(geojson_dir, "ranh gioi ap cu")
    old_hamlets_list = []
    old_hamlet_centers = {}
    
    if os.path.exists(old_hamlet_dir):
        old_files = sorted([f for f in os.listdir(old_hamlet_dir) if f.endswith(".geojson")])
        print(f"Found {len(old_files)} old boundary GeoJSON file(s) in '{old_hamlet_dir}'")
        for filename in old_files:
            filepath = os.path.join(old_hamlet_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            features = data.get("features", [])
            if not features:
                continue
                
            geometry = features[0].get("geometry", {})
            name = os.path.splitext(filename)[0]
            center = calculate_polygon_center(geometry)
            
            if center:
                old_hamlets_list.append({
                    "name": name,
                    "file": filename,
                    "center": center
                })
                old_hamlet_centers[name] = center
                print(f"  Processed old boundary: {name} (Center: {center})")
    else:
        print("  Info: Directory 'ranh gioi ap cu' does not exist, skipping old hamlet boundaries.")
        
    # 4. Handle manual old hamlets that don't have geojson files (Auto-offsets around new hamlet center)
    manual_old_hamlets = []
    # Identify all source hamlets mentioned that do not have their own boundary files
    for hamlet in hamlets_list:
        new_center = hamlet["center"]
        sources = hamlet["properties"]["sap_nhap_tu"]
        # If it is a merged hamlet
        if len(sources) > 1 or (len(sources) == 1 and sources[0] != hamlet["name"]):
            # Distribute old hamlets around new hamlet center in a small circle to avoid overlapping labels
            angle_step = 2 * math.pi / len(sources)
            for s_idx, source_name in enumerate(sources):
                # If we already have a boundary center for this old hamlet, use it
                if source_name in old_hamlet_centers:
                    continue
                # Calculate small offset (radius of ~0.003 degrees, approx 300m)
                angle = s_idx * angle_step
                offset_lat = new_center[0] + 0.0025 * math.sin(angle)
                offset_lng = new_center[1] + 0.0025 * math.cos(angle)
                
                manual_old_hamlets.append({
                    "name": source_name,
                    "coords": [offset_lat, offset_lng]
                })
                print(f"  Distributed manual old label: {source_name} (Center offset around {hamlet['name']}: {[offset_lat, offset_lng]})")

    # 5. Calculate global commune properties
    total_area_km2 = round(total_area_ha / 100.0, 2)
    density = round(total_pop / total_area_km2, 2) if total_area_km2 > 0 else 0.0
    
    commune_properties = {
        "ten": commune_name,
        "loai": "Xã",
        "cap": "2",
        "dien_tich_km2": str(total_area_km2),
        "dan_so": str(total_pop),
        "so_ho": str(total_households),
        "mat_do_km2": str(density)
    }
    
    # 6. Map default center (Average of all new hamlet centers)
    if all_latitudes and all_longitudes:
        default_center = [sum(all_latitudes) / len(all_latitudes), sum(all_longitudes) / len(all_longitudes)]
    else:
        default_center = [9.914, 106.08] # Fallback
        
    # 7. Compile everything to map data/compiled-config.json
    compiled_config = {
        "province_name": province_name,
        "commune_name": commune_name,
        "company_name": company_name,
        "year": year,
        "month": month,
        "defaultCenter": default_center,
        "defaultZoom": default_zoom,
        "communeProperties": commune_properties,
        "hamlets": hamlets_list,
        "oldHamlets": old_hamlets_list,
        "manualOldHamlets": manual_old_hamlets,
        "mergedHamletSources": merged_sources_map
    }
    
    compiled_config_path = os.path.join(geojson_dir, "compiled-config.json")
    with open(compiled_config_path, "w", encoding="utf-8") as f:
        json.dump(compiled_config, f, ensure_ascii=False, indent=2)
    print(f"Successfully generated config file: {compiled_config_path}")
    
    # 8. Update index.html dynamically
    index_path = "index.html"
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        # Regex replacements
        # Title
        html_content = re.sub(
            r"<title>.*?</title>",
            f"<title>Bản Đồ Tương Tác Xã {commune_name} | {province_name}</title>",
            html_content
        )
        # Description
        html_content = re.sub(
            r'<meta name="description" content=".*?">',
            f'<meta name="description" content="Bản đồ tương tác hiển thị thông tin ranh giới, diện tích, dân số, mật độ và ban lãnh đạo của xã {commune_name}, huyện {commune_name}, tỉnh {province_name} trên nền bản đồ Google Maps có nhãn cực sắc nét.">',
            html_content
        )
        # Keywords
        html_content = re.sub(
            r'<meta name="keywords" content=".*?">',
            f'<meta name="keywords" content="Bản đồ {commune_name}, Xã {commune_name}, Huyện {commune_name}, {province_name}, Bản đồ tương tác, Bản đồ vệ tinh Google">',
            html_content
        )
        # Main Header Text inside Sidebar
        html_content = re.sub(
            r"<p>Bản Đồ Số Tương Tác Xã .*?</p>",
            f"<p>Bản Đồ Số Tương Tác Xã {commune_name}</p>",
            html_content
        )
        # Intro Box Header
        html_content = re.sub(
            r"<p>Bản Đồ Số Tương Tác Xã .*?</p>",
            f"<p>Bản Đồ Số Tương Tác Xã {commune_name}</p>",
            # Handle multiple headers
            html_content
        )
        # Intro text paragraph
        intro_paragraph_pattern = r'<p class="intro-text">.*?</p>'
        new_intro_paragraph = (
            f'<p class="intro-text">\n'
            f'          Chào mừng quý vị đại biểu đến với Bản đồ số tương tác xã {commune_name}, tỉnh {province_name}. '
            f'Đây là sản phẩm công nghệ số do <strong style="color: var(--accent-emerald);">{company_name}</strong> thực hiện vào tháng {month} năm {year}. '
            f'Hệ thống dữ liệu này sẽ được cập nhật liên tục nhằm nâng cao hiệu quả cho công tác quản lý hành chính tại địa phương. '
            f'Xin trân trọng cảm ơn.\n'
            f'        </p>'
        )
        html_content = re.sub(intro_paragraph_pattern, new_intro_paragraph, html_content, flags=re.DOTALL)
        
        # Copyright footer
        footer_pattern = r'<p>&copy; \d+ Bản quyền thuộc về .*?</p>'
        new_footer = f'<p>&copy; {year} Bản quyền thuộc về {company_name} & UBND Xã {commune_name}</p>'
        html_content = re.sub(footer_pattern, new_footer, html_content)
        
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Successfully updated HTML variables in: {index_path}")
        
    print("=== DATA SYNCHRONIZATION COMPLETED ===")

if __name__ == "__main__":
    main()
