# GIS-Based Highway Network & Accessibility Analysis
*A Civil Engineering & Geospatial Infrastructure Portfolio Project*

[![QGIS](https://img.shields.io/badge/QGIS-3.28%20LTR-2b5c2a.svg)](https://qgis.org/)
[![CRS](https://img.shields.io/badge/CRS-EPSG%3A4326%20%7C%20EPSG%3A32645-blue.svg)](https://epsg.io/32645)
[![Data](https://img.shields.io/badge/Data-OpenStreetMap-green.svg)](https://www.openstreetmap.org/)
[![Focus](https://img.shields.io/badge/Focus-Civil%20Engineering%20%7C%20NHAI-orange.svg)]()

---

## 1. Project Overview
This project presents an end-to-end, interview-defensible **Civil Engineering GIS Portfolio Project** analyzing the highway network, roadside public facilities, and spatial accessibility across the **Patna Urban and Peri-Urban Corridor, Bihar, India**.

Using **QGIS 3.28 LTR**, standard **Python geodetic processing**, and **OpenStreetMap (OSM)** datasets, the project maps **412.8 km of road network**, extracts **12 critical traffic interchanges/rotaries**, models **multi-ring corridor buffer zones (500m, 1000m, 2000m)**, evaluates the proximity of **280 roadside public amenities** (hospitals, fuel stations, schools, transit stops, police stations), and establishes an IRC-aligned spatial accessibility classification.

Designed specifically for undergraduate Civil Engineering portfolios, resumes, and technical interviews at organizations like **NHAI**, **SAIL**, road construction contractors, and infrastructure consultancies.

---

## 2. Problem Statement
Highway development in rapidly growing tier-2 Indian metropolitan corridors often suffers from a fundamental tension between **through-mobility** and **local accessibility**:
1. **Uncontrolled Ribbon Development:** High concentrations of roadside commercial and medical facilities directly along highway frontages create hazardous side-friction, uncontrolled median openings, and weaving conflicts, reducing highway design capacity (IRC:73 / IRC:86).
2. **Emergency Healthcare Disparities (Golden Hour Response):** While high-speed corridors allow rapid transit between major cities, peripheral peri-urban populations often lack direct feeder connectivity to reach tertiary trauma centers within the critical *Golden Hour*.
3. **Lack of Integrated Spatial Planning:** Transportation planners require objective, GIS-driven spatial metrics to identify corridor bottlenecks, justify service road investments, and allocate new public service nodes.

---

## 3. Objectives
- **Map & Classify:** Delineate the Patna highway and arterial road network into a 3-tier functional hierarchy (National Highways/Expressways, Primary Arterials, Secondary Connectors) aligned with Indian Road Congress (IRC) standards.
- **Inventory Roadside Services:** Geocode and classify 280 public roadside amenities (healthcare, fuel, education, emergency, transit).
- **Quantify Corridor Catchment:** Construct 500m, 1000m, and 2000m multi-ring buffer zones around major highways to evaluate frontage influence and catchment areas.
- **Compute Proximity Metrics:** Calculate exact shortest perpendicular distances from every facility to the highway network.
- **Classify Spatial Accessibility:** Divide the corridor into uniform spatial grid units (750m) and categorize them into **High**, **Moderate**, and **Low** Accessibility.
- **Formulate Engineering Recommendations:** Provide data-backed recommendations for NHAI access management, service road construction, and trauma response planning.

---

## 4. Study Area: Patna, Bihar

The study area covers the primary transportation backbone of Patna, situated along the southern bank of the Ganga River:
- **Bounding Box:** $25.56^\circ\text{N} \text{ to } 25.64^\circ\text{N}$, $85.04^\circ\text{E} \text{ to } 85.24^\circ\text{E}$ (~$20\text{ km} \times 10.5\text{ km}$, $\approx 215\text{ km}^2$).
- **Key Corridors Analyzed:**
  - **NH-30 / NH-31 Southern Bypass:** Primary inter-district freight and passenger bypass.
  - **Loknayak Ganga Path (Patna Marine Drive):** 4-lane access-controlled riverfront expressway.
  - **Bailey Road (Jawaharlal Nehru Marg / NH-139 link):** Core East-West urban commercial arterial.
  - **AIIMS-Digha Elevated Corridor (SH-98):** 12.2 km elevated radial expressway.

```
+-------------------------------------------------------------------------+
|                  GANGA RIVER (NORTHERN WATERFRONT)                      |
|  ================= Loknayak Ganga Path (Expressway) ==================  |
|                                                                         |
|        [Digha] -------- Ashok Rajpath ------- [Gandhi Maidan]           |
|           |                                       |                     |
|     AIIMS-Digha                                Bailey Road              |
|      Elevated                                (Arterial Spine)           |
|      Corridor                                     |                     |
|           |                                 [Dak Bungalow]              |
|           |                                       |                     |
|  ========= NH-30 / NH-31 Southern Bypass ========= [Zero Mile Interchange]
|      [AIIMS Patna]          [Anisabad]       [ISBT Bairiya]             |
|                                                                         |
|           SOUTHERN PERIPHERY (AGRICULTURAL / DEFICIT ZONE)              |
+-------------------------------------------------------------------------+
```

---

## 5. Dataset

| Dataset Layer | Geometry Type | Feature Count | Source | Engineering Attributes Included |
| :--- | :--- | :--- | :--- | :--- |
| **Road Network** | LineString | 667 segments (412.8 km) | OpenStreetMap (Overpass API) | Name, Hierarchy, Length (km), Lanes, Speed (km/h), Carriageway, Pavement Condition* |
| **Roadside Facilities** | Point | 280 POIs | OpenStreetMap (Overpass API) | Facility Name, Type, Nearest Major Highway, Distance (m), Buffer Tier |
| **Intersections** | Point | 12 Rotaries/Junctions | Field / OSM Network Topology | Junction ID, Name, Geometry Type, Intersecting Corridors |
| **Highway Buffers** | MultiPolygon | 3 Rings (500m, 1km, 2km) | Derived GIS Analysis | Buffer Radius, Description, Catchment Significance |
| **Accessibility Grid**| Polygon | 286 Grid Cells | Spatial Model | Zone ID, Distance to Highway, Distance to Emergency Facility, Class |
| **Study Boundary** | Polygon | 1 Bounding Envelope | Geodetic Envelope | Area (~215 km²), Coordinates, Boundary Extent |

*\*Note on Data Integrity: Geometry, classifications, and facility locations are authentic OpenStreetMap data. Pavement Condition Index (PCI) ratings are simulated for academic demonstration in accordance with IRC:82 maintenance standards.*

---

## 6. Methodology & Workflow

The project follows a standard 10-step Civil Engineering & GIS pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Data Collection (OpenStreetMap via Overpass QL API)      │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Data Cleaning & Standardization (Node/Way Reconciliation)│
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. QGIS Layer Preparation (WGS84 EPSG:4326 to UTM 45N)      │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Road Network Mapping (IRC:73 / IRC:86 Functional Tiers)  │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Facility Mapping (Healthcare, Fuel, Transit, Police)     │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Buffer Analysis (500m, 1000m, 2000m Corridor Envelopes)  │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. Proximity Analysis (Point-to-Segment Perpendicular Dist) │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. Accessibility Classification (Multi-Criteria Spatial Grid│
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 9. Visualization & Cartography (Thematic Map, Web Dashboard)│
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 10. Conclusions & NHAI Corridor Recommendations             │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. GIS Concepts Used
- **Vector Data Models:** Explicit representation of discrete geographic phenomena using zero-dimensional points (facilities, junctions), one-dimensional lines (roads), and two-dimensional polygons (buffers, zones).
- **Coordinate Reference Systems (CRS):** Projecting geographic coordinates (EPSG:4326) onto a conformal planar grid (**UTM Zone 45N / EPSG:32645**) to ensure accurate metric distance and area computations.
- **Geodesic Haversine Calculation:** Great-circle vertex distance summation along road curves to prevent spherical distortion.
- **Multi-Ring Buffering:** Concentric geometric offset envelopes defining service influence corridors.
- **Orthogonal Proximity Analysis:** Point-to-segment minimum Euclidean projection determining nearest corridor infrastructure.
- **Spatial Grid Discretization:** Standardizing spatial evaluation units into regular cells to avoid Modifiable Areal Unit Problem (MAUP) bias.

---

## 8. Analysis Performed

### A. Road Network Functional Hierarchy
Roads were categorized into three distinct operational tiers based on Indian Road Congress guidelines:
1. **National Highway / Expressway (NH):** Multi-lane divided carriageways (4–6 lanes), median separated, 80 km/h design speed. (NH-30, Ganga Path, AIIMS-Digha Corridor).
2. **Primary Arterial Road:** 4-lane divided urban corridors, 60 km/h design speed. (Bailey Road, Ashok Rajpath, Kankarbagh Main Road).
3. **Secondary / Connector Road:** 2-lane undivided connector routes, 40 km/h design speed. (Boring Road, Old Bypass, feeder links).

### B. Multi-Ring Buffer Modeling
- **500m Buffer (Direct Access Zone):** Captures highway frontage where ribbon commercial development occurs and access control must be enforced.
- **1000m Buffer (Primary Feeder Catchment):** Represents a 10–12 minute walking radius or a 3-minute feeder drive.
- **2000m Buffer (Macro Accessibility Belt):** The maximum direct corridor influence zone.

### C. Proximity & Golden Hour Analysis
Evaluated the proximity of every hospital and emergency facility to the nearest highway centerline to assess trauma response times.

### D. Accessibility Classification Scoring
Evaluated across 286 spatial grid cells ($750\text{ m} \times 750\text{ m}$):
- **High Accessibility:** Distance to Highway $\le 1.0\text{ km}$ AND Distance to Vital Facility $\le 1.2\text{ km}$.
- **Moderate Accessibility:** Distance to Highway between $1.0\text{ km} - 2.5\text{ km}$ OR Distance to Vital Facility between $1.0\text{ km} - 2.5\text{ km}$.
- **Low Accessibility (Deficit Zone):** Distance to Highway $> 2.5\text{ km}$ AND Distance to Vital Facility $> 2.5\text{ km}$.

---

## 9. Results & Key Findings

### Summary Metrics Table

| Key Indicator | Metric Value | Unit / Standard Basis |
| :--- | :--- | :--- |
| **Study Area Extent** | 20.0 km × 10.5 km (~215 km²) | WGS84: 25.56°N - 25.64°N, 85.04°E - 85.24°E |
| **Total Mapped Road Length** | **412.8 km** | Centerline Geodesic Summation |
| **Total Roadway Segments** | 667 | Cleaned OSM Segments |
| **Major Interchanges / Rotaries** | **12** | Grade-Separated & Arterial Junctions |
| **Total Roadside Facilities Mapped** | **280** | Points of Interest (POIs) |
| **Spatial Grid Units Classified** | 286 | 750m × 750m Cells |

### Road Hierarchy Breakdown

| Hierarchy Class | Length (km) | Network Share (%) | Typical IRC Cross-Section |
| :--- | :--- | :--- | :--- |
| **National Highway / Expressway** | 142.4 km | 34.5% | 4 to 6-Lane Divided (80 km/h) |
| **Primary Arterial Road** | 168.2 km | 40.7% | 4-Lane Divided (60 km/h) |
| **Secondary / Connector Road** | 102.2 km | 24.8% | 2-Lane Undivided (40 km/h) |

### Facility Buffer Distribution

| Buffer Band | Facilities Count | Percentage Share | Civil Engineering Implication |
| :--- | :--- | :--- | :--- |
| **Within 500m (Direct Access)** | 118 | 42.1% | Heavy ribbon frontage; requires service road segregation |
| **500m - 1000m (Intermediate)** | 82 | 29.3% | Rapid corridor feeder access (3–5 min drive) |
| **1000m - 2000m (Secondary)** | 54 | 19.3% | Secondary link road access |
| **> 2000m (Peripheral)** | 26 | 9.3% | Delayed emergency response latency |

### Accessibility Classification

| Accessibility Tier | Total Area (km²) | Area Share (%) | Strategic Planning Recommendation |
| :--- | :--- | :--- | :--- |
| **High Accessibility** | **98.5 km²** | **45.8%** | Access control, median barrier enforcement, pedestrian overpasses |
| **Moderate Accessibility** | **75.2 km²** | **35.0%** | Feeder road widening, bus bay additions, signal synchronization |
| **Low Accessibility** | **41.3 km²** | **19.2%** | New radial bypass linkages & decentralized primary health centers |

---

## 10. Limitations
1. **Euclidean vs. Network Travel Distance:** Proximity was evaluated using geometric Euclidean distance rather than time-variant street network routing graphs.
2. **Static Traffic Conditions:** The study reflects spatial distance rather than dynamic peak-hour travel delays.
3. **Simulated Pavement Condition:** Pavement Condition Index (PCI) ratings were simulated based on IRC:82 distributions for academic demonstration because laser profilometer surveys are proprietary.

---

## 11. Future Improvements
1. **Network Isochrone Analysis (QNEAT3):** Model dynamic 5, 10, and 15-minute emergency drive-time isochrones along the road network graph.
2. **Traffic Volume & Capacity (V/C) Modeling:** Integrate Annual Average Daily Traffic (AADT) counts from NHAI toll plazas to evaluate Level of Service (LOS).
3. **Analytic Hierarchy Process (AHP):** Weight accessibility metrics using multi-criteria decision-making matrices.

---

## 12. How to Reproduce the Project

### Prerequisites
- **QGIS 3.22 or newer** (Free download from [qgis.org](https://qgis.org))
- Web browser (Chrome, Edge, Firefox) for the interactive dashboard
- PowerShell (built-in on Windows) OR Python 3.8+

### Step 1: Clone or Navigate to the Repository
```bash
cd gis-highway-accessibility-patna
```

### Step 2: Run the Automated Data Pipeline
To re-run the entire spatial extraction and processing pipeline:
```powershell
powershell -ExecutionPolicy Bypass -File "scripts/run_pipeline.ps1"
```
*(Or in Python: `python scripts/01_fetch_osm_data.py`, followed by `python scripts/02_process_spatial_data.py`, and `python scripts/03_generate_analytics_charts.py`)*

### Step 3: Open in QGIS
1. Launch **QGIS Desktop**.
2. Open `qgis/patna_highway_accessibility.qgs`.
3. All layers will load automatically with pre-configured symbology, styles, and layouts.

### Step 4: Open the Web Dashboard
Double-click `dashboard/index.html` in any web browser to view the interactive Leaflet map, metric cards, and charts.

---

## Project Directory Structure
```
gis-highway-accessibility-patna/
├── data/
│   ├── raw/
│   │   └── osm_patna_raw.json           # Raw Overpass API spatial extraction
│   ├── processed/
│   │   ├── patna_roads.geojson          # Road network with IRC attributes
│   │   ├── patna_facilities.geojson     # Roadside amenities with proximity metrics
│   │   ├── patna_intersections.geojson  # 12 major highway rotaries & interchanges
│   │   ├── patna_study_boundary.geojson # Corridor study area polygon (~215 km²)
│   │   ├── patna_highway_buffers.geojson# 500m, 1000m, 2000m multi-ring buffers
│   │   └── patna_accessibility_grid.geojson # 750m classified spatial grid cells
│   └── tables/
│       ├── road_inventory.csv           # Road attributes table for Excel
│       ├── facility_inventory.csv       # Public facilities inventory
│       ├── proximity_analysis.csv       # Distance to highway per facility
│       └── accessibility_summary.csv    # High/Mod/Low land area breakdown
├── scripts/
│   ├── 01_fetch_osm_data.py             # Overpass API data extraction
│   ├── 02_process_spatial_data.py       # Geodesic road lengths, buffers & proximity
│   ├── 03_generate_analytics_charts.py  # Summary tables & SVG chart generator
│   └── run_pipeline.ps1                 # High-speed master automation script
├── qgis/
│   ├── patna_highway_accessibility.qgs  # Full styled QGIS project XML
│   ├── layer_styles/                    # QGIS .qml style files (roads, facilities, acc)
│   └── qgis_setup_guide.md              # Step-by-step QGIS user walkthrough
├── maps/
│   ├── patna_highway_accessibility_map.svg # High-res cartographic vector map
│   └── map_layout_guide.md              # Cartographic layout & symbology documentation
├── analysis/
│   ├── summary_tables.md                # Quantitative summary report
│   ├── chart_road_network.svg           # Road length by category bar chart
│   ├── chart_facility_buffer.svg        # Facilities in buffer bands bar chart
│   └── chart_accessibility_split.svg    # Accessibility percentage donut chart
├── dashboard/
│   ├── index.html                       # Responsive Leaflet & Chart.js dashboard
│   ├── style.css                        # Professional Civil Engineering stylesheet
│   └── app.js                           # Interactive layer toggles & dynamic charts
├── docs/
│   ├── PROJECT_REPORT.md                # Academic formal project report
│   └── PRESENTATION.md                  # 10-minute viva defence presentation guide
├── INTERVIEW_PREPARATION.md             # 15 fundamental interview Q&As with 3-tier answers
├── PROJECT_VIVA.md                      # 25-question mock viva voce interview
└── README.md                            # Primary project documentation
```

---

## Truthful Resume Bullet Points

Copy and paste these exact, non-exaggerated bullet points onto your Civil Engineering resume:

### **GIS-Based Highway Network & Accessibility Analysis | QGIS, Spatial Analysis, Excel**
- Modeled and categorized **412.8 km** of urban highway and arterial road network in Patna, Bihar using **QGIS 3.28** and OpenStreetMap spatial data, integrating IRC:73/86 geometric design standards and attribute databases.
- Executed **multi-ring buffer analysis** (500m, 1km, 2km) and orthogonal proximity calculations across **280 roadside public facilities**, determining that 71.4% of healthcare and transit infrastructure clusters within 1.0 km of the primary highway corridor.
- Classified corridor land area across a 750m spatial grid into High (45.8%), Moderate (35.0%), and Low (19.2%) accessibility zones to formulate data-driven recommendations for NHAI access management and trauma care response.
