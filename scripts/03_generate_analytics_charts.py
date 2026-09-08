"""
===============================================================================
PROJECT: GIS-Based Highway Network & Accessibility Analysis (Patna, Bihar)
SCRIPT: 03_generate_analytics_charts.py
PURPOSE: Computes final civil engineering analytical metrics and generates:
         1. Comprehensive summary tables (Markdown & CSV)
         2. High-resolution standalone vector SVG charts for project portfolio:
            - Road Network Length by Category
            - Facility Distribution across Highway Buffer Zones
            - Study Area Accessibility Classification Split
===============================================================================
"""

import os
import json
import csv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
TABLES_DIR = os.path.join(PROJECT_ROOT, "data", "tables")
ANALYSIS_DIR = os.path.join(PROJECT_ROOT, "analysis")

os.makedirs(ANALYSIS_DIR, exist_ok=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_svg_bar_chart(title, subtitle, labels, values, colors, unit, output_path):
    """
    Generates a crisp, publication-grade SVG horizontal bar chart without external libraries.
    """
    width = 750
    bar_height = 36
    gap = 24
    top_offset = 90
    left_offset = 240
    chart_width = 420
    height = top_offset + len(labels) * (bar_height + gap) + 50

    max_val = max(values) if values and max(values) > 0 else 1.0

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}" style="background:#ffffff; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif;">',
        '  <!-- Background Card -->',
        f'  <rect x="0" y="0" width="{width}" height="{height}" rx="10" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>',
        f'  <text x="30" y="42" font-size="20" font-weight="700" fill="#1e293b">{title}</text>',
        f'  <text x="30" y="66" font-size="13" font-weight="400" fill="#64748b">{subtitle}</text>',
    ]

    for i, (label, val, color) in enumerate(zip(labels, values, colors)):
        y = top_offset + i * (bar_height + gap)
        bar_w = round((val / max_val) * chart_width, 1)

        # Label
        svg_lines.append(f'  <text x="{left_offset - 15}" y="{y + 23}" font-size="13" font-weight="600" fill="#334155" text-anchor="end">{label}</text>')
        # Background bar
        svg_lines.append(f'  <rect x="{left_offset}" y="{y}" width="{chart_width}" height="{bar_height}" rx="6" fill="#f1f5f9" />')
        # Filled bar
        svg_lines.append(f'  <rect x="{left_offset}" y="{y}" width="{bar_w}" height="{bar_height}" rx="6" fill="{color}" />')
        # Value text
        val_display = f"{val:g} {unit}" if isinstance(val, (int, float)) else f"{val} {unit}"
        svg_lines.append(f'  <text x="{left_offset + bar_w + 12}" y="{y + 23}" font-size="13" font-weight="700" fill="#0f172a">{val_display}</text>')

    svg_lines.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))
    print(f"[SAVED] SVG Chart: {output_path}")


def generate_svg_donut_chart(title, subtitle, categories, percentages, areas, colors, output_path):
    """
    Generates an SVG donut breakdown chart for Accessibility Classification.
    """
    width = 750
    height = 360
    cx, cy, r_out, r_in = 200, 195, 115, 65

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}" style="background:#ffffff; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif;">',
        f'  <rect x="0" y="0" width="{width}" height="{height}" rx="10" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>',
        f'  <text x="30" y="42" font-size="20" font-weight="700" fill="#1e293b">{title}</text>',
        f'  <text x="30" y="66" font-size="13" font-weight="400" fill="#64748b">{subtitle}</text>',
    ]

    import math
    current_angle = -90.0  # Start at top

    for cat, pct, area, col in zip(categories, percentages, areas, colors):
        angle_span = (pct / 100.0) * 360.0
        start_rad = math.radians(current_angle)
        end_rad = math.radians(current_angle + angle_span)

        x1_out = cx + r_out * math.cos(start_rad)
        y1_out = cy + r_out * math.sin(start_rad)
        x2_out = cx + r_out * math.cos(end_rad)
        y2_out = cy + r_out * math.sin(end_rad)

        x1_in = cx + r_in * math.cos(end_rad)
        y1_in = cy + r_in * math.sin(end_rad)
        x2_in = cx + r_in * math.cos(start_rad)
        y2_in = cy + r_in * math.sin(start_rad)

        large_arc = 1 if angle_span > 180 else 0

        path_data = (f"M {x1_out:.2f} {y1_out:.2f} "
                     f"A {r_out} {r_out} 0 {large_arc} 1 {x2_out:.2f} {y2_out:.2f} "
                     f"L {x1_in:.2f} {y1_in:.2f} "
                     f"A {r_in} {r_in} 0 {large_arc} 0 {x2_in:.2f} {y2_in:.2f} Z")

        svg_lines.append(f'  <path d="{path_data}" fill="{col}" stroke="#ffffff" stroke-width="2.5"/>')
        current_angle += angle_span

    # Center label in donut
    svg_lines.append(f'  <text x="{cx}" y="{cy - 5}" font-size="14" font-weight="700" fill="#0f172a" text-anchor="middle">TOTAL AREA</text>')
    total_area_val = sum(areas)
    svg_lines.append(f'  <text x="{cx}" y="{cy + 18}" font-size="13" font-weight="500" fill="#64748b" text-anchor="middle">{total_area_val:.1f} sq km</text>')

    # Legend on the right side
    leg_x = 380
    leg_y_start = 125
    for i, (cat, pct, area, col) in enumerate(zip(categories, percentages, areas, colors)):
        ly = leg_y_start + i * 55
        svg_lines.append(f'  <circle cx="{leg_x}" cy="{ly}" r="9" fill="{col}"/>')
        svg_lines.append(f'  <text x="{leg_x + 22}" y="{ly + 5}" font-size="15" font-weight="700" fill="#1e293b">{cat} ({pct:.1f}%)</text>')
        svg_lines.append(f'  <text x="{leg_x + 22}" y="{ly + 24}" font-size="13" font-weight="400" fill="#64748b">Area: {area:.2f} km²</text>')

    svg_lines.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))
    print(f"[SAVED] SVG Donut Chart: {output_path}")


def main():
    roads_data = load_json(os.path.join(PROCESSED_DIR, "patna_roads.geojson"))
    fac_data = load_json(os.path.join(PROCESSED_DIR, "patna_facilities.geojson"))
    jct_data = load_json(os.path.join(PROCESSED_DIR, "patna_intersections.geojson"))
    acc_data = load_json(os.path.join(PROCESSED_DIR, "patna_accessibility_grid.geojson"))

    # 1. Road Network Analytics
    total_road_length = 0.0
    road_lengths_by_cat = {
        "National Highway / Expressway": 0.0,
        "Primary Arterial Road": 0.0,
        "Secondary / Connector Road": 0.0
    }
    road_counts_by_cat = {k: 0 for k in road_lengths_by_cat}

    for feat in roads_data["features"]:
        cat = feat["properties"]["category"]
        length = feat["properties"]["length_km"]
        total_road_length += length
        if cat in road_lengths_by_cat:
            road_lengths_by_cat[cat] += length
            road_counts_by_cat[cat] += 1

    total_road_length = round(total_road_length, 2)
    for k in road_lengths_by_cat:
        road_lengths_by_cat[k] = round(road_lengths_by_cat[k], 2)

    # 2. Facility Analytics
    total_facilities = len(fac_data["features"])
    fac_by_type = {}
    fac_by_buffer = {"Within 500m": 0, "500m - 1000m": 0, "1000m - 2000m": 0, "> 2000m": 0}

    for feat in fac_data["features"]:
        ftype = feat["properties"]["facility_type"]
        fac_by_type[ftype] = fac_by_type.get(ftype, 0) + 1

        dist = feat["properties"]["distance_to_highway_m"]
        if dist <= 500:
            fac_by_buffer["Within 500m"] += 1
        elif dist <= 1000:
            fac_by_buffer["500m - 1000m"] += 1
        elif dist <= 2000:
            fac_by_buffer["1000m - 2000m"] += 1
        else:
            fac_by_buffer["> 2000m"] += 1

    # 3. Accessibility Breakdown
    acc_areas = {"High Accessibility": 0.0, "Moderate Accessibility": 0.0, "Low Accessibility": 0.0}
    acc_counts = {k: 0 for k in acc_areas}

    for feat in acc_data["features"]:
        aclass = feat["properties"]["accessibility_class"]
        area = feat["properties"]["area_sq_km"]
        if aclass in acc_areas:
            acc_areas[aclass] += area
            acc_counts[aclass] += 1

    total_study_area = sum(acc_areas.values())
    acc_pcts = {k: round((acc_areas[k] / total_study_area) * 100.0, 1) for k in acc_areas}

    # 4. Generate Markdown Summary Report
    summary_md_path = os.path.join(ANALYSIS_DIR, "summary_tables.md")
    with open(summary_md_path, "w", encoding="utf-8") as f:
        f.write("# Patna Highway Network & Accessibility Analysis: Summary Metrics\n\n")
        f.write("## 1. Study Area Infrastructure Overview\n\n")
        f.write("| Key Indicator | Metric Value | Unit / Standard Basis |\n")
        f.write("| :--- | :--- | :--- |\n")
        f.write(f"| **Study Area Extent** | 20.0 km × 10.5 km (~180 km²) | WGS84: 25.56°N - 25.64°N, 85.04°E - 85.24°E |\n")
        f.write(f"| **Total Mapped Road Length** | **{total_road_length}** | Kilometers (Centerline Geodesic) |\n")
        f.write(f"| **Total Highway / Arterial Segments** | {len(roads_data['features'])} | OSM Way Segments |\n")
        f.write(f"| **Major Highway Intersections / Rotaries** | **{len(jct_data['features'])}** | Grade-Separated & Major Surface Junctions |\n")
        f.write(f"| **Total Roadside Public Facilities Mapped** | **{total_facilities}** | Point Features (Hospitals, Fuel, Police, etc.) |\n")
        f.write(f"| **Total Classified Spatial Grid Cells** | {len(acc_data['features'])} | 750m × 750m Resolution Analysis Units |\n\n")

        f.write("## 2. Road Network Breakdown by Functional Category\n\n")
        f.write("| Functional Road Category | Length (km) | Share (%) | Segments | Typical IRC Cross-Section & Speed |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for cat in ["National Highway / Expressway", "Primary Arterial Road", "Secondary / Connector Road"]:
            l = road_lengths_by_cat[cat]
            pct = round((l / total_road_length) * 100.0, 1)
            c = road_counts_by_cat[cat]
            cross = "4 to 6-Lane Divided (80 km/h)" if "National" in cat else ("4-Lane Divided (60 km/h)" if "Primary" in cat else "2-Lane Undivided (40 km/h)")
            f.write(f"| **{cat}** | {l:.2f} km | {pct}% | {c} | {cross} |\n")
        f.write(f"| **Total Network** | **{total_road_length:.2f} km** | **100.0%** | **{len(roads_data['features'])}** | Complete Analyzed Network |\n\n")

        f.write("## 3. Roadside Facilities & Highway Proximity Distribution\n\n")
        f.write("| Buffer Distance Band | Facilities Count | Percentage Share | Civil Engineering Significance |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for b_name in ["Within 500m", "500m - 1000m", "1000m - 2000m", "> 2000m"]:
            cnt = fac_by_buffer[b_name]
            pct = round((cnt / total_facilities) * 100.0, 1)
            sig = "Direct access via frontage/service road; vital for trauma/refueling" if "500m" in b_name and "Within" in b_name else ("Intermediate feeder catchment (5-10 min walk/drive)" if "1000m" in b_name and "500" in b_name else ("Secondary access belt (accessible via local link roads)" if "2000m" in b_name and "1000" in b_name else "Peripheral zone; high response latency for highway emergencies"))
            f.write(f"| **{b_name}** | {cnt} | {pct}% | {sig} |\n")
        f.write(f"| **Total Facilities** | **{total_facilities}** | **100.0%** | All Analyzed Public Service POIs |\n\n")

        f.write("## 4. Accessibility Classification Summary\n\n")
        f.write("| Accessibility Tier | Total Area (km²) | Area Share (%) | Criteria Description | Strategic Planning Action |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for cls_name in ["High Accessibility", "Moderate Accessibility", "Low Accessibility"]:
            a = round(acc_areas[cls_name], 2)
            p = acc_pcts[cls_name]
            crit = "≤ 1.0 km to Highway AND ≤ 1.2 km to Emergency Facility" if "High" in cls_name else ("1.0 - 2.5 km to Highway OR 1.0 - 2.5 km to Facility" if "Moderate" in cls_name else "> 2.5 km to Highway AND > 2.5 km to Vital Facility")
            act = "Access management, median opening control, pedestrian safety" if "High" in cls_name else ("Feeder road widening, bus stop additions, intersection signalization" if "Moderate" in cls_name else "New arterial highway linkages and trauma care center placement")
            f.write(f"| **{cls_name}** | {a:.2f} km² | {p}% | {crit} | {act} |\n")
        f.write(f"| **Total Study Envelope** | **{total_study_area:.2f} km²** | **100.0%** | Comprehensive Corridor Area | Integrated Transport Masterplan |\n")

    print(f"[SAVED] Analysis Summary Markdown: {summary_md_path}")

    # 5. Generate Vector SVG Charts
    # Chart 1: Road lengths
    labels_road = ["National Highway / Expressway", "Primary Arterial Road", "Secondary / Connector Road"]
    vals_road = [road_lengths_by_cat[k] for k in labels_road]
    colors_road = ["#d97706", "#2563eb", "#64748b"]
    generate_svg_bar_chart(
        "Patna Highway Corridor: Road Length by Category",
        "Functional classification based on MoRTH / IRC standards (Total: " + str(total_road_length) + " km)",
        labels_road, vals_road, colors_road, "km",
        os.path.join(ANALYSIS_DIR, "chart_road_network.svg")
    )

    # Chart 2: Facilities in buffers
    labels_buf = ["Within 500m (Direct Access)", "500m - 1000m (Intermediate)", "1000m - 2000m (Secondary)", "> 2000m (Peripheral)"]
    vals_buf = [fac_by_buffer["Within 500m"], fac_by_buffer["500m - 1000m"], fac_by_buffer["1000m - 2000m"], fac_by_buffer["> 2000m"]]
    colors_buf = ["#16a34a", "#eab308", "#3b82f6", "#ef4444"]
    generate_svg_bar_chart(
        "Roadside Facilities Distribution Across Highway Buffers",
        "Proximity of hospitals, fuel stations, bus terminals, and police to major highways (N = " + str(total_facilities) + ")",
        labels_buf, vals_buf, colors_buf, "facilities",
        os.path.join(ANALYSIS_DIR, "chart_facility_buffer.svg")
    )

    # Chart 3: Accessibility Split Donut
    cats_acc = ["High Accessibility", "Moderate Accessibility", "Low Accessibility"]
    pcts_acc = [acc_pcts[k] for k in cats_acc]
    areas_acc = [acc_areas[k] for k in cats_acc]
    colors_acc = ["#15803d", "#d97706", "#b91c1c"]
    generate_svg_donut_chart(
        "Study Area Accessibility Classification Split",
        "Percentage of corridor land area by composite highway-facility accessibility index",
        cats_acc, pcts_acc, areas_acc, colors_acc,
        os.path.join(ANALYSIS_DIR, "chart_accessibility_split.svg")
    )


if __name__ == "__main__":
    main()
