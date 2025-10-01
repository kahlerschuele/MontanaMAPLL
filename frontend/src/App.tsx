import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

export const App: React.FC = () => {
  const mapContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    console.log('🚀 Montana Map - High Resolution Version');

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: {
        version: 8,
        sources: {
          // High-resolution satellite basemap options
          'esri-satellite': {
            type: 'raster',
            tiles: [
              'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
            ],
            tileSize: 256,
            attribution: '© Esri'
          },
          // Load real parcel data from backend
          'parcels': {
            type: 'geojson',
            data: 'http://localhost:8000/data/parcels.geojson'
          },
          'ownership': {
            type: 'geojson',
            data: 'http://localhost:8000/data/ownership.geojson'
          }
        },
        layers: [
          {
            id: 'background',
            type: 'background',
            paint: { 'background-color': '#0a0a0a' }
          },
          {
            id: 'satellite',
            type: 'raster',
            source: 'esri-satellite',
            paint: { 'raster-opacity': 1 }
          },
          // Public lands - semi-transparent colored fills
          {
            id: 'ownership-fill',
            type: 'fill',
            source: 'ownership',
            paint: {
              'fill-color': [
                'match',
                ['get', 'owner_class'],
                'federal', '#1d4ed8',
                'state', '#059669',
                'local', '#7c3aed',
                'tribal', '#b45309',
                'other_public', '#0ea5e9',
                '#94a3b8'
              ],
              'fill-opacity': 0.15
            }
          },
          {
            id: 'ownership-outline',
            type: 'line',
            source: 'ownership',
            paint: {
              'line-color': [
                'match',
                ['get', 'owner_class'],
                'federal', '#1d4ed8',
                'state', '#059669',
                'local', '#7c3aed',
                'tribal', '#b45309',
                'other_public', '#0ea5e9',
                '#94a3b8'
              ],
              'line-width': ['interpolate', ['linear'], ['zoom'], 8, 1, 16, 2.5],
              'line-opacity': 0.7
            }
          },
          // Private parcels - white lines with black casing (onX style)
          {
            id: 'parcels-casing',
            type: 'line',
            source: 'parcels',
            minzoom: 13,
            paint: {
              'line-color': '#000000',
              'line-width': ['interpolate', ['linear'], ['zoom'], 13, 1.5, 18, 4],
              'line-opacity': 0.6,
              'line-join': 'round',
              'line-cap': 'round'
            }
          },
          {
            id: 'parcels-line',
            type: 'line',
            source: 'parcels',
            minzoom: 13,
            paint: {
              'line-color': '#ffffff',
              'line-width': ['interpolate', ['linear'], ['zoom'], 13, 1, 18, 2.5],
              'line-opacity': 0.95,
              'line-join': 'round',
              'line-cap': 'round'
            }
          }
        ]
      },
      center: [-111.0425, 45.6780], // Bozeman, MT
      zoom: 16,
      minZoom: 3,
      maxZoom: 20,
      maxPitch: 0  // Keep 2D for clearer lot lines
    });

    map.addControl(new maplibregl.NavigationControl(), 'top-left');
    map.addControl(new maplibregl.ScaleControl(), 'bottom-left');

    map.on('load', () => {
      console.log('✅ Map loaded - Esri World Imagery (high-res)');
      console.log('Sources:', Object.keys(map.getStyle().sources));
    });

    map.on('error', (e) => {
      console.error('Map error:', e);
    });

    // Hover cursor
    map.on('mouseenter', 'parcels-line', () => {
      map.getCanvas().style.cursor = 'pointer';
    });
    map.on('mouseleave', 'parcels-line', () => {
      map.getCanvas().style.cursor = '';
    });

    // Click handlers with popups
    map.on('click', 'parcels-line', (e) => {
      if (!e.features?.[0]) return;
      const p = e.features[0].properties;

      const html = `
        <div style="font-family: sans-serif; min-width: 200px;">
          <div style="font-weight: 600; font-size: 14px; margin-bottom: 8px; color: #1a1a1a;">
            Parcel ${p.PARCELID || p.parcel_id || 'N/A'}
          </div>
          <div style="font-size: 12px; line-height: 1.6; color: #4a4a4a;">
            ${p.OWNERNAME || p.owner_name ? `<strong>Owner:</strong> ${p.OWNERNAME || p.owner_name}<br/>` : ''}
            ${p.ACRES || p.acres ? `<strong>Acres:</strong> ${parseFloat(p.ACRES || p.acres).toFixed(2)}<br/>` : ''}
            ${p.TAXVALUE || p.tax_value ? `<strong>Value:</strong> $${parseInt(p.TAXVALUE || p.tax_value).toLocaleString()}<br/>` : ''}
            ${p.MAILADD || p.address ? `<strong>Address:</strong> ${p.MAILADD || p.address}<br/>` : ''}
            <strong>Source:</strong> Montana Cadastral
          </div>
        </div>
      `;

      new maplibregl.Popup({ closeButton: true, maxWidth: '350px' })
        .setLngLat(e.lngLat)
        .setHTML(html)
        .addTo(map);
    });

    map.on('click', 'ownership-fill', (e) => {
      if (!e.features?.[0]) return;
      const p = e.features[0].properties;

      const html = `
        <div style="font-family: sans-serif; min-width: 200px;">
          <div style="font-weight: 600; font-size: 14px; margin-bottom: 8px; color: #1a1a1a;">
            ${p.unit_name || p.owner_name || 'Public Land'}
          </div>
          <div style="font-size: 12px; line-height: 1.6; color: #4a4a4a;">
            ${p.owner_name ? `<strong>Owner:</strong> ${p.owner_name}<br/>` : ''}
            <strong>Class:</strong> ${(p.owner_class || '').replace('_', ' ')}<br/>
            <strong>Source:</strong> ${p.source || 'PAD-US'}<br/>
            <strong>As of:</strong> ${p.asof || '2023-09-01'}
          </div>
        </div>
      `;

      new maplibregl.Popup({ closeButton: true, maxWidth: '300px' })
        .setLngLat(e.lngLat)
        .setHTML(html)
        .addTo(map);
    });

    return () => map.remove();
  }, []);

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />

      {/* Legend */}
      <div style={{
        position: 'absolute',
        top: 12,
        right: 12,
        background: 'rgba(255,255,255,0.95)',
        padding: '14px 16px',
        borderRadius: 8,
        boxShadow: '0 2px 12px rgba(0,0,0,0.25)',
        minWidth: 180,
        zIndex: 1000
      }}>
        <h3 style={{ margin: '0 0 10px', fontSize: 14, fontWeight: 600, color: '#1a1a1a' }}>
          Public Lands
        </h3>
        {[
          { label: 'Federal', color: '#1d4ed8' },
          { label: 'State', color: '#059669' },
          { label: 'Local', color: '#7c3aed' },
          { label: 'Tribal', color: '#b45309' },
          { label: 'Other', color: '#0ea5e9' }
        ].map(item => (
          <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 7 }}>
            <div style={{ width: 14, height: 14, background: item.color, borderRadius: 2, border: '1px solid rgba(0,0,0,0.1)' }} />
            <span style={{ fontSize: 12, color: '#4a4a4a' }}>{item.label}</span>
          </div>
        ))}
        <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px solid #e0e0e0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ width: 20, height: 2, background: '#fff', border: '1px solid #000' }} />
            <span style={{ fontSize: 11, color: '#666' }}>Private Parcels</span>
          </div>
          <div style={{ fontSize: 10, color: '#999', marginTop: 4, marginLeft: 28 }}>
            Visible at z≥13
          </div>
        </div>
      </div>

      {/* Info panel */}
      <div style={{
        position: 'absolute',
        bottom: 12,
        left: 12,
        background: 'rgba(255,255,255,0.9)',
        padding: '8px 12px',
        borderRadius: 6,
        fontSize: 11,
        color: '#666',
        zIndex: 1000
      }}>
        Esri World Imagery © Esri | Parcels © Montana Cadastral
      </div>
    </div>
  );
};