import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

map_data_dir = r"d:\4. code\xa_cau_ke\map data"

giong_dau_path = os.path.join(map_data_dir, "Ấp Giồng Dầu.geojson")
thong_thao_path = os.path.join(map_data_dir, "Ấp Thông Thảo.geojson")

with open(giong_dau_path, "r", encoding="utf-8") as f:
    giong_dau_data = json.load(f)

with open(thong_thao_path, "r", encoding="utf-8") as f:
    thong_thao_data = json.load(f)

# Update giong_dau_data (currently east geometry) to represent "Ấp Thông Thảo"
giong_dau_data["name"] = "Ấp Thông Thảo"
props_gd = giong_dau_data["features"][0]["properties"]
props_gd["ten"] = "Ấp Thông Thảo"
props_gd["ma"] = "3005007"
props_gd["sap_nhap_tu"] = ["Ấp Thông Thảo"]

# Update thong_thao_data (currently west geometry) to represent "Ấp Giồng Dầu"
thong_thao_data["name"] = "Ấp Giồng Dầu"
props_tt = thong_thao_data["features"][0]["properties"]
props_tt["ten"] = "Ấp Giồng Dầu"
props_tt["ma"] = "3005006"
props_tt["sap_nhap_tu"] = ["Ấp Giồng Dầu"]

# Write them back with swapped filenames!
with open(thong_thao_path, "w", encoding="utf-8") as f:
    json.dump(giong_dau_data, f, ensure_ascii=False, indent=2)

with open(giong_dau_path, "w", encoding="utf-8") as f:
    json.dump(thong_thao_data, f, ensure_ascii=False, indent=2)

print("Swapped metadata and filenames successfully!")
