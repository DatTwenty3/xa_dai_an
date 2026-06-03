import pyproj

# Test different central meridians and ellipsoid parameters
# Trà Vinh: 105.5
proj_vn2000_krass = pyproj.Proj("+proj=tmerc +lat_0=0 +lon_0=105.5 +k=0.9999 +x_0=500000 +y_0=0 +ellps=krass +towgs84=-191.9,-39.3,-111.5,-0.009288,0.019754,-0.004273,0.252906278 +units=m +no_defs")
proj_vn2000_wgs84 = pyproj.Proj("+proj=tmerc +lat_0=0 +lon_0=105.5 +k=0.9999 +x_0=500000 +y_0=0 +ellps=WGS84 +towgs84=-191.9,-39.3,-111.5,-0.009288,0.019754,-0.004273,0.252906278 +units=m +no_defs")
proj_wgs84 = pyproj.Proj("+proj=latlong +datum=WGS84 +no_defs")

transformer_krass = pyproj.Transformer.from_proj(proj_vn2000_krass, proj_wgs84)
transformer_wgs84 = pyproj.Transformer.from_proj(proj_vn2000_wgs84, proj_wgs84)

x = 587226.8088833063
y = 1065213.840897045

lng_kr, lat_kr = transformer_krass.transform(x, y)
lng_w84, lat_w84 = transformer_wgs84.transform(x, y)

print(f"Krassovsky projection: Lat: {lat_kr}, Lng: {lng_kr}")
print(f"WGS84 projection: Lat: {lat_w84}, Lng: {lng_w84}")
