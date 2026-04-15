import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { api } from '../../api/client';

interface SensorChartProps {
  batchId: string;
}

export const SensorChart: React.FC<SensorChartProps> = ({ batchId }) => {
  const { data, isLoading } = useQuery({
    queryKey: ['sensor-history', batchId],
    queryFn: () => api.get(`/dashboard/sensor-history/${batchId}?hours=48`).then(res => res.data),
    refetchInterval: 30000 // Refresh every 30 seconds
  });
  
  if (isLoading || !data) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse h-64 bg-gray-100 rounded"></div>
      </div>
    );
  }
  
  // Transform data for Recharts
  const chartData = data.timestamps.map((timestamp: string, i: number) => ({
    time: new Date(timestamp).toLocaleTimeString(),
    temperature: data.temperatures[i],
    humidity: data.humidities[i],
    co2: data.co2_levels[i]
  }));
  
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Sensor History (48 hours)</h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis yAxisId="left" label={{ value: 'Temp (°C) / Humidity (%)', angle: -90, position: 'insideLeft' }} />
            <YAxis yAxisId="right" orientation="right" label={{ value: 'CO2 (ppm)', angle: 90, position: 'insideRight' }} />
            <Tooltip />
            <Legend />
            <Line 
              yAxisId="left"
              type="monotone" 
              dataKey="temperature" 
              stroke="#ef4444" 
              name="Temperature (°C)"
              strokeWidth={2}
            />
            <Line 
              yAxisId="left"
              type="monotone" 
              dataKey="humidity" 
              stroke="#3b82f6" 
              name="Humidity (%)"
              strokeWidth={2}
            />
            <Line 
              yAxisId="right"
              type="monotone" 
              dataKey="co2" 
              stroke="#10b981" 
              name="CO2 (ppm)"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      {/* Threshold indicators */}
      <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-100">
        <div className="text-center">
          <div className="text-xs text-gray-500">Temperature Alert</div>
          <div className="text-sm font-medium text-red-600">&gt;30°C = Critical</div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-500">Humidity Alert</div>
          <div className="text-sm font-medium text-yellow-600">&gt;70% = Risk</div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-500">CO₂ Alert</div>
          <div className="text-sm font-medium text-green-600">&gt;500ppm = Respiration spike</div>
        </div>
      </div>
    </div>
  );
};