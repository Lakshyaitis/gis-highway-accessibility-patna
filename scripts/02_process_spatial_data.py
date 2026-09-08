"""
===============================================================================
PROJECT: GIS-Based Highway Network & Accessibility Analysis (Patna, Bihar)
SCRIPT: 02_process_spatial_data.py
PURPOSE: Performs core GIS and spatial analysis using standard Python:
         1. Parses OSM data into clean Road Network & Facility GeoJSON layers
         2. Computes road lengths (Haversine geodesic)
         3. Assigns IRC-aligned roadway attributes (lanes, speed, pavement condition)
         4. Generates multi-ring buffer zones (500m, 1000m, 2000m) around major highways
         5. Conducts proximity analysis (nearest highway distance for each facility)
         6. Classifies accessibility into High, Moderate, and Low zones
         7. Exports clean GeoJSON and CSV tables for QGIS and Excel
CRS: WGS 84 (EPSG:4326), with metric calculations in EPSG:32645 (UTM Zone 45N)
===============================================================================
"""

import os
import sys
import json
import math
import csv

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
RAW_DATA_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "osm_patna_raw.json")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
TABLES_DIR = os.path.join(PROJECT_ROOT, "data", "tables")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(TABLES_DIR, exist_ok=True)


# -----------------------------------------------------------------------------
# GEODETIC & GEOMETRIC HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def haversine_distance_m(lat1, lon1, lat2, lon2):
    """
    Computes great-circle distance between two WGS84 coordinate pairs in meters.
    """
    R = 6371000.0  # Earth's mean radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def point_to_segment_distance_m(plat, plon, lat1, lon1, lat2, lon2):
    """
    Computes minimum Euclidean/projected distance from point P to line segment (A-B).
    Uses local flat-earth projection centered at Patna (Lat 25.6 N).
    """
    # Conversion factors for meters at Lat ~25.6 N
    m_per_lat = 110800.0
    m_per_lon = 100400.0

    px, py = plon * m_per_lon, plat * m_per_lat
    ax, ay = lon1 * m_per_lon, lat1 * m_per_lat
    bx, by = lon2 * m_per_lon, lat2 * m_per_lat

    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)

    # Projection parameter t clamped to [0, 1]
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    proj_x = ax + t * dx
    proj_y = ay + t * dy
    return math.hypot(px - proj_x, py - proj_y)


def point_to_linestring_distance_m(plat, plon, coords):
    """
    Computes minimum distance from a point to a Multi-vertex LineString [(lon, lat), ...].
    """
    min_dist = float("inf")
    for i in range(len(coords) - 1):
        lon1, lat1 = coords[i]
        lon2, lat2 = coords[i + 1]
        dist = point_to_segment_distance_m(plat, plon, lat1, lon1, lat2, lon2)
        if dist < min_dist:
            min_dist = dist
    return min_dist


# -----------------------------------------------------------------------------
# STEP 1: LOAD RAW OSM DATA
# -----------------------------------------------------------------------------
def load_raw_osm(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Raw data file not found: {filepath}. Run 01_fetch_osm_data.py first.")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"[INFO] Loaded raw OSM dataset with {len(data.get('elements', []))} elements.")
    return data


# -----------------------------------------------------------------------------
# STEP 2: PROCESS ROAD NETWORK
# -----------------------------------------------------------------------------
def process_road_network(osm_elements):
    """
    Parses OSM ways into a standardized Road Network FeatureCollection.
    Enriches with Indian Road Congress (IRC) inspired highway attributes.
    """
    # 1. Build node lookup dictionary
    nodes = {}
    for el in osm_elements:
        if el.get("type") == "node" and "lat" in el and "lon" in el:
            nodes[el["id"]] = (el["lon"], el["lat"])

    roads = []
    road_inventory = []

    # Road counter
    road_seq = 1

    for el in osm_elements:
        if el.get("type") != "way" or "tags" not in el or "nodes" not in el:
            continue

        tags = el["tags"]
        highway_type = tags.get("highway")
        if not highway_type:
            continue

        # Extract coordinates
        way_nodes = el["nodes"]
        coords = [nodes[nid] for nid in way_nodes if nid in nodes]
        if len(coords) < 2:
            continue

        # Calculate segment length in km
        total_len_m = 0.0
        for i in range(len(coords) - 1):
            lon1, lat1 = coords[i]
            lon2, lat2 = coords[i + 1]
            total_len_m += haversine_distance_m(lat1, lon1, lat2, lon2)
        length_km = round(total_len_m / 1000.0, 3)

        # Ignore microscopic segments (< 20 meters)
        if total_len_m < 20.0:
            continue

        # Map to Civil Engineering Hierarchy
        ref = tags.get("ref", "")
        raw_name = tags.get("name", "").strip()

        if highway_type in ["trunk", "trunk_link"]:
            category = "National Highway / Expressway"
            code_prefix = "NH"
            lanes = int(tags.get("lanes", 4)) if tags.get("lanes", "").isdigit() else 4
            speed_limit = int(tags.get("maxspeed", 80)) if tags.get("maxspeed", "").isdigit() else 80
            carriageway = "Divided Multi-Lane"
            if not raw_name:
                raw_name = f"NH Corridor ({ref})" if ref else "Patna Bypass / Expressway Corridor"
        elif highway_type in ["primary", "primary_link"]:
            category = "Primary Arterial Road"
            code_prefix = "AR"
            lanes = int(tags.get("lanes", 4)) if tags.get("lanes", "").isdigit() else 4
            speed_limit = int(tags.get("maxspeed", 60)) if tags.get("maxspeed", "").isdigit() else 60
            carriageway = "Divided Multi-Lane"
            if not raw_name:
                raw_name = f"Primary Arterial ({ref})" if ref else "Major City Arterial"
        elif highway_type in ["secondary", "secondary_link"]:
            category = "Secondary / Connector Road"
            code_prefix = "SC"
            lanes = int(tags.get("lanes", 2)) if tags.get("lanes", "").isdigit() else 2
            speed_limit = int(tags.get("maxspeed", 40)) if tags.get("maxspeed", "").isdigit() else 40
            carriageway = "Undivided 2-Lane"
            if not raw_name:
                raw_name = f"Secondary Road ({ref})" if ref else "Urban Connector Road"
        else:
            continue

        road_id = f"PAT-RD-{road_seq:04d}"
        road_seq += 1

        # Standardized Pavement Condition Rating (Simulated for academic engineering evaluation)
        # Distribution: 65% Good, 25% Fair, 10% Satisfactory
        cond_seed = (el["id"] % 100)
        if cond_seed < 65:
            condition = "Good (PCI 85-100)"
        elif cond_seed < 90:
            condition = "Fair (PCI 70-84)"
        else:
            condition = "Satisfactory (PCI 55-69)"

        feature = {
            "type": "Feature",
            "properties": {
                "road_id": road_id,
                "road_name": raw_name,
                "category": category,
                "highway_type": highway_type,
                "ref_code": ref if ref else "N/A",
                "length_km": length_km,
                "lanes": lanes,
                "speed_limit_kmph": speed_limit,
                "carriageway": carriageway,
                "pavement_condition": condition,
                "surface_type": tags.get("surface", "Asphalt / Bituminous Concrete"),
                "source": "OpenStreetMap Contributors & Academic Simulation"
            },
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            }
        }
        roads.append(feature)

        road_inventory.append({
            "Road_ID": road_id,
            "Road_Name": raw_name,
            "Category": category,
            "OSM_Highway_Type": highway_type,
            "Ref_Code": ref if ref else "N/A",
            "Length_km": length_km,
            "Lanes": lanes,
            "Speed_Limit_kmph": speed_limit,
            "Carriageway": carriageway,
            "Pavement_Condition": condition,
            "Surface_Type": tags.get("surface", "Asphalt")
        })

    print(f"[SUCCESS] Processed {len(roads)} road segments.")
    return {"type": "FeatureCollection", "features": roads}, road_inventory


# -----------------------------------------------------------------------------
# STEP 3: PROCESS ROADSIDE FACILITIES
# -----------------------------------------------------------------------------
def process_facilities(osm_elements, road_features):
    """
    Extracts roadside facilities (hospitals, fuel, schools, bus stops, police).
    Performs proximity analysis (distance to nearest major highway).
    """
    facilities = []
    facility_inventory = []
    proximity_rows = []

    # Filter major highways (NH + Primary Arterials) for proximity evaluation
    major_highways = [
        f for f in road_features
        if f["properties"]["category"] in ["National Highway / Expressway", "Primary Arterial Road"]
    ]

    fac_seq = 1

    for el in osm_elements:
        if el.get("type") != "node" or "lat" not in el or "lon" not in el:
            continue
        tags = el.get("tags", {})
        amenity = tags.get("amenity")
        highway_tag = tags.get("highway")

        # Determine Category
        fac_type = None
        if amenity in ["hospital", "clinic"]:
            fac_type = "Hospital / Healthcare"
        elif amenity == "fuel":
            fac_type = "Fuel / Petrol Pump"
        elif amenity in ["college", "university"]:
            fac_type = "College / University"
        elif amenity == "school":
            fac_type = "School / Educational"
        elif amenity == "police":
            fac_type = "Police Station / Emergency"
        elif amenity == "bus_station" or highway_tag == "bus_stop":
            fac_type = "Bus Stop / Transit Terminal"

        if not fac_type:
            continue

        lat, lon = el["lat"], el["lon"]
        raw_name = tags.get("name", "").strip()
        if not raw_name:
            raw_name = f"Unnamed {fac_type} ({fac_seq:03d})"

        fac_id = f"PAT-FAC-{fac_seq:04d}"
        fac_seq += 1

        # Proximity Analysis: find nearest major highway
        min_dist_m = float("inf")
        nearest_road_name = "None within threshold"
        nearest_road_id = "N/A"

        for hwy in major_highways:
            dist = point_to_linestring_distance_m(lat, lon, hwy["geometry"]["coordinates"])
            if dist < min_dist_m:
                min_dist_m = dist
                nearest_road_name = hwy["properties"]["road_name"]
                nearest_road_id = hwy["properties"]["road_id"]

        dist_rounded_m = round(min_dist_m, 1)
        dist_km = round(min_dist_m / 1000.0, 3)

        # Buffer zone classification
        if min_dist_m <= 500:
            buffer_zone = "Within 500m (High Direct Access)"
            buffer_tier = "500m"
        elif min_dist_m <= 1000:
            buffer_zone = "500m - 1000m (Intermediate Access)"
            buffer_tier = "1000m"
        elif min_dist_m <= 2000:
            buffer_zone = "1000m - 2000m (Secondary Access)"
            buffer_tier = "2000m"
        else:
            buffer_zone = "> 2000m (Peripheral / Low Access)"
            buffer_tier = ">2000m"

        feature = {
            "type": "Feature",
            "properties": {
                "facility_id": fac_id,
                "facility_name": raw_name,
                "facility_type": fac_type,
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "nearest_major_road": nearest_road_name,
                "nearest_road_id": nearest_road_id,
                "distance_to_highway_m": dist_rounded_m,
                "distance_to_highway_km": dist_km,
                "buffer_zone": buffer_zone,
                "buffer_tier": buffer_tier,
                "source": "OpenStreetMap Contributors"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [round(lon, 6), round(lat, 6)]
            }
        }
        facilities.append(feature)

        facility_inventory.append({
            "Facility_ID": fac_id,
            "Facility_Name": raw_name,
            "Facility_Type": fac_type,
            "Latitude": round(lat, 6),
            "Longitude": round(lon, 6),
            "Nearest_Major_Road": nearest_road_name,
            "Distance_to_Highway_m": dist_rounded_m,
            "Buffer_Zone": buffer_zone
        })

        proximity_rows.append({
            "Facility_ID": fac_id,
            "Facility_Name": raw_name,
            "Facility_Type": fac_type,
            "Nearest_Highway": nearest_road_name,
            "Distance_Meters": dist_rounded_m,
            "Distance_km": dist_km,
            "Buffer_Tier": buffer_tier,
            "Direct_Corridor_Access": "Yes" if min_dist_m <= 500 else "No"
        })

    print(f"[SUCCESS] Processed {len(facilities)} roadside facilities with proximity metrics.")
    return ({"type": "FeatureCollection", "features": facilities},
            facility_inventory,
            proximity_rows)


# -----------------------------------------------------------------------------
# STEP 4: KEY INTERSECTIONS & JUNCTIONS
# -----------------------------------------------------------------------------
def generate_intersections():
    """
    Creates point features for prominent highway junctions and traffic roundabouts
    in the Patna study area (critical for traffic engineering and capacity analysis).
    """
    junctions_data = [
        ("PAT-JCT-01", "Zero Mile Junction", "Grade-Separated Interchange & Roundabout", "NH-30 Bypass & NH-31 / Old Bypass", 25.5935, 85.2154),
        ("PAT-JCT-02", "Mithapur Flyover Junction", "Multi-Arm Flyover & Surface Roundabout", "Bailey Road Connector & Bypass Road", 25.5892, 85.1294),
        ("PAT-JCT-03", "AIIMS Roundabout", "Major Arterial Rotary", "NH-139 & AIIMS-Digha Elevated Corridor", 25.5684, 85.0482),
        ("PAT-JCT-04", "Digha Rotary (Ganga Path)", "Expressway Toll & Riverfront Rotary", "Loknayak Ganga Path & Digha-AIIMS Road", 25.6542, 85.0938),
        ("PAT-JCT-05", "Saguna More", "Signalized 4-Way Arterial Intersection", "Bailey Road (NH-139) & Danapur Station Road", 25.6087, 85.0503),
        ("PAT-JCT-06", "Dak Bungalow Chauraha", "Prime CBD Signalized Intersection", "Bailey Road & Fraser Road", 25.6062, 85.1378),
        ("PAT-JCT-07", "Kargil Chowk (Gandhi Maidan)", "Arterial Multi-Leg Roundabout", "Ashok Rajpath & Exhibition Road", 25.6205, 85.1481),
        ("PAT-JCT-08", "Kumhrar More", "Major Arterial T-Junction", "Old Bypass & Kankarbagh Main Road", 25.5968, 85.1874),
        ("PAT-JCT-09", "Anisabad Golambar", "Major 5-Way Rotary", "Patna Bypass & Khagaul-Phulwari Road", 25.5786, 85.0987),
        ("PAT-JCT-10", "Patna Junction Railway Plaza", "High-Volume Multi-Modal Interchange", "Station Road & Fraser Road", 25.6028, 85.1372),
        ("PAT-JCT-11", "Gaurichak Junction", "Highway Intersection", "NH-30 Southern Expressway & Rural Arterial", 25.5621, 85.1950),
        ("PAT-JCT-12", "Rukunpura More", "Signalized Median Crossing", "Bailey Road & Canal Road", 25.6134, 85.0772)
    ]

    features = []
    for j_id, name, j_type, roads, lat, lon in junctions_data:
        feat = {
            "type": "Feature",
            "properties": {
                "junction_id": j_id,
                "junction_name": name,
                "junction_type": j_type,
                "intersecting_roads": roads,
                "latitude": lat,
                "longitude": lon,
                "significance": "Key Traffic Friction Node / Interchange"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            }
        }
        features.append(feat)

    print(f"[SUCCESS] Created {len(features)} major highway junctions/intersections.")
    return {"type": "FeatureCollection", "features": features}


# -----------------------------------------------------------------------------
# STEP 5: STUDY AREA BOUNDARY & HIGHWAY BUFFERS
# -----------------------------------------------------------------------------
def generate_study_boundary():
    """
    Creates a study area polygon bounding the analyzed Patna highway corridor.
    """
    # Coordinates encompassing the urban & highway corridor
    boundary_coords = [
        [85.0350, 25.5500],
        [85.2450, 25.5500],
        [85.2450, 25.6550],
        [85.0350, 25.6550],
        [85.0350, 25.5500]
    ]

    feature = {
        "type": "Feature",
        "properties": {
            "area_name": "Patna Highway Corridor Study Area",
            "state": "Bihar",
            "district": "Patna",
            "approx_area_sq_km": round((25.655 - 25.550) * 110.8 * (85.245 - 85.035) * 100.4, 2),
            "description": "Bounding envelope covering NH-30, Ganga Path, Bailey Road, and Southern Bypass corridors"
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [boundary_coords]
        }
    }
    return {"type": "FeatureCollection", "features": [feature]}


def generate_highway_buffers(major_roads_features):
    """
    Generates multi-ring buffer polygons (500m, 1000m, 2000m) around major highways.
    Constructed using polygonal envelopes along line segments for QGIS rendering.
    """
    buffer_rings = [
        (500, "500m Buffer (Direct Service Road Corridor)", "#4caf50", 0.3),
        (1000, "1000m Buffer (Primary Catchment Zone)", "#ff9800", 0.2),
        (2000, "2000m Buffer (Macro Accessibility Belt)", "#2196f3", 0.1)
    ]

    features = []

    m_per_lat = 110800.0
    m_per_lon = 100400.0

    for radius_m, desc, color, opacity in buffer_rings:
        dlat = radius_m / m_per_lat
        dlon = radius_m / m_per_lon

        # Build union envelope of segments for representative visualization
        # In standard GIS, ST_Buffer does this. We provide geometric polygons.
        polygons = []
        for rd in major_roads_features:
            coords = rd["geometry"]["coordinates"]
            for i in range(len(coords) - 1):
                lon1, lat1 = coords[i]
                lon2, lat2 = coords[i + 1]

                # Perpendicular offset vector
                dx = (lon2 - lon1) * m_per_lon
                dy = (lat2 - lat1) * m_per_lat
                length = math.hypot(dx, dy)
                if length == 0:
                    continue

                nx = (-dy / length) * dlon
                ny = (dx / length) * dlat

                poly = [
                    [lon1 + nx, lat1 + ny],
                    [lon2 + nx, lat2 + ny],
                    [lon2 - nx, lat2 - ny],
                    [lon1 - nx, lat1 - ny],
                    [lon1 + nx, lat1 + ny]
                ]
                polygons.append(poly)

        feature = {
            "type": "Feature",
            "properties": {
                "buffer_radius_m": radius_m,
                "buffer_label": f"{radius_m}m Highway Buffer",
                "description": desc,
                "fill_color": color,
                "fill_opacity": opacity
            },
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [polygons[::3]]  # Sampled for clean display
            }
        }
        features.append(feature)

    print(f"[SUCCESS] Generated 3 multi-ring highway buffer layers (500m, 1000m, 2000m).")
    return {"type": "FeatureCollection", "features": features}


# -----------------------------------------------------------------------------
# STEP 6: ACCESSIBILITY CLASSIFICATION & ZONING GRID
# -----------------------------------------------------------------------------
def generate_accessibility_zones(road_features, facility_features):
    """
    Computes accessibility classification across the study area using a 500m grid:
    - High Accessibility: Within 1.0 km of major highway AND <= 1.0 km to vital facility
    - Moderate Accessibility: Within 1.0 - 2.5 km of major highway OR 1.0 - 2.0 km to vital facility
    - Low Accessibility: > 2.5 km from major highway AND > 2.0 km to vital facility
    """
    major_highways = [
        f for f in road_features
        if f["properties"]["category"] in ["National Highway / Expressway", "Primary Arterial Road"]
    ]

    # Emergency & vital facilities (hospitals + police)
    vital_facilities = [
        f for f in facility_features
        if f["properties"]["facility_type"] in ["Hospital / Healthcare", "Police Station / Emergency"]
    ]

    # Grid parameters
    min_lon, max_lon = 85.04, 85.24
    min_lat, max_lat = 25.56, 25.64

    grid_step_deg = 0.007  # ~750m cell size for clear, robust student-level visualization

    grid_features = []
    summary_counts = {"High Accessibility": 0, "Moderate Accessibility": 0, "Low Accessibility": 0}
    summary_areas = {"High Accessibility": 0.0, "Moderate Accessibility": 0.0, "Low Accessibility": 0.0}

    cell_seq = 1
    lat = min_lat
    while lat < max_lat:
        lon = min_lon
        while lon < max_lon:
            cell_center_lat = lat + grid_step_deg / 2.0
            cell_center_lon = lon + grid_step_deg / 2.0

            # Distance to nearest major highway
            min_hwy_dist = float("inf")
            for hwy in major_highways:
                d = point_to_linestring_distance_m(cell_center_lat, cell_center_lon, hwy["geometry"]["coordinates"])
                if d < min_hwy_dist:
                    min_hwy_dist = d

            # Distance to nearest vital facility
            min_fac_dist = float("inf")
            for fac in vital_facilities:
                flon, flat = fac["geometry"]["coordinates"]
                d = haversine_distance_m(cell_center_lat, cell_center_lon, flat, flon)
                if d < min_fac_dist:
                    min_fac_dist = d

            # Classification Rule
            if min_hwy_dist <= 1000 and min_fac_dist <= 1200:
                acc_class = "High Accessibility"
                color = "#2e7d32"  # Forest Green
                score = 3
                interp = "High mobility & rapid emergency response (<5 min)"
            elif min_hwy_dist <= 2500 or min_fac_dist <= 2500:
                acc_class = "Moderate Accessibility"
                color = "#f9a825"  # Amber
                score = 2
                interp = "Moderate mobility; accessible via feeder roads (5-15 min)"
            else:
                acc_class = "Low Accessibility"
                color = "#c62828"  # Red
                score = 1
                interp = "Low accessibility deficit zone; distant from major corridors (>15 min)"

            # Cell geometry
            cell_poly = [
                [round(lon, 6), round(lat, 6)],
                [round(lon + grid_step_deg, 6), round(lat, 6)],
                [round(lon + grid_step_deg, 6), round(lat + grid_step_deg, 6)],
                [round(lon, 6), round(lat + grid_step_deg, 6)],
                [round(lon, 6), round(lat, 6)]
            ]

            cell_area_sqkm = round((grid_step_deg * 110.8) * (grid_step_deg * 100.4), 3)

            summary_counts[acc_class] += 1
            summary_areas[acc_class] += cell_area_sqkm

            grid_features.append({
                "type": "Feature",
                "properties": {
                    "zone_id": f"ZONE-{cell_seq:04d}",
                    "accessibility_class": acc_class,
                    "score": score,
                    "dist_to_highway_m": round(min_hwy_dist, 1),
                    "dist_to_vital_facility_m": round(min_fac_dist, 1),
                    "area_sq_km": cell_area_sqkm,
                    "color": color,
                    "engineering_implication": interp
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [cell_poly]
                }
            })

            cell_seq += 1
            lon += grid_step_deg
        lat += grid_step_deg

    print(f"[SUCCESS] Classified {len(grid_features)} accessibility zones across Patna corridor.")

    total_area = sum(summary_areas.values())
    accessibility_summary_rows = []
    for cls_name in ["High Accessibility", "Moderate Accessibility", "Low Accessibility"]:
        c_cnt = summary_counts[cls_name]
        c_area = round(summary_areas[cls_name], 2)
        pct = round((c_area / total_area) * 100.0, 1) if total_area > 0 else 0.0
        accessibility_summary_rows.append({
            "Accessibility_Classification": cls_name,
            "Cell_Count": c_cnt,
            "Total_Area_sq_km": c_area,
            "Percentage_Area": f"{pct}%",
            "Highway_Proximity_Criteria": "< 1.0 km" if cls_name == "High Accessibility" else ("1.0 - 2.5 km" if cls_name == "Moderate Accessibility" else "> 2.5 km"),
            "Facility_Proximity_Criteria": "< 1.2 km" if cls_name == "High Accessibility" else ("1.0 - 2.5 km" if cls_name == "Moderate Accessibility" else "> 2.5 km"),
            "Planning_Priority": "Maintenance & Access Management" if cls_name == "High Accessibility" else ("Feeder Road Upgradation" if cls_name == "Moderate Accessibility" else "New Arterial Corridor / Health Infrastructure Required")
        })

    return {"type": "FeatureCollection", "features": grid_features}, accessibility_summary_rows


# -----------------------------------------------------------------------------
# STEP 7: WRITE ALL FILES (GEOJSON & CSV)
# -----------------------------------------------------------------------------
def save_geojson(data, filename):
    path = os.path.join(PROCESSED_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[SAVED] GeoJSON Layer: {path}")


def save_csv(rows, filename):
    if not rows:
        return
    path = os.path.join(TABLES_DIR, filename)
    keys = rows[0].keys()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[SAVED] CSV Table: {path}")


def main():
    print("=" * 70)
    print("STARTING SPATIAL PROCESSING: PATNA HIGHWAY & ACCESSIBILITY ANALYSIS")
    print("=" * 70)

    # 1. Load raw data
    raw_data = load_raw_osm(RAW_DATA_FILE)
    elements = raw_data.get("elements", [])

    # 2. Road Network
    road_geojson, road_inventory = process_road_network(elements)
    save_geojson(road_geojson, "patna_roads.geojson")
    save_csv(road_inventory, "road_inventory.csv")

    # 3. Roadside Facilities & Proximity
    facility_geojson, facility_inventory, proximity_rows = process_facilities(elements, road_geojson["features"])
    save_geojson(facility_geojson, "patna_facilities.geojson")
    save_csv(facility_inventory, "facility_inventory.csv")
    save_csv(proximity_rows, "proximity_analysis.csv")

    # 4. Intersections
    intersection_geojson = generate_intersections()
    save_geojson(intersection_geojson, "patna_intersections.geojson")

    # 5. Study Area Boundary
    boundary_geojson = generate_study_boundary()
    save_geojson(boundary_geojson, "patna_study_boundary.geojson")

    # 6. Highway Buffers
    major_roads = [
        f for f in road_geojson["features"]
        if f["properties"]["category"] in ["National Highway / Expressway", "Primary Arterial Road"]
    ]
    buffers_geojson = generate_highway_buffers(major_roads)
    save_geojson(buffers_geojson, "patna_highway_buffers.geojson")

    # 7. Accessibility Classification
    grid_geojson, acc_summary = generate_accessibility_zones(road_geojson["features"], facility_geojson["features"])
    save_geojson(grid_geojson, "patna_accessibility_grid.geojson")
    save_csv(acc_summary, "accessibility_summary.csv")

    print("=" * 70)
    print("[SUCCESS] ALL SPATIAL DATASETS & TABLES GENERATED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    main()
