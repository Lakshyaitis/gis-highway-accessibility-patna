# QGIS Setup & Project Exploration Guide

This document provides a step-by-step walkthrough for opening, exploring, styling, and presenting the **Patna Highway Network & Accessibility Analysis** project in **QGIS 3.x** (QGIS 3.22 / 3.28 / 3.34 LTR).

---

## 1. Prerequisites
- **QGIS Desktop** (Free & Open Source): Download from [qgis.org](https://qgis.org) (Version 3.22 or newer).
- No special proprietary plugins or paid extensions are required.

---

## 2. Opening the Project in QGIS

### Option A: Open the Pre-Configured Project File (Recommended)
1. Launch **QGIS Desktop**.
2. Go to **Project → Open...** (or press `Ctrl + O`).
3. Navigate to:
   ```
   gis-highway-accessibility-patna/qgis/patna_highway_accessibility.qgs
   ```
4. Click **Open**.
5. All layers will load automatically with relative paths to `../data/processed/`, complete with styled symbology, labels, and rendering order.

---

### Option B: Loading GeoJSON Layers Manually
If you prefer to load the layers from scratch into a fresh QGIS project:
1. Open a blank QGIS project.
2. Set the Project Coordinate Reference System (CRS) at the bottom-right corner to:
   - **WGS 84 (EPSG:4326)** for geographic coordinates, OR
   - **WGS 84 / UTM Zone 45N (EPSG:32645)** for metric cartographic projection (standard UTM zone for Bihar).
3. Open the file browser in QGIS and navigate to `data/processed/`.
4. Drag and drop the following files into the **Layers Panel** in this exact order (from top to bottom):
   1. `patna_intersections.geojson` *(Points - Major Junctions & Rotaries)*
   2. `patna_facilities.geojson` *(Points - Public Facilities & POIs)*
   3. `patna_roads.geojson` *(Lines - Road Network)*
   4. `patna_highway_buffers.geojson` *(Polygons - 500m, 1000m, 2000m Buffers)*
   5. `patna_accessibility_grid.geojson` *(Polygons - High/Mod/Low Accessibility)*
   6. `patna_study_boundary.geojson` *(Polygon - Study Area Outline)*
5. Add OpenStreetMap Basemap (Optional background):
   - In the QGIS **Browser Panel**, expand **XYZ Tiles**.
   - Double-click **OpenStreetMap** to add the global base map under your layers.

---

## 3. Applying Layer Styles (.qml)

Pre-built layer style files are provided in `qgis/layer_styles/`. To apply them:

1. Right-click the layer in the **Layers Panel** (e.g., `patna_roads`).
2. Select **Properties...** (or press `F8`).
3. In the lower-left corner of the dialog, click **Style → Load Style...**.
4. Browse to `qgis/layer_styles/` and choose the corresponding `.qml` file:
   - For `patna_roads` → `roads_style.qml`
   - For `patna_facilities` → `facilities_style.qml`
   - For `patna_accessibility_grid` → `accessibility_style.qml`
5. Click **Open** and then **Apply → OK**.

---

## 4. Key Spatial Features to Demonstrate in an Interview

### A. Road Network Categorization
- Open the Attribute Table for `patna_roads` (Right-click → **Open Attribute Table** or press `F6`).
- Point out the field `category`:
  - **National Highway / Expressway** (e.g., NH-30 Bypass, Ganga Path, AIIMS-Digha corridor)
  - **Primary Arterial Road** (e.g., Bailey Road, Ashok Rajpath, Kankarbagh Road)
  - **Secondary / Connector Road** (e.g., Boring Road, Old Bypass)
- Demonstrate how you calculated the `length_km` field and assigned IRC-compliant lane configurations (`lanes`, `speed_limit_kmph`, `carriageway`).

### B. Proximity Analysis on Facilities
- Open the Attribute Table for `patna_facilities`.
- Highlight the fields:
  - `nearest_major_road`: Names the primary highway corridor servicing the facility.
  - `distance_to_highway_m`: Exact perpendicular distance from the facility to the highway.
  - `buffer_zone`: Classifies whether the facility falls within 500m, 1000m, 2000m, or >2000m.
- Show how emergency facilities (trauma centers/hospitals) cluster within 500m of the major bypass.

### C. Multi-Ring Buffers
- Toggle the visibility of `patna_highway_buffers`.
- Explain the civil engineering logic:
  - **500m**: Direct highway corridor influence (frontage road, immediate service access).
  - **1000m**: Intermediate catchment zone (10-minute pedestrian/feeder vehicle access).
  - **2000m**: Macro regional catchment (extended highway accessibility belt).

### D. Accessibility Classification Grid
- Toggle the visibility of `patna_accessibility_grid`.
- Explain the 3-tier categorization:
  - **High Accessibility (Green)**: Within 1.0 km of major highway AND ≤ 1.2 km of an emergency facility.
  - **Moderate Accessibility (Amber)**: Within 1.0 - 2.5 km of major highway OR within 1.0 - 2.5 km of facility.
  - **Low Accessibility (Red)**: Peripheral areas > 2.5 km from major corridors.

---

## 5. Exporting Maps via QGIS Print Layout

1. In QGIS, navigate to **Project → Layouts → Patna Highway Accessibility Map Layout**.
2. The pre-configured print layout contains:
   - **Map Canvas**: Centered on Patna corridor at 1:75,000 scale.
   - **Cartographic Elements**: Dynamic North Arrow, Metric Scale Bar (km), Layer Legend.
   - **Metadata Box**: Title, Subtitle, Author details, Coordinate Reference System (WGS 84 / UTM 45N), Data Source notice.
3. To export:
   - Click **Layout → Export as Image...** (choose PNG, 300 DPI).
   - Click **Layout → Export as PDF...** (for vector document submission).
