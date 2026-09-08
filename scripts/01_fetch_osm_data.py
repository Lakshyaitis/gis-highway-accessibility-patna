"""
===============================================================================
PROJECT: GIS-Based Highway Network & Accessibility Analysis (Patna, Bihar)
SCRIPT: 01_fetch_osm_data.py
PURPOSE: Fetches real-world OpenStreetMap (OSM) spatial data for Patna using
         the Overpass API. Extracts major highways, secondary roads, and
         essential roadside facilities (hospitals, fuel stations, schools,
         bus stops, police stations).
CRS: WGS 84 (EPSG:4326)
===============================================================================
"""

import os
import sys
import json
import urllib.request
import urllib.parse

# Define Study Area Bounding Box for Patna Highway Corridor
# South, West, North, East (covers Digha, Danapur, AIIMS, NH-30 Bypass, Ganga Path, Zero Mile)
BBOX_PATNA = "25.56,85.04,25.64,85.24"

# Overpass API endpoint
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
OUTPUT_FILE = os.path.join(RAW_DATA_DIR, "osm_patna_raw.json")


def build_overpass_query(bbox):
    """
    Constructs an Overpass QL query to extract:
    1. Highways: trunk (NH), primary (major arterials), secondary (state/district roads)
    2. Roadside Amenities: hospitals, clinics, fuel stations, bus stops, police, colleges
    """
    query = f"""
    [out:json][timeout:60];
    (
      way["highway"~"trunk|primary|secondary"]({bbox});
      node["amenity"~"hospital|clinic|fuel|bus_station|police|college|university|school"]({bbox});
      node["highway"="bus_stop"]({bbox});
    );
    out body;
    >;
    out skel qt;
    """
    return query.strip()


def fetch_osm_data():
    """
    Sends POST request to Overpass API and saves the raw response to JSON.
    """
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    query = build_overpass_query(BBOX_PATNA)
    print(f"[INFO] Connecting to Overpass API for Patna bounding box: {BBOX_PATNA}...")

    encoded_data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    req = urllib.request.Request(
        OVERPASS_URL,
        data=encoded_data,
        headers={"User-Agent": "PatnaGISCivilProject/1.0 (academic research)"}
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            if response.status == 200:
                raw_json = json.loads(response.read().decode("utf-8"))
                elements = raw_json.get("elements", [])
                print(f"[SUCCESS] Received {len(elements)} spatial elements from OpenStreetMap.")

                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(raw_json, f, indent=2)
                print(f"[INFO] Raw OSM data written to: {OUTPUT_FILE}")
                return True
            else:
                print(f"[ERROR] API returned status code: {response.status}")
                return False
    except Exception as e:
        print(f"[WARNING] Live API fetch encountered an issue: {e}")
        if os.path.exists(OUTPUT_FILE):
            print(f"[INFO] Using existing cached raw data at: {OUTPUT_FILE}")
            return True
        else:
            print("[ERROR] No cached data available.")
            return False


if __name__ == "__main__":
    fetch_osm_data()
