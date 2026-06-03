"""Recalculate mat_do_km2 = dan_so / dien_tich_km2 (nguoi/km2)."""
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
        if "dan_so" not in props or "dien_tich_km2" not in props:
            continue
        pop = float(str(props["dan_so"]).replace(",", "."))
        km2 = float(str(props["dien_tich_km2"]).replace(",", "."))
        if km2 <= 0:
            continue
        density = f"{pop / km2:.2f}"
        if props.get("mat_do_km2") != density:
            props["mat_do_km2"] = density
            changed = True

    if changed:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("updated:", path.stem.encode("unicode_escape").decode())

print("done")
