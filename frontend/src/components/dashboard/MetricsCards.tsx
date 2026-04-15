import React from 'react';
import { AlertTriangle, Package, TrendingDown, DollarSign } from 'lucide-react';

interface MetricsCardsProps {
  summary: {
    active_batches: number;
    critical_alerts: number;
    avg_loss_percent: number;
    estimated_value_lost: number;
  };
}

export const MetricsCards: React.FC<MetricsCardsProps> = ({ summary }) => {
  const cards = [
    {
      title: 'Active Batches',
      value: summary.active_batches,
      icon: Package,
      color: 'blue',
      change: null
    },
    {
      title: 'Critical Alerts',
      value: summary.critical_alerts,
      icon: AlertTriangle,
      color: 'red',
      change: summary.critical_alerts > 0 ? '+2 from yesterday' : null
    },
    {
      title: 'Avg Loss Rate',
      value: `${summary.avg_loss_percent}%`,
      icon: TrendingDown,
      color: 'yellow',
      change: 'Below regional avg of 25%'
    },
    {
      title: 'Value Lost',
      value: `$${summary.estimated_value_lost.toLocaleString()}`,
      icon: DollarSign,
      color: 'gray',
      change: 'Last 30 days'
    }
  ];
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => {
        const Icon = card.icon;
        const colorClasses = {
          blue: 'bg-blue-50 text-blue-600',
          red: 'bg-red-50 text-red-600',
          yellow: 'bg-yellow-50 text-yellow-600',
          gray: 'bg-gray-50 text-gray-600'
        };
        
        return (
          <div key={card.title} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">{card.title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{card.value}</p>
                {card.change && (
                  <p className="text-xs text-gray-500 mt-2">{card.change}</p>
                )}
              </div>
              <div className={`p-3 rounded-full ${colorClasses[card.color]}`}>
                <Icon className="h-6 w-6" />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};