import React from 'react';

interface BatchListProps {
  batches: any[];
  onSelectBatch: (id: string | null) => void;
  selectedBatchId: string | null;
}

export const BatchList: React.FC<BatchListProps> = ({ batches, onSelectBatch, selectedBatchId }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">Batches</h3>
      <div className="space-y-2">
        {batches.map((batch) => (
          <div
            key={batch.id}
            className={`p-3 border rounded cursor-pointer ${
              selectedBatchId === batch.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
            }`}
            onClick={() => onSelectBatch(selectedBatchId === batch.id ? null : batch.id)}
          >
            <p className="font-medium">{batch.name}</p>
            <p className="text-sm text-gray-600">Status: {batch.status}</p>
          </div>
        ))}
      </div>
    </div>
  );
};