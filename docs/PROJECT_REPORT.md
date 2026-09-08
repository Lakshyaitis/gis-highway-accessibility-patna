# Project Report: GIS-Based Highway Network & Accessibility Analysis

**Study Area:** Patna Urban & Peri-Urban Highway Corridor, Bihar, India  
**Academic Level:** Undergraduate B.Tech Civil Engineering Portfolio Project  
**Target Applications:** National Highways Authority of India (NHAI), Infrastructure Consulting, State PWD, Urban Transport Authorities  
**Author:** B.Tech Civil Engineering Candidate  
**Software Stack:** QGIS 3.28 LTR, Python (Geodetic Analysis), OpenStreetMap Overpass API, Leaflet.js  
**Coordinate Reference System:** WGS 84 (EPSG:4326) / Projected UTM Zone 45N (EPSG:32645)

---

## Executive Summary

Highway infrastructure is the primary catalyst for economic development, regional freight movement, and public accessibility. However, unplanned ribbon development and uncoordinated roadside infrastructure frequently impair corridor mobility while leaving peripheral populations with inadequate emergency access.

This project delivers a comprehensive GIS-based evaluation of the highway network and roadside facility accessibility across the **Patna Highway Corridor, Bihar** (~215 km² study area encompassing NH-30 Bypass, Loknayak Ganga Path / Patna Marine Drive, and the Bailey Road arterial spine). Using OpenStreetMap spatial datasets and standard geodetic spatial analysis in QGIS, the project maps 667 road segments (totaling 412.8 km), categorizes road functional hierarchies according to Indian Road Congress (IRC:73 / IRC:86) specifications, extracts key traffic friction nodes (12 major interchanges and rotaries), and evaluates the proximity of 280 roadside public facilities (hospitals, fuel stations, educational institutions, police stations, and transit terminals).

Through multi-ring buffer analysis (500m, 1000m, 2000m) and a multi-criteria spatial accessibility classification, the study identifies that:
1. **71.4% of major healthcare and trauma facilities** cluster within 1.0 km of primary highway spines, facilitating rapid emergency access along the corridor.
2. **45.8% of the study area land** exhibits **High Accessibility** (under 1.0 km to a major highway and under 1.2 km to emergency infrastructure).
3. **19.2% of the peripheral territory** suffers from an **Accessibility Deficit (Low Accessibility)**, requiring strategic radial feeder linkages and decentralized emergency service facilities.

---

## 1. Introduction & Problem Statement

### 1.1 Background
The National Highways Authority of India (NHAI) and state road development corporations face dual challenges in highway corridor planning:
- **Corridor Throughput & Mobility:** Ensuring high-speed, unimpeded vehicular flow on trunk routes.
- **Local Accessibility & Equity:** Providing surrounding communities and roadside developments with safe, convenient access to public facilities without causing uncontrolled roadside friction.

In rapidly growing tier-2 urban agglomerations like Patna, high-density residential and commercial expansion has outpaced arterial road planning. While major expressways (such as the Loknayak Ganga Path and NH-30 Southern Bypass) handle high traffic volumes, accessibility to vital roadside services—particularly **emergency healthcare (Golden Hour response)**, refueling logistics, and multi-modal transit interchange—varies significantly across space.

### 1.2 Project Objectives
1. Map and categorize the Patna highway network into an IRC-aligned functional hierarchy using GIS.
2. Build an attribute database incorporating road geometry, lanes, design speeds, and simulated pavement condition ratings.
3. Geo-locate vital public roadside facilities and analyze their spatial proximity to the highway network.
4. Model multi-ring buffer zones (500m, 1000m, 2000m) to quantify corridor service capture.
5. Formulate a simple, transparent accessibility classification index to delineate high, moderate, and underserved zones.
6. Provide actionable engineering recommendations for NHAI, road safety authorities, and urban planners.

---

## 2. Study Area Profile: Patna, Bihar

Patna, the capital of Bihar, is situated on the southern bank of the Ganga River. The study area covers an East-West corridor spanning approximately 20 km and a North-South extent of 10.5 km (Latitude 25.56°N to 25.64°N, Longitude 85.04°E to 85.24°E).

### Key Corridors Analyzed:
- **NH-30 / NH-31 Bypass:** The critical east-west regional freight bypass connecting Didarganj/Zero Mile to Anisabad and Phulwari Sharif, diverting inter-state freight away from the core city.
- **Loknayak Ganga Path (Patna Marine Drive):** High-speed 4-lane access-controlled riverfront expressway designed to relieve northern urban congestion.
- **Bailey Road (Jawaharlal Nehru Marg / NH-139 link):** The primary urban commercial and institutional arterial running east-west from Danapur to Dak Bungalow.
- **AIIMS-Digha Elevated Corridor (SH-98):** Major 12.2 km elevated radial expressway linking northern Patna (Digha) directly to AIIMS and the southern bypass.

---

## 3. Data Collection & Preprocessing

### 3.1 Data Sources
- **Spatial Geometry & Network Topology:** OpenStreetMap (OSM) via the Overpass QL API.
- **Highway Standards & Design Guidelines:** Indian Road Congress (IRC) publications:
  - *IRC:73-1980:* Geometric Design Standards for Rural (Non-Urban) Highways.
  - *IRC:86-1983:* Geometric Design Standards for Urban Roads in Plains.
  - *IRC:37-2018:* Guidelines for the Design of Flexible Pavements.
  - *IRC:82-2015:* Code of Practice for Maintenance of Bituminous Surfaces.

### 3.2 Data Preprocessing Workflow
1. **Extraction:** Queried OSM ways (`highway=trunk|primary|secondary`) and nodes (`amenity=hospital|fuel|police|school|college|bus_station`).
2. **Cleaning & Filtering:** Removed dangling microscopic segments (< 20m) and standardized naming conventions.
3. **Attribute Enrichment:** Assigned functional categories, number of lanes (divided/undivided carriageways), statutory design speed limits, and simulated Pavement Condition Index (PCI) ratings (Good, Fair, Satisfactory) clearly tagged for academic demonstration.
4. **Coordinate Reference System (CRS):** Processed in WGS 84 (EPSG:4326) with metric Euclidean distance calculations projected to UTM Zone 45N (EPSG:32645).

---

## 4. Methodology & GIS Operations

```
[OpenStreetMap Overpass API]
          │
          ▼
[01_fetch_osm_data.py] ──> Raw OSM JSON
          │
          ▼
[02_process_spatial_data.py]
   ├─ Haversine Road Length Calculation
   ├─ Functional Classification (NH, Primary, Secondary)
   ├─ Point-to-Segment Minimum Distance (Proximity Analysis)
   ├─ Multi-Ring Buffer Generation (500m, 1000m, 2000m)
   └─ Accessibility Grid Scoring (750m Cells)
          │
          ├─► GeoJSON Spatial Layers (data/processed/)
          ├─► Tabular CSV Inventories (data/tables/)
          ├─► QGIS 3.28 Project & Thematic Map (qgis/, maps/)
          └─► Interactive Web Dashboard (dashboard/)
```

### 4.1 Geodesic Road Length Calculation
Centerline road lengths were computed by iterating through way vertex coordinates using the Haversine spherical formula:
$$\Delta\sigma = 2 \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)} \right)$$
$$d = R \cdot \Delta\sigma \quad (R = 6,371.0 \text{ km})$$

### 4.2 Multi-Ring Buffer Analysis
Buffer zones around major highways (National Highways and Primary Arterials) were constructed at three distinct radii:
- **500m Buffer:** Immediate Highway Corridor Influence Zone. Evaluates direct access via frontage/service roads and properties prone to ribbon development.
- **1000m Buffer:** Primary Catchment Zone. Represents a 10–12 minute walking threshold or rapid 3-minute vehicular feeder trip.
- **2000m Buffer:** Macro Accessibility Belt. Represents the broader regional catchment served by the highway.

### 4.3 Proximity Analysis (Point-to-Line Nearest Distance)
For each facility $P(x_p, y_p)$, the minimum perpendicular distance to every road segment $AB$ was calculated:
$$t = \max\left(0, \min\left(1, \frac{(P - A) \cdot (B - A)}{\|B - A\|^2}\right)\right)$$
$$\text{Distance} = \|P - (A + t(B - A))\|$$
This identified the exact nearest highway corridor and distance in meters.

### 4.4 Accessibility Classification Index
The study area was discretized into a regular spatial grid. Each cell was classified using transparent, explainable thresholds:
- **High Accessibility:** Distance to Major Highway $\le 1,000\text{ m}$ AND Distance to Vital Emergency Facility $\le 1,200\text{ m}$.
- **Moderate Accessibility:** Distance to Major Highway between $1,000\text{ m} - 2,500\text{ m}$ OR Distance to Vital Facility between $1,000\text{ m} - 2,500\text{ m}$.
- **Low Accessibility (Deficit Zone):** Distance to Major Highway $> 2,500\text{ m}$ AND Distance to Vital Facility $> 2,500\text{ m}$.

---

## 5. Results & Analytical Findings

### 5.1 Road Network Inventory
- **Total Analyzed Road Length:** **412.8 km** across 667 segments.
- **National Highways / Expressways:** 142.4 km (34.5%) — 4 to 6 lanes divided, design speed 80 km/h.
- **Primary Arterial Roads:** 168.2 km (40.7%) — 4 lanes divided, design speed 60 km/h.
- **Secondary / Connector Roads:** 102.2 km (24.8%) — 2 lanes undivided, design speed 40 km/h.
- **Critical Intersections / Rotaries:** 12 major nodes identified (Zero Mile, Mithapur, Digha Rotary, AIIMS Roundabout, Saguna More, Dak Bungalow).

### 5.2 Facility Proximity to Major Highways
Across 280 mapped public facilities:
- **Within 500m (Direct Access):** 118 facilities (42.1%).
- **500m – 1000m (Intermediate Access):** 82 facilities (29.3%).
- **1000m – 2000m (Secondary Access):** 54 facilities (19.3%).
- **> 2000m (Peripheral):** 26 facilities (9.3%).

**Significance:** Over **71.4%** of vital facilities (including AIIMS Patna, Paras HMRI, IGIMS, and major fuel depots) are situated within 1.0 km of a major highway corridor.

### 5.3 Accessibility Classification Breakdown
- **High Accessibility:** **98.5 km² (45.8%)** — Dominates the central urban core and primary highway corridors (NH-30, Bailey Road, Ganga Path).
- **Moderate Accessibility:** **75.2 km² (35.0%)** — Transitional belt accessible via secondary roads and feeder networks.
- **Low Accessibility:** **41.3 km² (19.2%)** — Concentrated in the southern and south-eastern peri-urban fringe, characterized by agricultural expanses and inadequate radial road connectivity.

---

## 6. Engineering Recommendations for NHAI & PWD

1. **Access Management on NH-30 Bypass (IRC:73 Compliance):**
   - High concentration of commercial fuel stations and private hospitals along the bypass causes frequent direct median openings and uncontrolled weaving.
   - **Recommendation:** NHAI should construct dedicated 2-lane grade-separated service roads with physical barrier curbs to eliminate direct access to high-speed express lanes.
2. **Trauma Center "Golden Hour" Linkage:**
   - In highway safety engineering, the *Golden Hour* dictates that critical accident victims reach surgical trauma care within 60 minutes.
   - While AIIMS Patna and PMCH provide excellent level-1 trauma care, accident victims on the eastern stretch of NH-30 (beyond Zero Mile / Fatuha) face severe congestion reaching these centers.
   - **Recommendation:** Establish a dedicated Highway Emergency Care Unit near Zero Mile Interchange with emergency ambulance turnaround lanes.
3. **Radial Connector Development in Low-Accessibility Sectors:**
   - The 19.2% low-accessibility southern zone suffers from poor cross-corridor mobility between NH-30 and rural arterials.
   - **Recommendation:** State PWD / BSRDCL should plan two 4-lane radial bypasses connecting Phulwari Sharif to Gaurichak to disperse traffic before it reaches saturated city junctions.

---

## 7. Limitations

1. **Euclidean vs. Network Shortest Path Distance:** Proximity was calculated using perpendicular Euclidean distance. In actual travel, route circuity, one-way restrictions, and railway crossings introduce network impedance.
2. **Static vs. Time-Variant Congestion:** The study uses geometric distance rather than dynamic peak-hour travel times.
3. **Simulated Condition Ratings:** Pavement Condition Index (PCI) ratings were simulated for academic demonstration in accordance with IRC:82 guidelines, as field laser profilometer data is proprietary.

---

## 8. Future Improvements

1. **Network Analysis in QGIS (QNEAT3):** Perform origin-destination cost matrices and isochrone travel-time maps using true road network graphs.
2. **Traffic Volume (PCU) Integration:** Incorporate Annual Average Daily Traffic (AADT) and Passenger Car Unit (PCU) counts from NHAI toll plazas to evaluate corridor capacity saturation (V/C ratios).
3. **Multi-Criteria Analytic Hierarchy Process (AHP):** Weight accessibility factors using formal multi-criteria decision analysis.

---

## 9. References
- Indian Roads Congress (1980). *IRC:73-1980: Geometric Design Standards for Rural (Non-Urban) Highways*. New Delhi.
- Indian Roads Congress (1983). *IRC:86-1983: Geometric Design Standards for Urban Roads in Plains*. New Delhi.
- Indian Roads Congress (2015). *IRC:82-2015: Code of Practice for Maintenance of Bituminous Surfaces of Roads*. New Delhi.
- Ministry of Road Transport and Highways (MoRTH) (2013). *Specifications for Road and Bridge Works* (5th Revision).
- OpenStreetMap Contributors (2024). *Planet Dump & Overpass API*. Open Data Commons Open Database License (ODbL).
