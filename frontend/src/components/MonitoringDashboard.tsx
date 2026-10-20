import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Metrics {
  prediction_count: number;
  p95_latency: number;
  error_rate: number;
  feedback_correction_rate: number;
  model_f1: number;
  drift_score: number;
}

export const MonitoringDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<Metrics | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await axios.get('/api/v1/metrics');
        setMetrics(response.data);
      } catch (error) {
        console.error('Error fetching metrics', error);
      }
    };
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  if (!metrics) return <div>Loading metrics...</div>;

  return (
    <div className="p-4 bg-white shadow rounded-lg mb-6">
      <h2 className="text-xl font-semibold mb-4">Application Metrics</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div className="p-4 border rounded bg-gray-50">
          <p className="text-sm text-gray-500">Prediction Count</p>
          <p className="text-2xl font-bold">{metrics.prediction_count}</p>
        </div>
        <div className="p-4 border rounded bg-gray-50">
          <p className="text-sm text-gray-500">P95 Latency</p>
          <p className="text-2xl font-bold">{metrics.p95_latency.toFixed(2)} ms</p>
        </div>
        <div className="p-4 border rounded bg-gray-50">
          <p className="text-sm text-gray-500">Error Rate</p>
          <p className="text-2xl font-bold">{(metrics.error_rate * 100).toFixed(2)}%</p>
        </div>
        <div className="p-4 border rounded bg-gray-50">
          <p className="text-sm text-gray-500">Correction Rate (Feedback)</p>
          <p className="text-2xl font-bold">{(metrics.feedback_correction_rate * 100).toFixed(2)}%</p>
        </div>
        <div className="p-4 border rounded bg-gray-50">
          <p className="text-sm text-gray-500">Latest Model F1</p>
          <p className="text-2xl font-bold">{metrics.model_f1.toFixed(4)}</p>
        </div>
        <div className="p-4 border rounded bg-gray-50">
          <p className="text-sm text-gray-500">Drift Score</p>
          <p className="text-2xl font-bold">{metrics.drift_score.toFixed(4)}</p>
        </div>
      </div>
    </div>
  );
};
