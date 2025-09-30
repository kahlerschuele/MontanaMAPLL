import React from 'react';

const LEGEND_ITEMS = [
  { label: 'Federal', color: '#1d4ed8' },
  { label: 'State', color: '#059669' },
  { label: 'Local', color: '#7c3aed' },
  { label: 'Tribal', color: '#b45309' },
  { label: 'Other Public', color: '#0ea5e9' },
];

export const Legend: React.FC = () => {
  return (
    <div style={styles.container}>
      <h3 style={styles.title}>Public Land Ownership</h3>
      <div style={styles.items}>
        {LEGEND_ITEMS.map(item => (
          <div key={item.label} style={styles.item}>
            <div
              style={{
                ...styles.colorBox,
                backgroundColor: item.color,
              }}
            />
            <span style={styles.label}>{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

const styles = {
  container: {
    position: 'absolute' as const,
    top: '16px',
    right: '16px',
    backgroundColor: 'var(--bg-panel)',
    padding: 'var(--spacing-lg)',
    borderRadius: 'var(--radius-md)',
    boxShadow: 'var(--shadow-md)',
    minWidth: '180px',
    zIndex: 1000,
  },
  title: {
    fontSize: 'var(--font-size-base)',
    fontWeight: 600,
    color: 'var(--text-primary)',
    marginBottom: 'var(--spacing-md)',
  },
  items: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 'var(--spacing-sm)',
  },
  item: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--spacing-sm)',
  },
  colorBox: {
    width: '16px',
    height: '16px',
    borderRadius: 'var(--radius-sm)',
    border: '1px solid rgba(0,0,0,0.1)',
  },
  label: {
    fontSize: 'var(--font-size-sm)',
    color: 'var(--text-primary)',
  },
};