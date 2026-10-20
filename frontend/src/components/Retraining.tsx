import React, { useState, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

interface RetrainingJob {
  id: string;
  trigger_type: string;
  reason: string | null;
  feedback_count: number;
  dataset_id: string | null;
  candidate_model_version_id: string | null;
  status: string;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export const Retraining: React.FC = () => {
  const [jobs, setJobs] = useState<RetrainingJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [triggering, setTriggering] = useState(false);

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const res = await fetch(`${API_URL}/retraining/jobs`);
      if (!res.ok) throw new Error('Failed to fetch retraining jobs');
      const data = await res.json();
      setJobs(data.jobs || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const triggerRetraining = async (triggerType: string) => {
    setTriggering(true);
    try {
      const res = await fetch(`${API_URL}/retraining/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ trigger_type: triggerType, reason: 'Manual trigger from UI' })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to trigger job');
      }
      alert('Retraining job triggered successfully');
      fetchJobs();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setTriggering(false);
    }
  };

  if (loading) return <div>Loading retraining jobs...</div>;

  return (
    <div className="retraining-container" style={{ padding: '20px' }}>
      <h2>Retraining Jobs</h2>
      
      <div style={{ marginBottom: '20px' }}>
        <button 
          onClick={() => triggerRetraining('MANUAL')} 
          disabled={triggering}
          style={{ padding: '8px 16px', marginRight: '10px', cursor: 'pointer' }}
        >
          {triggering ? 'Triggering...' : 'Trigger Manual Retraining'}
        </button>
        <button 
          onClick={() => triggerRetraining('FEEDBACK_THRESHOLD')} 
          disabled={triggering}
          style={{ padding: '8px 16px', cursor: 'pointer' }}
        >
          {triggering ? 'Triggering...' : 'Trigger Feedback Retraining'}
        </button>
      </div>

      {error && <div style={{ color: 'red', marginBottom: '20px' }}>Error: {error}</div>}

      {jobs.length === 0 ? (
        <p>No retraining jobs found.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f2f2f2', textAlign: 'left' }}>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>ID</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Trigger</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Reason</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Feedback Count</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Dataset ID</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Candidate Model ID</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Status</th>
              <th style={{ padding: '10px', border: '1px solid #ddd' }}>Timeline</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job) => (
              <tr key={job.id}>
                <td style={{ padding: '10px', border: '1px solid #ddd', fontSize: '0.85em' }}>{job.id.substring(0, 8)}...</td>
                <td style={{ padding: '10px', border: '1px solid #ddd' }}>{job.trigger_type}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd' }}>{job.reason || 'N/A'}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd' }}>{job.feedback_count}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd', fontSize: '0.85em' }}>{job.dataset_id ? job.dataset_id.substring(0, 8) + '...' : 'N/A'}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd', fontSize: '0.85em' }}>{job.candidate_model_version_id ? job.candidate_model_version_id.substring(0, 8) + '...' : 'N/A'}</td>
                <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                  <span style={{ 
                    padding: '4px 8px', 
                    borderRadius: '4px',
                    backgroundColor: job.status === 'COMPLETED' ? '#d4edda' : 
                                   job.status === 'FAILED' ? '#f8d7da' : 
                                   job.status === 'RUNNING' ? '#cce5ff' : '#e2e3e5'
                  }}>
                    {job.status}
                  </span>
                  {job.error_message && <div style={{ color: 'red', fontSize: '0.8em', marginTop: '4px' }}>{job.error_message}</div>}
                </td>
                <td style={{ padding: '10px', border: '1px solid #ddd', fontSize: '0.85em' }}>
                  <div>Created: {new Date(job.created_at).toLocaleString()}</div>
                  {job.started_at && <div>Started: {new Date(job.started_at).toLocaleString()}</div>}
                  {job.completed_at && <div>Finished: {new Date(job.completed_at).toLocaleString()}</div>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
