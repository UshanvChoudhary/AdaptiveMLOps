import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface DriftRun {
  id: string;
  drift_score: number;
  status: string;
  reference_dataset_id: string | null;
  current_window_start: string | null;
  current_window_end: string | null;
  class_distribution: Record<string, number> | null;
  confidence_trend: any;
  input_distribution: any;
  recommended_action: string;
  created_at: string;
}

export const DriftDashboard: React.FC = () => {
  const [drift, setDrift] = useState<DriftRun | null>(null);

  useEffect(() => {
    const fetchDrift = async () => {
      try {
        const response = await axios.get('/api/v1/drift/latest');
        setDrift(response.data);
      } catch (error) {
        console.error('Error fetching drift', error);
      }
    };
    fetchDrift();
  }, []);

  const runDriftAnalysis = async () => {
    try {
      const response = await axios.post('/api/v1/drift/run', {});
      setDrift(response.data);
    } catch (error) {
      console.error('Error running drift analysis', error);
    }
  };

  if (!drift) {
    return (
      <div className="p-4 bg-white shadow rounded-lg mb-6">
        <h2 className="text-xl font-semibold mb-4">Drift Analysis</h2>
        <p className="mb-4">No drift runs found.</p>
        <button 
          onClick={runDriftAnalysis}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Run Drift Analysis
        </button>
      </div>
    );
  }

  const statusColor = 
    drift.status === 'CRITICAL' ? 'text-red-600' :
    drift.status === 'WARNING' ? 'text-yellow-600' : 'text-green-600';

  return (
    <div className="p-4 bg-white shadow rounded-lg mb-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Intelligent Drift Detection</h2>
        <button 
          onClick={runDriftAnalysis}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Run Analysis Now
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-medium border-b pb-2 mb-2">Status Overview</h3>
          <p><strong>Status:</strong> <span className={`font-bold ${statusColor}`}>{drift.status}</span></p>
          <p><strong>Drift Score:</strong> {drift.drift_score.toFixed(4)}</p>
          <p><strong>Last Analyzed:</strong> {new Date(drift.created_at).toLocaleString()}</p>
          <p><strong>Action:</strong> {drift.recommended_action}</p>
        </div>
        
        <div>
          <h3 className="text-lg font-medium border-b pb-2 mb-2">Analysis Window</h3>
          <p><strong>Start:</strong> {drift.current_window_start ? new Date(drift.current_window_start).toLocaleString() : 'N/A'}</p>
          <p><strong>End:</strong> {drift.current_window_end ? new Date(drift.current_window_end).toLocaleString() : 'N/A'}</p>
          <p><strong>Reference DB:</strong> {drift.reference_dataset_id || 'Last 24h (Dynamic)'}</p>
        </div>
      </div>
      
      <div className="mt-6">
        <h3 className="text-lg font-medium border-b pb-2 mb-2">Distributions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-3 border rounded bg-gray-50 text-sm">
            <strong>Class Distribution</strong>
            <pre className="mt-2 text-xs overflow-auto">{JSON.stringify(drift.class_distribution, null, 2)}</pre>
          </div>
          <div className="p-3 border rounded bg-gray-50 text-sm">
            <strong>Confidence Trend</strong>
            <pre className="mt-2 text-xs overflow-auto">{JSON.stringify(drift.confidence_trend, null, 2)}</pre>
          </div>
          <div className="p-3 border rounded bg-gray-50 text-sm">
            <strong>Input Distribution</strong>
            <pre className="mt-2 text-xs overflow-auto">{JSON.stringify(drift.input_distribution, null, 2)}</pre>
          </div>
        </div>
      </div>
    </div>
  );
};
