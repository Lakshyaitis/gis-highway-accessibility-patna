# Mock Viva Voce & Technical Interview Guide: 25 Questions & Answers

**Project Title:** GIS-Based Highway Network & Accessibility Analysis (Patna Corridor)  
**Target Profile:** B.Tech Civil Engineering Candidate  
**Target Roles:** Graduate Engineer Trainee (GET) / Internships at NHAI, SAIL, L&T Infrastructure, RITES, Transport Planning & Management  

---

## Round 1: Core GIS Fundamentals & Coordinate Systems (Basic)

### Question 1: What motivated you to choose a highway accessibility project in Patna?
**Candidate Answer:**  
> *"Patna is currently witnessing major highway infrastructure investments, such as the Loknayak Ganga Path (Patna Marine Drive), the AIIMS-Digha elevated expressway, and the NH-30 bypass expansion. However, rapid commercial growth along these corridors often happens without coordinated access planning. I wanted to apply GIS tools to objectively analyze how well these highway investments serve essential public services like trauma care hospitals and transit hubs, and identify peripheral zones that still suffer from poor connectivity."*

### Question 2: Why did you use QGIS instead of commercial software like ArcGIS?
**Candidate Answer:**  
> *"QGIS is an open-source, industry-standard GIS desktop package supported by the OSGeo Foundation. It provides full functionality for vector analysis, buffering, and map production without costly proprietary licenses. In many government departments, state PWDs, and infrastructure consultancies, QGIS is increasingly preferred for cost-effective, transparent, and reproducible geospatial workflows."*

### Question 3: What is the difference between Geographic and Projected Coordinate Reference Systems?
**Candidate Answer:**  
> *"A Geographic CRS represents locations on a curved 3D spherical Earth using angular units—latitude and longitude in decimal degrees (e.g., WGS 84 / EPSG:4326). A Projected CRS uses mathematical projection formulas to flatten the 3D surface onto a 2D Cartesian plane using linear units, typically meters (e.g., UTM Zone 45N / EPSG:32645 for Bihar). In GIS, we must never calculate distances or areas in degrees because one degree of longitude varies in physical length depending on latitude."*

### Question 4: How did you handle coordinate transformations in this project?
**Candidate Answer:**  
> *"The raw spatial data from OpenStreetMap was retrieved in geographic coordinates (EPSG:4326). To perform metric buffer analysis (500m, 1000m, 2000m) and compute road segment lengths in kilometers, the distance algorithms projected the coordinates to UTM Zone 45N (EPSG:32645), which minimizes conformal distortion for Bihar's geographic belt."*

### Question 5: What is the difference between attributes and spatial geometry in a GIS layer?
**Candidate Answer:**  
> *"Spatial geometry defines the shape and geographic location of a feature using coordinate points, lines, or polygons. Attributes are tabular descriptive properties associated with that specific geometry, stored in a database table. For example, in our road layer, the linestring geometry defines the path of the NH-30 Bypass on the map, while its attribute table records that it is a 4-lane divided highway with an 80 km/h design speed."*

### Question 6: What is a spatial join and how is it different from a regular database join?
**Candidate Answer:**  
> *"A regular relational database join merges two tables based on a common text or numeric key (like a shared `Road_ID`). A spatial join merges two tables based on their geographic spatial relationship—such as containment, intersection, or proximity. For example, joining roadside facilities to highway buffers based on whether the facility point physically falls inside the buffer polygon is a spatial join."*

---

## Round 2: Data Sourcing, Formats & Cleaning (Basic to Intermediate)

### Question 7: Where did you get the road network and facility data? Is it authentic?
**Candidate Answer:**  
> *"The data was extracted directly from OpenStreetMap (OSM) using the Overpass QL API for the Patna bounding box (25.56°N to 25.64°N, 85.04°E to 85.24°E). OSM is a publicly verified, peer-reviewed global geospatial database widely used in academic research and commercial applications. The road centerlines, highway names, and public facilities like AIIMS, PMCH, and Mithapur bus stand are real, physical infrastructure assets in Patna."*

### Question 8: How did you handle roads or facilities that had missing names or tags in OSM?
**Candidate Answer:**  
> *"During data cleaning, I filtered features by primary infrastructure tags (`highway=trunk|primary|secondary` and `amenity=hospital|fuel|police|bus_station`). If a road segment had an official reference code (like `NH-30` or `SH-98`), that was used. If a local name was missing, a standardized systematic identifier (such as `PAT-RD-0142` or `NH Corridor Link`) was assigned to ensure complete relational integrity without fabricating fictional names."*

### Question 9: Why did you include simulated pavement condition data? Did you present it as real?
**Candidate Answer:**  
> *"No, I have clearly labeled the pavement condition ratings as 'Simulated for Academic Demonstration' in accordance with academic integrity guidelines. Real pavement condition surveys require expensive Network Survey Vehicles (NSV) with laser profilometers, which are proprietary to NHAI and contractors. To demonstrate how a civil engineer uses GIS for Pavement Management Systems (PMS), I simulated representative Pavement Condition Index (PCI) ratings—Good, Fair, Satisfactory—distributed according to standard IRC:82 maintenance distributions."*

### Question 10: What is a GeoJSON file? Why did you use it over a Shapefile?
**Candidate Answer:**  
> *"GeoJSON is an open, human-readable data format based on JSON (JavaScript Object Notation) that represents simple geographical features along with their non-spatial attributes. Unlike legacy Shapefiles, which require at least three separate files (`.shp`, `.dbf`, `.shx`) and truncate column names to 10 characters, GeoJSON is stored as a single self-contained text file that can be opened in QGIS, inspected in text editors, and rendered directly in web browsers like Leaflet."*

### Question 11: What is a GeoPackage (`.gpkg`), and what are its advantages?
**Candidate Answer:**  
> *"A GeoPackage is an open, platform-independent SQLite database container defined by the Open Geospatial Consortium (OGC). Its key advantages over Shapefiles include: storing multiple vector layers and raster tables in a single file, supporting unlimited file sizes beyond the 2 GB Shapefile limit, allowing full-length column names without truncation, and having built-in spatial indexing (R-tree) for rapid querying."*

### Question 12: How did you calculate the length of road segments in Python?
**Candidate Answer:**  
> *"I implemented the Haversine formula, which computes the great-circle geodesic distance between consecutive latitude-longitude vertex pairs along each road linestring:
> $$d = 2R \arcsin\left(\sqrt{\sin^2(\Delta\phi/2) + \cos\phi_1\cos\phi_2\sin^2(\Delta\lambda/2)}\right)$$
> where $R = 6,371\text{ km}$. The segment lengths were summed to obtain the total centerline distance in kilometers, filtering out tiny digitized artifacts under 20 meters."*

---

## Round 3: Spatial Analysis & Accessibility Methodology (Intermediate)

### Question 13: Explain what multi-ring buffer analysis is and why you selected 500m, 1000m, and 2000m.
**Candidate Answer:**  
> *"Multi-ring buffering generates multiple concentric distance bands around a feature. In this project, the distances were selected based on Indian highway planning conventions:
> 1. **500m Buffer:** Represents the direct corridor influence zone where roadside facilities rely on service/frontage roads.
> 2. **1000m Buffer:** Represents the primary catchment zone, corresponding to a 10–12 minute walking threshold or a 3-minute feeder drive.
> 3. **2000m Buffer:** Represents the secondary catchment belt, indicating the maximum reasonable influence zone for a highway corridor in an urbanized area."*

### Question 14: What is proximity analysis, and how did you implement it?
**Candidate Answer:**  
> *"Proximity analysis determines the spatial closeness between features. In our script, for every one of the 280 mapped facilities, the algorithm calculated the minimum perpendicular distance from that point to the nearest road segment of the major highway network:
> $$t = \text{clamp}\left(\frac{(P - A) \cdot (B - A)}{\|B - A\|^2}, 0, 1\right), \quad \text{Distance} = \|P - (A + t(B - A))\|$$
> This identified both the name of the nearest highway corridor (e.g., NH-30 Bypass) and the exact distance in meters."*

### Question 15: How did you define and classify 'Accessibility' across the study area?
**Candidate Answer:**  
> *"I designed a transparent, beginner-friendly two-factor accessibility classification model evaluated across a 750m spatial grid:
> - **High Accessibility:** Within 1,000m of a major highway AND within 1,200m of an emergency facility (trauma hospital or police station).
> - **Moderate Accessibility:** Within 1,000m to 2,500m of a highway OR within 1,000m to 2,500m of a facility.
> - **Low Accessibility:** Greater than 2,500m from a major highway AND greater than 2,500m from a vital facility.
> This avoids complicated 'black-box' mathematical models while providing clear, defensible spatial zones."*

### Question 16: What percentage of the study area fell into each accessibility class?
**Candidate Answer:**  
> *"Out of the ~215 km² study area:
> - **High Accessibility:** Covered **45.8%** of the land area (98.5 km²), concentrated along the NH-30, Bailey Road, and Ganga Path corridors.
> - **Moderate Accessibility:** Covered **35.0%** of the land area (75.2 km²), representing the transitional urban-feeder belt.
> - **Low Accessibility:** Covered **19.2%** of the land area (41.3 km²), located mostly in the southern peri-urban and agricultural areas south of the bypass."*

### Question 17: What is the difference between Euclidean distance and network distance? Why did you use Euclidean?
**Candidate Answer:**  
> *"Euclidean distance is the 'as-the-crow-flies' straight-line perpendicular distance, whereas network distance measures the actual shortest path distance constrained along a connected road graph with turn rules and one-way streets. I used Euclidean distance because it serves as an unconstrained geometric benchmark for preliminary corridor catchment screening without requiring high-complexity network topology graphs, making it transparent and easy to defend."*

### Question 18: What is a spatial grid, and why did you use it for accessibility instead of ward boundaries?
**Candidate Answer:**  
> *"A spatial grid divides the study area into uniform, regular geometric squares (750m × 750m) independent of administrative boundaries. Ward or municipal boundaries vary wildly in size and shape, which can introduce statistical bias known as the Modifiable Areal Unit Problem (MAUP). A regular grid provides an objective, standardized unit of measurement across urban, peri-urban, and rural highway fringes."*

### Question 19: How did you extract and map the major highway intersections?
**Candidate Answer:**  
> *"Major highway intersections and rotaries—such as Zero Mile, Mithapur Flyover, Digha Rotary, and AIIMS Roundabout—were identified as critical nodes where two or more major corridors intersect. In traffic engineering, these nodes are primary sources of traffic friction, weaving, and capacity bottlenecks, making them essential points for interchange planning and emergency turnaround access."*

---

## Round 4: Civil Engineering & Practical NHAI Application (Viva Defence)

### Question 20: How does this project relate to the Indian Road Congress (IRC) standards?
**Candidate Answer:**  
> *"The project directly references Indian Road Congress geometric design standards:
> - **IRC:73-1980:** Governs the geometric design of rural highways, specifying carriage-way widths (7.0m for 2-lane, 14.0m for 4-lane divided) and access control guidelines.
> - **IRC:86-1983:** Governs urban arterial designs and design speeds (80 km/h for expressways, 60 km/h for arterials).
> - **IRC:82-2015:** Guides pavement maintenance and condition ratings.
> By aligning the OSM network categories with these IRC codes, the GIS analysis reflects real-world Indian highway engineering practice."*

### Question 21: What is the 'Golden Hour' in highway engineering, and how did your findings relate to it?
**Candidate Answer:**  
> *"In highway safety and trauma engineering, the 'Golden Hour' refers to the first 60 minutes following a severe traumatic injury during which prompt surgical intervention can prevent mortality. Our proximity analysis revealed that **71.4% of all public facilities and hospitals** (including AIIMS Patna and IGIMS) are located within 1.0 km of the highway network. While this provides excellent Golden Hour response along the central bypass, the 19.2% peripheral deficit zone faces travel times exceeding 15–20 minutes, demonstrating a clear spatial gap in trauma care distribution."*

### Question 22: What is ribbon development, and what does your buffer analysis reveal about it on NH-30?
**Candidate Answer:**  
> *"Ribbon development is the unplanned, linear sprawling of commercial buildings, petrol pumps, and institutions directly along highway frontages. Our 500m buffer analysis showed that **42.1% of all facilities** are concentrated directly within 500 meters of the highway. While convenient for motorists, direct driveway cuts create dangerous speed differentials and side-friction on 80 km/h highways. This provides empirical justification for NHAI to mandate continuous grade-separated service roads."*

### Question 23: How can NHAI use this analysis for Wayside Amenities planning?
**Candidate Answer:**  
> *"NHAI has a formal policy to develop Wayside Amenities (fuel, food plazas, restrooms, truck parking) every 40 to 50 km along National Highways. By using GIS proximity and buffer analysis, NHAI planners can identify underserved highway stretches where fuel or repair facilities are absent, prioritize land acquisition for new amenities, and ensure that entry/exit ramps have sufficient acceleration and deceleration lanes."*

### Question 24: If an NHAI interviewer asks you: 'What is the biggest weakness of this project?', what would you say?
**Candidate Answer:**  
> *"I would truthfully say that the biggest limitation is the use of static Euclidean distance rather than time-variant network travel time. In Patna, traffic congestion during morning and evening rush hours significantly increases travel times on routes like Bailey Road or the Old Bypass, meaning that physical distance does not always equal travel time. With more time, I would incorporate a QGIS network routing graph with peak-hour speed data to model dynamic isochrones."*

### Question 25: How would you summarize what this project taught you in 30 seconds?
**Candidate Answer:**  
> *"This project taught me how to take raw, publicly available spatial data, clean and structure it according to Indian Civil Engineering standards, and use GIS spatial analysis—specifically buffering, proximity modeling, and accessibility zoning—to make defensible infrastructure planning decisions. It proved to me that GIS is not just about making pretty maps, but an indispensable analytical tool for highway design, corridor safety, and emergency response planning."*
