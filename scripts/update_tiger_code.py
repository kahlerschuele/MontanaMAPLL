#!/usr/bin/env python3
"""
Update map.html with new TIGER/ACS implementation
"""

from pathlib import Path

# Read the map.html file
map_html_path = Path(__file__).parent.parent / "frontend" / "public" / "map.html"
with open(map_html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start and end of the loadTIGERBoundaries function
start_marker = "// TIGER boundary visibility toggles"
end_marker = "// Toggle TIGER layer visibility"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("ERROR: Could not find TIGER function markers")
    exit(1)

# Find the end of the toggleTIGERLayer function (next function or section)
# Look for the next major comment or function after toggle
temp = content[end_idx:end_idx+500]
next_section = temp.find("\n\n//")
if next_section != -1:
    end_idx = end_idx + next_section

print(f"Found TIGER code at positions {start_idx} to {end_idx}")

# New implementation
new_tiger_code = '''// TIGER/ACS Layer Configuration
const tigerConfig = {
    // State boundary - always visible
    state: {
        file: './data/montana_state.geojson',
        lineColor: '#FF0000',
        lineWidth: 3,
        minzoom: 0,
        visible: true
    },
    // Counties - visible at low zoom
    counties: {
        file: './data/tiger/mt_counties.geojson',
        lineColor: '#444444',
        lineWidth: 1.5,
        fillColor: 'rgba(68, 68, 68, 0.05)',
        minzoom: 5,
        visible: true
    },
    // Places (cities/towns) - visible at medium zoom
    places: {
        file: './data/tiger/mt_places.geojson',
        lineColor: '#F7DC6F',
        lineWidth: 1,
        fillColor: 'rgba(247, 220, 111, 0.15)',
        minzoom: 7,
        visible: false
    },
    // Census tracts with ACS demographics - visible at high zoom with choropleth
    tracts: {
        file: './data/tiger/mt_tracts_acs.geojson',
        lineColor: '#666666',
        lineWidth: 0.5,
        minzoom: 8,
        visible: true,
        choropleth: {
            property: 'median_household_income',
            stops: [
                [0, '#fee5d9'],
                [40000, '#fcbba1'],
                [60000, '#fc9272'],
                [80000, '#fb6a4a'],
                [100000, '#de2d26'],
                [150000, '#a50f15']
            ]
        }
    },
    // Block groups - visible at very high zoom
    blockgroups: {
        file: './data/tiger/mt_blockgroups.geojson',
        lineColor: '#999999',
        lineWidth: 0.3,
        fillColor: 'rgba(153, 153, 153, 0.03)',
        minzoom: 11,
        visible: false
    }
};

// Load TIGER/ACS boundary layers
async function loadTIGERBoundaries() {
    console.log('Loading TIGER/ACS layers...');

    for (const [layerId, config] of Object.entries(tigerConfig)) {
        try {
            const response = await fetch(config.file);
            const data = await response.json();

            const sourceId = `tiger-${layerId}`;

            // Add source
            map.addSource(sourceId, {
                type: 'geojson',
                data: data
            });

            // Add fill layer if configured
            if (config.fillColor || config.choropleth) {
                const fillPaint = {};

                if (config.choropleth) {
                    // Choropleth coloring based on ACS data
                    fillPaint['fill-color'] = [
                        'interpolate',
                        ['linear'],
                        ['get', config.choropleth.property],
                        ...config.choropleth.stops.flat()
                    ];
                    fillPaint['fill-opacity'] = 0.7;
                } else {
                    fillPaint['fill-color'] = config.fillColor;
                    fillPaint['fill-opacity'] = 1;
                }

                map.addLayer({
                    id: `${sourceId}-fill`,
                    type: 'fill',
                    source: sourceId,
                    minzoom: config.minzoom || 0,
                    paint: fillPaint,
                    layout: {
                        'visibility': config.visible ? 'visible' : 'none'
                    }
                });
            }

            // Add line layer
            map.addLayer({
                id: `${sourceId}-line`,
                type: 'line',
                source: sourceId,
                minzoom: config.minzoom || 0,
                paint: {
                    'line-color': config.lineColor,
                    'line-width': config.lineWidth,
                    'line-opacity': 0.8
                },
                layout: {
                    'visibility': config.visible ? 'visible' : 'none'
                }
            });

            // Add labels for places
            if (layerId === 'places') {
                map.addLayer({
                    id: `${sourceId}-labels`,
                    type: 'symbol',
                    source: sourceId,
                    minzoom: 8,
                    layout: {
                        'text-field': ['get', 'NAME'],
                        'text-size': ['interpolate', ['linear'], ['zoom'], 8, 10, 12, 14],
                        'text-anchor': 'center',
                        'visibility': config.visible ? 'visible' : 'none'
                    },
                    paint: {
                        'text-color': '#333333',
                        'text-halo-color': '#ffffff',
                        'text-halo-width': 1.5
                    }
                });
            }

            // Add click handler for demographics (tracts only)
            if (layerId === 'tracts') {
                map.on('click', `${sourceId}-fill`, (e) => {
                    if (!e.features?.[0]) return;
                    const p = e.features[0].properties;

                    const formatNumber = (n) => n ? n.toLocaleString() : 'N/A';
                    const formatCurrency = (n) => n ? `$${n.toLocaleString()}` : 'N/A';

                    const html = `
                        <div style="font-family: -apple-system, sans-serif; min-width: 280px;">
                            <div style="font-weight: 700; font-size: 14px; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 2px solid #444;">
                                Census Tract ${p.NAME || p.GEOID}
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 11px;">
                                <div style="background: #f0f0f0; padding: 6px; border-radius: 3px;">
                                    <div style="color: #666; font-size: 9px;">Population</div>
                                    <div style="font-weight: 700; font-size: 13px;">${formatNumber(p.total_population)}</div>
                                </div>
                                <div style="background: #f0f0f0; padding: 6px; border-radius: 3px;">
                                    <div style="color: #666; font-size: 9px;">Median Age</div>
                                    <div style="font-weight: 700; font-size: 13px;">${p.median_age || 'N/A'}</div>
                                </div>
                                <div style="background: #e6f3ff; padding: 6px; border-radius: 3px;">
                                    <div style="color: #0066cc; font-size: 9px;">Median Income</div>
                                    <div style="font-weight: 700; font-size: 13px; color: #0066cc;">${formatCurrency(p.median_household_income)}</div>
                                </div>
                                <div style="background: #e6f3ff; padding: 6px; border-radius: 3px;">
                                    <div style="color: #0066cc; font-size: 9px;">Per Capita</div>
                                    <div style="font-weight: 700; font-size: 13px; color: #0066cc;">${formatCurrency(p.per_capita_income)}</div>
                                </div>
                                <div style="background: #fff3e6; padding: 6px; border-radius: 3px;">
                                    <div style="color: #cc6600; font-size: 9px;">Housing Units</div>
                                    <div style="font-weight: 700; font-size: 13px;">${formatNumber(p.total_housing_units)}</div>
                                </div>
                                <div style="background: #fff3e6; padding: 6px; border-radius: 3px;">
                                    <div style="color: #cc6600; font-size: 9px;">Median Home Value</div>
                                    <div style="font-weight: 700; font-size: 13px;">${formatCurrency(p.median_home_value)}</div>
                                </div>
                            </div>
                        </div>
                    `;

                    new maplibregl.Popup({ closeButton: true, maxWidth: '320px' })
                        .setLngLat(e.lngLat)
                        .setHTML(html)
                        .addTo(map);
                });

                // Hover cursor
                map.on('mouseenter', `${sourceId}-fill`, () => {
                    map.getCanvas().style.cursor = 'pointer';
                });
                map.on('mouseleave', `${sourceId}-fill`, () => {
                    map.getCanvas().style.cursor = '';
                });
            }

            console.log(`TIGER ${layerId}: ${data.features.length} features loaded`);
        } catch (error) {
            console.error(`Failed to load TIGER ${layerId}:`, error);
        }
    }

    console.log('TIGER/ACS layers loaded');
}

'''

# Replace the old code
new_content = content[:start_idx] + new_tiger_code + content[end_idx:]

# Write back
with open(map_html_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("SUCCESS: Updated map.html with new TIGER/ACS implementation")
print("File saved at:", map_html_path)
