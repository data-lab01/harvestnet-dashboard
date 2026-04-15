import React from 'react';

interface MapViewProps {
  batches: any[];
}

export const MapView: React.FC<MapViewProps> = ({ batches }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">Farm Map</h3>
      <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
        <p className="text-gray-500">Map placeholder</p>
      </div>
    </div>
  );
};