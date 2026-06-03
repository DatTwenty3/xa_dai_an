import os
import json
import sys

# Reconfigure stdout to use utf-8 to avoid console encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Hamlet stats from thong_tin_sap_nhap.txt
STATS = {
    "Ấp Chợ": {
        "ma": "3006001",
        "dien_tich_ha": 144.5,
        "so_ho": 705,
        "dan_so": 3136,
        "sap_nhap_tu": ["Ấp Chợ", "Ấp Mé Rạch E", "Ấp Giồng Đình"]
    },
    "Ấp Trà Kha": {
        "ma": "3006002",
        "dien_tich_ha": 328.53,
        "so_ho": 704,
        "dan_so": 3087,
        "sap_nhap_tu": ["Ấp Cây Da", "Ấp Trà Kha"]
    },
    "Ấp Giồng Đình": {
        "ma": "3006003",
        "dien_tich_ha": 372.35,
        "so_ho": 725,
        "dan_so": 3197,
        "sap_nhap_tu": ["Ấp Giồng Đình", "Ấp Xà Lôn"]
    },
    "Ấp Giồng Giữa": {
        "ma": "3006004",
        "dien_tich_ha": 902.74,
        "so_ho": 705,
        "dan_so": 2716,
        "sap_nhap_tu": ["Ấp Mé Rạch B", "Ấp Giồng Giữa", "Ấp Bến Tranh", "Ấp Vàm Bến Tranh"]
    },
    "Ấp Mé Láng": {
        "ma": "3006005",
        "dien_tich_ha": 359.47,
        "so_ho": 816,
        "dan_so": 3525,
        "sap_nhap_tu": ["Ấp Mé Láng", "Ấp Làng Cá", "Ấp Bến Chùa"]
    },
    "Ấp Định An": {
        "ma": "3006006",
        "dien_tich_ha": 751.92,
        "so_ho": 745,
        "dan_so": 3611,
        "sap_nhap_tu": ["Ấp Định An", "Ấp Cá Lóc", "Ấp Bến Tranh", "Ấp Vàm Bến Tranh"]
    },
    "Ấp Giồng Lớn": {
        "ma": "3006007",
        "dien_tich_ha": 552.19,
        "so_ho": 861,
        "dan_so": 3764,
        "sap_nhap_tu": ["Ấp Giồng Lớn A", "Ấp Giồng Lớn B"]
    }
}

def main():
    map_dir = "map data"
    print("=== STARTING POPULATION & POLYGONIZATION ===")
    
    for filename in os.listdir(map_dir):
        if not filename.endswith(".geojson"):
            continue
            
        hamlet_name = os.path.splitext(filename)[0]
        if hamlet_name not in STATS:
            print(f"Warning: Hamlet '{hamlet_name}' not found in stats mapping, skipping.")
            continue
            
        filepath = os.path.join(map_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        features = data.get("features", [])
        if not features:
            print(f"Warning: No features in {filename}, skipping.")
            continue
            
        info = STATS[hamlet_name]
        
        # We need to compile the features to have correct properties and geometries
        for feature in features:
            # 1. Update properties
            area_ha = info["dien_tich_ha"]
            pop = info["dan_so"]
            feature["properties"] = {
                "ten": hamlet_name,
                "ma": info["ma"],
                "loai": "Ấp",
                "dien_tich_ha": str(area_ha),
                "dien_tich_km2": f"{(area_ha / 100.0):.4f}",
                "dan_so": str(pop),
                "so_ho": str(info["so_ho"]),
                "mat_do_km2": f"{(pop / (area_ha / 100.0)):.2f}" if area_ha > 0 else "0",
                "sap_nhap_tu": info["sap_nhap_tu"]
            }
            
            # 2. Polygonize geometry if MultiLineString
            geom = feature.get("geometry", {})
            gtype = geom.get("type")
            coords = geom.get("coordinates", [])
            
            if gtype == "MultiLineString":
                new_coords = []
                for line in coords:
                    if len(line) < 3:
                        continue
                    # Close line if not closed
                    if line[0][0] != line[-1][0] or line[0][1] != line[-1][1]:
                        line.append(line[0])
                    new_coords.append([line])
                
                if len(new_coords) == 1:
                    geom["type"] = "Polygon"
                    geom["coordinates"] = new_coords[0]
                elif len(new_coords) > 1:
                    geom["type"] = "MultiPolygon"
                    geom["coordinates"] = new_coords
                    
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully processed {filename} (Properties populated & converted to Polygon/MultiPolygon)")
        
    print("=== POPULATION & POLYGONIZATION COMPLETED ===")

if __name__ == "__main__":
    main()
