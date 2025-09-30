import React from 'react';

interface AttributionProps {
  asofDate?: string;
}

export const Attribution: React.FC<AttributionProps> = ({ asofDate = '2023-09-01' }) => {
  return (
    <div style={styles.container}>
      <span style={styles.text}>
        Imagery © USGS | Boundaries © PAD-US (as of {asofDate})
      </span>
    </div>
  );
};

const styles = {
  container: {
    position: 'absolute' as const,
    bottom: '8px',
    right: '8px',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    padding: '4px 8px',
    borderRadius: 'var(--radius-sm)',
    fontSize: '11px',
    color: 'rgba(0, 0, 0, 0.7)',
    zIndex: 1000,
    pointerEvents: 'none' as const,
  },
  text: {
    whiteSpace: 'nowrap' as const,
  },
};