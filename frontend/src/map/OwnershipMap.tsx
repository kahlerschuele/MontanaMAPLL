import React, { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { Legend } from '../ui/Legend';
import { Attribution } from '../ui/Attribution';

const OWNER_COLORS = {
  federal: '#1d4ed8',
  state: '#059669',
  local: '#7c3aed',
  tribal: '#b45309',
  other_public: '#0ea5e9',
};

export const OwnershipMap: React.FC = () => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const popupRef = useRef<maplibregl.Popup | null>(null);
  const [asofDate, setAsofDate] = useState<string>('2023-09-01');

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Initialize map with satellite basemap + vector tiles
    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: {
        version: 8,
        sources: {
          'usgs-imagery': {
            type: 'raster',
            tiles: [
              'https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}'
            ],
            tileSize: 256,
            attribution: '© USGS'
          },
          'ownership-data': {
            type: 'geojson',
            data: 'http://localhost:8001/data/ownership.geojson'
          },
          'test-parcels': {
            type: 'geojson',
            data: 'http://localhost:8001/data/parcels.geojson'
          }
        },
        layers: [
          {
            id: 'background',
            type: 'background',
            paint: {
              'background-color': '#000'
            }
          },
          {
            id: 'satellite',
            type: 'raster',
            source: 'usgs-imagery',
            paint: {
              'raster-opacity': 1
            }
          },
          // PAD-US public lands (GeoJSON)
          {
            id: 'ownership-fill',
            type: 'fill',
            source: 'ownership-data',
            paint: {
              'fill-color': [
                'match',
                ['get', 'owner_class'],
                'federal', OWNER_COLORS.federal,
                'state', OWNER_COLORS.state,
                'local', OWNER_COLORS.local,
                'tribal', OWNER_COLORS.tribal,
                'other_public', OWNER_COLORS.other_public,
                '#94a3b8'
              ],
              'fill-opacity': 0.15
            }
          },
          {
            id: 'ownership-line',
            type: 'line',
            source: 'ownership-data',
            paint: {
              'line-color': [
                'match',
                ['get', 'owner_class'],
                'federal', OWNER_COLORS.federal,
                'state', OWNER_COLORS.state,
                'local', OWNER_COLORS.local,
                'tribal', OWNER_COLORS.tribal,
                'other_public', OWNER_COLORS.other_public,
                '#94a3b8'
              ],
              'line-width': [
                'interpolate',
                ['linear'],
                ['zoom'],
                8, 1.2,
                16, 3.0
              ],
              'line-opacity': 0.8
            }
          },
          // Test parcels (GeoJSON) with white lines + black casing
          {
            id: 'parcels-casing',
            type: 'line',
            source: 'test-parcels',
            minzoom: 13,
            paint: {
              'line-color': '#000',
              'line-width': [
                'interpolate',
                ['linear'],
                ['zoom'],
                13, 0.9,
                16, 1.6
              ],
              'line-opacity': 0.5,
              'line-join': 'round',
              'line-cap': 'round'
            }
          },
          {
            id: 'parcels-line',
            type: 'line',
            source: 'test-parcels',
            minzoom: 13,
            paint: {
              'line-color': '#fff',
              'line-width': [
                'interpolate',
                ['linear'],
                ['zoom'],
                13, 0.6,
                16, 1.4
              ],
              'line-opacity': 0.9,
              'line-join': 'round',
              'line-cap': 'round'
            }
          }
        ]
      },
      center: [-111.0425, 45.6780], // Bozeman, Montana
      zoom: 16,
      minZoom: 3,
      maxZoom: 20,
    });

    mapRef.current = map;

    // Add navigation controls
    map.addControl(new maplibregl.NavigationControl(), 'top-left');

    // Log when map loads
    map.on('load', () => {
      console.log('Map loaded successfully');
      console.log('Sources:', Object.keys(map.getStyle().sources));
      console.log('Layers:', map.getStyle().layers.map(l => l.id));
    });

    // Log errors
    map.on('error', (e) => {
      console.error('Map error:', e);
    });

    // Change cursor on hover for parcels
    map.on('mouseenter', 'parcels-line', () => {
      map.getCanvas().style.cursor = 'pointer';
    });

    map.on('mouseleave', 'parcels-line', () => {
      map.getCanvas().style.cursor = '';
    });

    // Change cursor on hover for ownership
    map.on('mouseenter', 'ownership-fill', () => {
      map.getCanvas().style.cursor = 'pointer';
    });

    map.on('mouseleave', 'ownership-fill', () => {
      map.getCanvas().style.cursor = '';
    });

    // Click handler for parcels
    map.on('click', 'parcels-line', (e) => {
      if (!e.features || e.features.length === 0) return;

      const feature = e.features[0];
      const props = feature.properties || {};

      const parcelId = props.PARCELID || props.parcelid || 'Unknown';
      const ownerName = props.OWNERNAME || props.ownername || 'Unknown Owner';
      const mailAddress = props.MAILADD || props.mailadd || '';
      const mailCity = props.MAILCITY || props.mailcity || '';
      const mailState = props.MAILSTATE || props.mailstate || '';
      const mailZip = props.MAILZIP || props.mailzip || '';
      const acres = props.ACRES || props.acres || 0;
      const taxValue = props.TAXVALUE || props.taxvalue || 0;

      const lines: string[] = [];
      lines.push(`<strong>Parcel ID:</strong> ${parcelId}`);
      lines.push(`<strong>Owner:</strong> ${ownerName}`);

      if (mailAddress) {
        lines.push(`<strong>Address:</strong> ${mailAddress}`);
        if (mailCity || mailState || mailZip) {
          lines.push(`${mailCity}, ${mailState} ${mailZip}`);
        }
      }

      if (acres > 0) {
        lines.push(`<strong>Acres:</strong> ${parseFloat(acres).toFixed(2)}`);
      }

      if (taxValue > 0) {
        lines.push(`<strong>Tax Value:</strong> $${parseInt(taxValue).toLocaleString()}`);
      }

      lines.push(`<strong>Source:</strong> Montana Cadastral`);

      const htmlContent = `
        <div style="font-family: var(--font-family); padding: 4px;">
          <h4 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 600;">Private Parcel</h4>
          <div style="font-size: 12px; line-height: 1.6;">
            ${lines.join('<br>')}
          </div>
        </div>
      `;

      if (popupRef.current) {
        popupRef.current.remove();
      }

      const popup = new maplibregl.Popup({
        closeButton: true,
        closeOnClick: true,
        maxWidth: '350px',
      })
        .setLngLat(e.lngLat)
        .setHTML(htmlContent)
        .addTo(map);

      popupRef.current = popup;
    });

    // Click handler for PAD-US ownership
    map.on('click', 'ownership-fill', (e) => {
      if (!e.features || e.features.length === 0) return;

      const feature = e.features[0];
      const props = feature.properties || {};

      const unitName = props.unit_name || '';
      const ownerName = props.owner_name || '';
      const ownerClass = props.owner_class || '';
      const source = props.source || 'PAD-US';
      const asof = props.asof || '2023-09-01';

      if (asof) {
        setAsofDate(asof);
      }

      const title = unitName || ownerName || 'Public Land';
      const lines: string[] = [];

      if (ownerName) lines.push(`<strong>Owner:</strong> ${ownerName}`);
      if (ownerClass) lines.push(`<strong>Class:</strong> ${ownerClass.replace('_', ' ')}`);
      lines.push(`<strong>Source:</strong> ${source}`);
      lines.push(`<strong>As of:</strong> ${asof}`);

      const htmlContent = `
        <div style="font-family: var(--font-family); padding: 4px;">
          <h4 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 600;">${title}</h4>
          <div style="font-size: 12px; line-height: 1.6;">
            ${lines.join('<br>')}
          </div>
        </div>
      `;

      if (popupRef.current) {
        popupRef.current.remove();
      }

      const popup = new maplibregl.Popup({
        closeButton: true,
        closeOnClick: true,
        maxWidth: '300px',
      })
        .setLngLat(e.lngLat)
        .setHTML(htmlContent)
        .addTo(map);

      popupRef.current = popup;
    });

    // Cleanup
    return () => {
      if (popupRef.current) {
        popupRef.current.remove();
      }
      map.remove();
    };
  }, []);

  return (
    <div style={styles.container}>
      <div ref={mapContainerRef} style={styles.map} />
      <Legend />
      <Attribution asofDate={asofDate} />
    </div>
  );
};

const styles = {
  container: {
    position: 'relative' as const,
    width: '100%',
    height: '100%',
  },
  map: {
    width: '100%',
    height: '100%',
  },
};