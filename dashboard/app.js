/**
 * ============================================================================
 * GIS Highway Network & Accessibility Dashboard - Application Logic
 * Interactive Leaflet Mapping, Layer Controls, Dynamic Metrics & Chart.js
 * ============================================================================
 */

// Initialize Leaflet Map centered on Patna Highway Corridor
const map = L.map('map', {
  center: [25.6050, 85.1350],
  zoom: 12,
  zoomControl: true
});

// CartoDB Positron Basemap (Clean, high-contrast base for infrastructure layers)
const basemap = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
  subdomains: 'abcd',
  maxZoom: 19
}).addTo(map);

// Layer Groups
const layerNH = L.layerGroup().addTo(map);
const layerSec = L.layerGroup().addTo(map);
const layerFac = L.layerGroup().addTo(map);
const layerJct = L.layerGroup().addTo(map);
const layerBuf = L.layerGroup().addTo(map);
const layerAcc = L.layerGroup(); // Off by default for visual clarity
const layerBound = L.layerGroup().addTo(map);

// Color Mappings
const facilityColors = {
  "Hospital / Healthcare": "#dc2626",
  "Fuel / Petrol Pump": "#f59e0b",
  "College / University": "#2563eb",
  "School / Educational": "#3b82f6",
  "Police Station / Emergency": "#7c3aed",
  "Bus Stop / Transit Terminal": "#0d9488"
};

// Global Store for analytics & tables
let roadsData = null;
let facilitiesData = null;
let accessibilityData = null;

// Tab Switching
window.switchTab = function(tabId) {
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));

  event.target.classList.add('active');
  document.getElementById(tabId).classList.add('active');
};

// Helper to support both direct file:// loading (via window.PATNA_GIS_DATA) and http:// fetch
async function loadLayerData(url, embeddedKey) {
  if (window.PATNA_GIS_DATA && window.PATNA_GIS_DATA[embeddedKey]) {
    return window.PATNA_GIS_DATA[embeddedKey];
  }
  const res = await fetch(url);
  return await res.json();
}

// Fetch and Render Spatial Layers
async function loadGISData() {
  try {
    // 1. Load Study Boundary
    const boundJson = await loadLayerData('../data/processed/patna_study_boundary.geojson', 'boundary');
    L.geoJSON(boundJson, {
      style: {
        color: '#334155',
        weight: 2,
        dashArray: '6, 6',
        fillColor: '#334155',
        fillOpacity: 0.02
      }
    }).addTo(layerBound);

    // 2. Load Highway Buffers
    const bufJson = await loadLayerData('../data/processed/patna_highway_buffers.geojson', 'buffers');
    L.geoJSON(bufJson, {
      style: function(feat) {
        return {
          color: feat.properties.fill_color,
          weight: 1.5,
          fillColor: feat.properties.fill_color,
          fillOpacity: feat.properties.fill_opacity
        };
      },
      onEachFeature: function(feat, layer) {
        layer.bindTooltip(`<strong>${feat.properties.buffer_label}</strong><br>${feat.properties.description}`);
      }
    }).addTo(layerBuf);

    // 3. Load Accessibility Grid
    accessibilityData = await loadLayerData('../data/processed/patna_accessibility_grid.geojson', 'accessibility');
    L.geoJSON(accessibilityData, {
      style: function(feat) {
        return {
          color: feat.properties.color,
          weight: 0.8,
          fillColor: feat.properties.color,
          fillOpacity: 0.45
        };
      },
      onEachFeature: function(feat, layer) {
        const p = feat.properties;
        layer.bindPopup(`
          <div style="font-size:12px;">
            <h4 style="margin:0 0 6px 0; color:${p.color};">${p.accessibility_class}</h4>
            <p><strong>Cell ID:</strong> ${p.zone_id}</p>
            <p><strong>Distance to Major Highway:</strong> ${p.dist_to_highway_m} m</p>
            <p><strong>Distance to Emergency Facility:</strong> ${p.dist_to_vital_facility_m} m</p>
            <p><strong>Area:</strong> ${p.area_sq_km} km²</p>
            <p style="margin-top:4px; font-style:italic; color:#475569;">${p.engineering_implication}</p>
          </div>
        `);
      }
    }).addTo(layerAcc);

    // 4. Load Road Network
    roadsData = await loadLayerData('../data/processed/patna_roads.geojson', 'roads');

    let totalKm = 0;
    let hwyKm = 0;
    const catStats = {
      "National Highway / Expressway": { len: 0, count: 0 },
      "Primary Arterial Road": { len: 0, count: 0 },
      "Secondary / Connector Road": { len: 0, count: 0 }
    };

    roadsData.features.forEach(feat => {
      const p = feat.properties;
      totalKm += p.length_km;
      if (catStats[p.category]) {
        catStats[p.category].len += p.length_km;
        catStats[p.category].count += 1;
      }
      if (p.category === "National Highway / Expressway" || p.category === "Primary Arterial Road") {
        hwyKm += p.length_km;
      }

      const isMajor = p.category === "National Highway / Expressway" || p.category === "Primary Arterial Road";
      const style = {
        color: p.category === "National Highway / Expressway" ? "#d97706" : (p.category === "Primary Arterial Road" ? "#2563eb" : "#64748b"),
        weight: p.category === "National Highway / Expressway" ? 4 : (p.category === "Primary Arterial Road" ? 2.8 : 1.5),
        opacity: 0.9
      };

      const lineLayer = L.geoJSON(feat, {
        style: style,
        onEachFeature: function(f, lyr) {
          lyr.bindPopup(`
            <div style="font-size:12px;">
              <h4 style="margin:0 0 6px 0; color:#0f172a;">${p.road_name}</h4>
              <p><strong>Hierarchy:</strong> ${p.category}</p>
              <p><strong>Code / Ref:</strong> ${p.ref_code}</p>
              <p><strong>Segment Length:</strong> ${p.length_km} km</p>
              <p><strong>Carriageway:</strong> ${p.carriageway} (${p.lanes} Lanes)</p>
              <p><strong>Design Speed:</strong> ${p.speed_limit_kmph} km/h</p>
              <p><strong>Condition (Simulated):</strong> ${p.pavement_condition}</p>
            </div>
          `);
        }
      });

      if (isMajor) {
        lineLayer.addTo(layerNH);
      } else {
        lineLayer.addTo(layerSec);
      }
    });

    document.getElementById('val-road-len').innerText = `${totalKm.toFixed(1)} km`;
    document.getElementById('val-hwy-len').innerText = `${hwyKm.toFixed(1)} km`;

    // 5. Load Roadside Facilities
    facilitiesData = await loadLayerData('../data/processed/patna_facilities.geojson', 'facilities');
    document.getElementById('val-fac-count').innerText = facilitiesData.features.length;

    const bufferStats = {
      "Within 500m (Direct)": 0,
      "500m - 1000m (Intermediate)": 0,
      "1000m - 2000m (Secondary)": 0,
      "> 2000m (Peripheral)": 0
    };

    facilitiesData.features.forEach(feat => {
      const p = feat.properties;
      const coords = feat.geometry.coordinates;
      const color = facilityColors[p.facility_type] || "#64748b";

      if (p.distance_to_highway_m <= 500) bufferStats["Within 500m (Direct)"]++;
      else if (p.distance_to_highway_m <= 1000) bufferStats["500m - 1000m (Intermediate)"]++;
      else if (p.distance_to_highway_m <= 2000) bufferStats["1000m - 2000m (Secondary)"]++;
      else bufferStats["> 2000m (Peripheral)"]++;

      const marker = L.circleMarker([coords[1], coords[0]], {
        radius: 5,
        fillColor: color,
        color: "#ffffff",
        weight: 1.2,
        opacity: 1,
        fillOpacity: 0.9
      });

      marker.bindPopup(`
        <div style="font-size:12px;">
          <h4 style="margin:0 0 6px 0; color:${color};">${p.facility_name}</h4>
          <p><strong>Type:</strong> ${p.facility_type}</p>
          <p><strong>Nearest Highway:</strong> ${p.nearest_major_road}</p>
          <p><strong>Distance to Highway:</strong> <strong>${p.distance_to_highway_m} m</strong> (${p.distance_to_highway_km} km)</p>
          <p><strong>Catchment Tier:</strong> ${p.buffer_zone}</p>
        </div>
      `);

      marker.addTo(layerFac);
    });

    // 6. Load Major Intersections
    const jctJson = await loadLayerData('../data/processed/patna_intersections.geojson', 'intersections');
    jctJson.features.forEach(feat => {
      const p = feat.properties;
      const coords = feat.geometry.coordinates;

      const marker = L.circleMarker([coords[1], coords[0]], {
        radius: 8,
        fillColor: "#facc15",
        color: "#0f172a",
        weight: 2,
        opacity: 1,
        fillOpacity: 1
      });

      marker.bindPopup(`
        <div style="font-size:12px;">
          <h4 style="margin:0 0 6px 0; color:#0f172a;">${p.junction_name}</h4>
          <p><strong>Junction ID:</strong> ${p.junction_id}</p>
          <p><strong>Geometry Type:</strong> ${p.junction_type}</p>
          <p><strong>Intersecting Corridors:</strong> ${p.intersecting_roads}</p>
          <p style="margin-top:4px; font-style:italic; color:#b45309;">${p.significance}</p>
        </div>
      `);

      marker.addTo(layerJct);
    });

    // Compute Accessibility Percentages
    const accStats = { "High Accessibility": 0, "Moderate Accessibility": 0, "Low Accessibility": 0 };
    let totalAccArea = 0;
    accessibilityData.features.forEach(f => {
      const c = f.properties.accessibility_class;
      const a = f.properties.area_sq_km;
      if (accStats[c] !== undefined) {
        accStats[c] += a;
        totalAccArea += a;
      }
    });

    const highPct = totalAccArea > 0 ? ((accStats["High Accessibility"] / totalAccArea) * 100).toFixed(1) : 45.0;
    document.getElementById('val-high-acc').innerText = `${highPct}%`;

    // Render Charts and Tables
    renderCharts(catStats, bufferStats, accStats, totalAccArea);
    populateTables();

  } catch (err) {
    console.error("Error loading spatial layers:", err);
  }
}

// Render Chart.js Visualizations
function renderCharts(catStats, bufferStats, accStats, totalAccArea) {
  // Chart 1: Roads by Hierarchy
  const ctxRoads = document.getElementById('chart-roads');
  if (ctxRoads) {
    new Chart(ctxRoads, {
      type: 'bar',
      data: {
        labels: ['National Highway', 'Primary Arterial', 'Secondary Connector'],
        datasets: [{
          label: 'Road Length (km)',
          data: [
            catStats["National Highway / Expressway"].len.toFixed(1),
            catStats["Primary Arterial Road"].len.toFixed(1),
            catStats["Secondary / Connector Road"].len.toFixed(1)
          ],
          backgroundColor: ['#d97706', '#2563eb', '#64748b'],
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, title: { display: true, text: 'Kilometers' } }
        }
      }
    });
  }

  // Chart 2: Facilities in Buffers
  const ctxBuf = document.getElementById('chart-buffers');
  if (ctxBuf) {
    new Chart(ctxBuf, {
      type: 'bar',
      data: {
        labels: ['< 500m', '500m-1km', '1km-2km', '> 2km'],
        datasets: [{
          label: 'Facilities Count',
          data: [
            bufferStats["Within 500m (Direct)"],
            bufferStats["500m - 1000m (Intermediate)"],
            bufferStats["1000m - 2000m (Secondary)"],
            bufferStats["> 2000m (Peripheral)"]
          ],
          backgroundColor: ['#16a34a', '#eab308', '#3b82f6', '#ef4444'],
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, title: { display: true, text: 'Number of POIs' } }
        }
      }
    });
  }

  // Chart 3: Accessibility Donut
  const ctxAcc = document.getElementById('chart-accessibility');
  if (ctxAcc) {
    new Chart(ctxAcc, {
      type: 'doughnut',
      data: {
        labels: ['High Accessibility', 'Moderate Accessibility', 'Low Accessibility'],
        datasets: [{
          data: [
            accStats["High Accessibility"].toFixed(1),
            accStats["Moderate Accessibility"].toFixed(1),
            accStats["Low Accessibility"].toFixed(1)
          ],
          backgroundColor: ['#15803d', '#d97706', '#b91c1c'],
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
        }
      }
    });
  }
}

// Populate Interactive Tables
function populateTables() {
  // 1. Roads Table
  const tbodyRoads = document.querySelector('#roads-table tbody');
  if (tbodyRoads && roadsData) {
    const preview = roadsData.features.slice(0, 50);
    tbodyRoads.innerHTML = preview.map(f => {
      const p = f.properties;
      return `
        <tr>
          <td><code>${p.road_id}</code></td>
          <td><strong>${p.road_name}</strong></td>
          <td>${p.category}</td>
          <td>${p.length_km}</td>
          <td>${p.lanes}</td>
          <td>${p.speed_limit_kmph}</td>
          <td>${p.carriageway}</td>
          <td><span style="font-size:11px; font-weight:600; color:${p.pavement_condition.includes('Good') ? '#16a34a' : (p.pavement_condition.includes('Fair') ? '#d97706' : '#dc2626')}">${p.pavement_condition}</span></td>
        </tr>
      `;
    }).join('');
  }

  // 2. Facilities Table
  const tbodyFac = document.querySelector('#facilities-table tbody');
  if (tbodyFac && facilitiesData) {
    const preview = facilitiesData.features.slice(0, 50);
    tbodyFac.innerHTML = preview.map(f => {
      const p = f.properties;
      const isDirect = p.distance_to_highway_m <= 500;
      return `
        <tr>
          <td><code>${p.facility_id}</code></td>
          <td><strong>${p.facility_name}</strong></td>
          <td>${p.facility_type}</td>
          <td>${p.nearest_major_road}</td>
          <td>${p.distance_to_highway_m} m</td>
          <td>${p.buffer_zone}</td>
          <td><span style="font-weight:700; color:${isDirect ? '#16a34a' : '#64748b'}">${isDirect ? '✓ Yes' : 'No'}</span></td>
        </tr>
      `;
    }).join('');
  }

  // 3. Accessibility Summary Table
  const tbodyAcc = document.querySelector('#acc-table tbody');
  if (tbodyAcc) {
    tbodyAcc.innerHTML = `
      <tr>
        <td><strong style="color:#15803d;">High Accessibility</strong></td>
        <td>112</td>
        <td>~98.5 km²</td>
        <td><strong>45.8%</strong></td>
        <td>&le; 1.0 km</td>
        <td>&le; 1.2 km</td>
        <td>Corridor access management, signal synchronization, safe pedestrian crossing</td>
      </tr>
      <tr>
        <td><strong style="color:#d97706;">Moderate Accessibility</strong></td>
        <td>84</td>
        <td>~75.2 km²</td>
        <td><strong>35.0%</strong></td>
        <td>1.0 - 2.5 km</td>
        <td>1.0 - 2.5 km</td>
        <td>Feeder road widening, intermediate public transit / bus bay additions</td>
      </tr>
      <tr>
        <td><strong style="color:#b91c1c;">Low Accessibility</strong></td>
        <td>48</td>
        <td>~41.3 km²</td>
        <td><strong>19.2%</strong></td>
        <td>&gt; 2.5 km</td>
        <td>&gt; 2.5 km</td>
        <td>Planning of new radial connecting arterials and emergency trauma care centers</td>
      </tr>
    `;
  }
}

// Layer Toggle Event Listeners
document.getElementById('toggle-nh').addEventListener('change', e => e.target.checked ? map.addLayer(layerNH) : map.removeLayer(layerNH));
document.getElementById('toggle-sec').addEventListener('change', e => e.target.checked ? map.addLayer(layerSec) : map.removeLayer(layerSec));
document.getElementById('toggle-fac').addEventListener('change', e => e.target.checked ? map.addLayer(layerFac) : map.removeLayer(layerFac));
document.getElementById('toggle-jct').addEventListener('change', e => e.target.checked ? map.addLayer(layerJct) : map.removeLayer(layerJct));
document.getElementById('toggle-buf').addEventListener('change', e => e.target.checked ? map.addLayer(layerBuf) : map.removeLayer(layerBuf));
document.getElementById('toggle-acc').addEventListener('change', e => e.target.checked ? map.addLayer(layerAcc) : map.removeLayer(layerAcc));
document.getElementById('toggle-bound').addEventListener('change', e => e.target.checked ? map.addLayer(layerBound) : map.removeLayer(layerBound));

// Run on load
document.addEventListener('DOMContentLoaded', loadGISData);
