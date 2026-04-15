import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MetricsCards } from '../components/dashboard/MetricsCards';
import { SensorChart } from '../components/dashboard/SensorChart';
import { AlertFeed } from '../components/dashboard/AlertFeed';
import { BatchList } from '../components/dashboard/BatchList';
import { MapView } from '../components/dashboard/MapView';
import { api } from '../api/client';
import { useWebSocket } from '../hooks/useWebSocket';

export const Dashboard: React.FC = () => {
  const [selectedBatch, setSelectedBatch] = useState<string | null>(null);
  
  // Fetch dashboard data
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: () => api.get('/dashboard/summary').then(res => res.data)
  });
  
  // Real-time WebSocket updates
  const { lastMessage } = useWebSocket('ws://localhost:8000/ws/farm-123');
  
  useEffect(() => {
    if (lastMessage) {
      // Update UI with real-time sensor data
      refetch();
    }
  }, [lastMessage, refetch]);
  
  if (isLoading) {
    return <DashboardSkeleton />;
  }
  
  const { summary, status, batches, alerts } = data;
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-900">HarvestNet Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">Real-time post-harvest intelligence</p>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="p-6">
        {/* Status Banner */}
        <div className={`mb-6 p-4 rounded-lg ${
          status.color === 'green' ? 'bg-green-50 border border-green-200' :
          status.color === 'yellow' ? 'bg-yellow-50 border border-yellow-200' :
          'bg-red-50 border border-red-200'
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <div className={`text-lg font-semibold ${
                status.color === 'green' ? 'text-green-800' :
                status.color === 'yellow' ? 'text-yellow-800' :
                'text-red-800'
              }`}>
                System Status: {status.color.toUpperCase()}
              </div>
              <div className="text-sm text-gray-600 mt-1">
                {status.message}
              </div>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-gray-900">{summary.safe_days_remaining}</div>
              <div className="text-xs text-gray-500">safe days remaining</div>
            </div>
          </div>
        </div>
        
        {/* Metrics Cards */}
        <MetricsCards summary={summary} />
        
        {/* Two-column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
          {/* Left column (2/3 width) */}
          <div className="lg:col-span-2 space-y-6">
            {/* Sensor Chart */}
            {selectedBatch && (
              <SensorChart batchId={selectedBatch} />
            )}
            
            {/* Batch List */}
            <BatchList 
              batches={batches} 
              onSelectBatch={setSelectedBatch}
              selectedBatchId={selectedBatch}
            />
          </div>
          
          {/* Right column (1/3 width) */}
          <div className="space-y-6">
            {/* Alert Feed */}
            <AlertFeed alerts={alerts} />
            
            {/* Map View */}
            <MapView batches={batches} />
          </div>
        </div>
      </main>
    </div>
  );
};

const DashboardSkeleton: React.FC = () => (
  <div className="min-h-screen bg-gray-50 p-6">
    <div className="animate-pulse space-y-6">
      <div className="h-24 bg-gray-200 rounded-lg"></div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
        ))}
      </div>
      <div className="h-96 bg-gray-200 rounded-lg"></div>
    </div>
  </div>
);