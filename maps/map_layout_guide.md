# Cartographic Design & Map Layout Guide

This guide documents the cartographic standards and civil engineering conventions applied in the design of the **Patna Highway Network & Accessibility Map**.

---

## 1. Essential Map Elements (Cartographic Checklist)
As required for professional engineering submittals, portfolio presentations, and academic evaluations, the map contains:

1. **Title Block**:
   - Primary Title: *"GIS-Based Highway Network & Accessibility Analysis"*
   - Subtitle: Details the study area (Patna Urban & Peri-Urban Corridor, Bihar), key highway corridors (NH-30, Ganga Path, Bailey Road), and academic context.
2. **Visual Hierarchy & Symbology**:
   - **National Highways / Expressways**: Prominent 5.5px amber stroke (`#d97706`), reflecting primary arterial importance and high design speed (80 km/h).
   - **Primary Arterial Roads**: 3.5px royal blue stroke (`#2563eb`), signifying major multi-lane city linkages (60 km/h).
   - **Secondary / Connector Roads**: 2px dashed slate gray (`#64748b`), showing intermediate access roads (40 km/h).
3. **Point Features (Roadside Facilities)**:
   - Color-coded by function to avoid visual clutter:
     - Red circle (`#dc2626`): Hospitals & Trauma Centers
     - Amber diamond (`#f59e0b`): Fuel & Petrol Stations
     - Teal square (`#0d9488`): Bus Terminals & Transit Hubs
     - Purple circle (`#7c3aed`): Police Stations & Highway Patrol
     - Gold rotary with dark border (`#facc15`): Major Highway Interchanges / Roundabouts
4. **Buffer Zones**:
   - Translucent multi-ring concentric bands (500m green, 1000m orange, 2000m blue) showing service road frontage and accessibility catchment.
5. **Accessibility Background Tint**:
   - Forest green (`#dcfce7`): High Accessibility
   - Soft amber (`#fef3c7`): Moderate Accessibility
   - Soft red (`#fee2e2`): Low Accessibility Deficit Zone
6. **Cartographic Controls**:
   - **North Arrow**: Clear, standard engineering orientation indicator.
   - **Scale Bar**: Metric alternating bar calibrated to $1:75,000$ scale ($0 - 2.5 - 5.0 - 7.5 - 10.0\text{ km}$).
   - **Coordinate Reference System**: Explicitly stated as WGS 84 / UTM Zone 45N (`EPSG:32645`).
   - **Data Source Citation**: OpenStreetMap contributors (ODbL) with explicit attribution for simulated pavement condition attributes.

---

## 2. Civil Engineering Interpretation for NHAI & Infrastructure Panels

When presenting this map in an interview, point out:
- **Corridor Ribbon Development**: Notice how healthcare and fueling infrastructure heavily cluster within the 500m buffer of the NH-30 Bypass and Bailey Road.
- **Access Management Needs (IRC:73 / MoRTH)**: Explain that while high facility concentration along the highway improves emergency response, it also generates dangerous side friction and weaving maneuvers if direct driveway cuts are permitted instead of regulated service/frontage roads.
- **Accessibility Deficit in the Southern & Eastern Periphery**: Point to the red-tinted zones south of the bypass where travel times to emergency trauma centers exceed 15–20 minutes, justifying proposed radial feeder roads or new primary health center investments.
