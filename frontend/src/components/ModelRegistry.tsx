import React, { useState, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

interface ModelVersion {
  id: string;
  version: string;
  algorithm: string;
  status: string;
  created_at: string;
  artifact_path: string;
  training_run: {
    git_commit: string;
    hyperparameters: any;
    status: string;
    dataset: {
      version: string;
      checksum: string;
    } | null;
  } | null;
  evaluations: any[];
}

export const ModelRegistry: React.FC = () => {
  const [models, setModels] = useState<ModelVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      const res = await fetch(`${API_URL}/models/`);
      if (!res.ok) throw new Error('Failed to fetch models');
      const data = await res.json();
      setModels(data.models || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading registry...</div>;
  if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;

  return (
    <div className="registry-container" style={{ padding: '20px' }}>
      <h2>Model Registry</h2>
      
      {models.length === 0 ? (
        <p>No models registered yet.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
          <thead>
            <tr style={{ backgroundColor: '#f2f2f2', textAlign: 'left' }}>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Version</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Algorithm</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Dataset</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Training Date</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Git Commit</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Status</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Metrics</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Artifact</th>
            </tr>
          </thead>
          <tbody>
            {models.map((model) => (
              <tr key={model.id}>
                <td style={{ padding: '10px', border: '1px solid #ddd' }}>{model.version}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd' }}>{model.algorithm}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                  {model.training_run?.dataset ? model.training_run.dataset.version : 'N/A'}
                </td>
                <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                  {new Date(model.created_at).toLocaleString()}
                </td>
                <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                  {model.training_run ? model.training_run.git_commit.substring(0, 7) : 'N/A'}
                </td>
                <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                  <span style={{ 
                    padding: '4px 8px', 
                    borderRadius: '4px',
                    backgroundColor: model.status === 'PRODUCTION' ? '#d4edda' : 
                                   model.status === 'REJECTED' ? '#f8d7da' : '#e2e3e5'
                  }}>
                    {model.status}
                  </span>
                </td>
                <td style={{ padding: '10px', border: '1px solid #ddd', fontSize: '0.85em' }}>
                  {model.evaluations && model.evaluations.length > 0 ? (
                    <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                      {JSON.stringify(model.evaluations[model.evaluations.length - 1].metrics, null, 2)}
                    </pre>
                  ) : (
                    'No evals'
                  )}
                </td>
                <td style={{ padding: '10px', border: '1px solid #ddd', fontSize: '0.85em' }}>
                  {model.artifact_path}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
