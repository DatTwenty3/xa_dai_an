import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

map_data_dir = r"d:\4. code\xa_cau_ke\map data"

thong_thao_path = os.path.join(map_data_dir, "Ấp Thông Thảo.geojson")
giong_dau_path = os.path.join(map_data_dir, "Ấp Giồng Dầu.geojson")

with open(thong_thao_path, "r", encoding="utf-8") as f:
    thong_thao_data = json.load(f)

with open(giong_dau_path, "r", encoding="utf-8") as f:
    giong_dau_data = json.load(f)

props_tt = thong_thao_data["features"][0]["properties"]
props_gd = giong_dau_data["features"][0]["properties"]

keys = [
    "so_ho_sau_sap_nhap",
    "so_dan_sau_sap_nhap",
    "dien_tich_sau_sap_nhap_ha",
    "dien_tich_km2",
    "dien_tich_ha",
    "dan_so",
    "so_ho",
    "mat_do_km2"
]

for key in keys:
    temp = props_tt[key]
    props_tt[key] = props_gd[key]
    props_gd[key] = temp

with open(thong_thao_path, "w", encoding="utf-8") as f:
    json.dump(thong_thao_data, f, ensure_ascii=False, indent=2)

with open(giong_dau_path, "w", encoding="utf-8") as f:
    json.dump(giong_dau_data, f, ensure_ascii=False, indent=2)

print("Swapped statistics successfully!")
