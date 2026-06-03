"""Recalculate dien_tich_km2 from dien_tich_ha (1 ha = 0.01 km2)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "map data"

for path in sorted(DATA_DIR.glob("*.geojson")):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    changed = False
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        if "dien_tich_ha" not in props:
            continue
        ha = float(str(props["dien_tich_ha"]).replace(",", "."))
        km2 = f"{ha / 100:.4f}"
        if props.get("dien_tich_km2") != km2:
            props["dien_tich_km2"] = km2
            changed = True

    if changed:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("updated:", path.stem.encode("unicode_escape").decode())

print("done")
