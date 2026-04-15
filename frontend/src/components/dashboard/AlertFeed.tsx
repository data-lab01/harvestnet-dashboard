import React from 'react';

interface AlertFeedProps {
  alerts: any[];
}

export const AlertFeed: React.FC<AlertFeedProps> = ({ alerts }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">Recent Alerts</h3>
      <div className="space-y-2">
        {alerts.map((alert, index) => (
          <div key={index} className="p-3 bg-red-50 border border-red-200 rounded">
            <p className="text-sm text-red-800">{alert.message}</p>
            <p className="text-xs text-red-600 mt-1">{alert.timestamp}</p>
          </div>
        ))}
      </div>
    </div>
  );
};