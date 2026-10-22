import React, { useState, useEffect } from 'react';
import axios from 'axios';

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

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      'X-API-Key': 'secret-admin-key',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    };
  };

  const fetchJobs = async () => {
    try {
      const res = await axios.get('/api/v1/retraining/jobs', {
        headers: getAuthHeaders()
      });
      setJobs(res.data.jobs || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const triggerRetraining = async (triggerType: string) => {
    setTriggering(true);
    try {
      const res = await axios.post('/api/v1/retraining/trigger', 
        { trigger_type: triggerType, reason: 'Manual trigger from UI' },
        { 
          headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders()
          } 
        }
      );
      alert('Retraining job triggered successfully');
      fetchJobs();
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.message;
      alert(`Error triggering retraining: ${detail}`);
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
          style={{ padding: '8px 16px', marginRight: '10px', cursor: 'pointer', background: '#2563eb', color: '#fff', border: 'none', borderRadius: '4px' }}
        >
          {triggering ? 'Triggering...' : 'Trigger Manual Retraining'}
        </button>
        <button 
          onClick={() => triggerRetraining('FEEDBACK_THRESHOLD')} 
          disabled={triggering}
          style={{ padding: '8px 16px', cursor: 'pointer', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '4px' }}
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
            <tr style={{ backgroundColor: '#1e293b', color: '#94a3b8', textAlign: 'left' }}>
              <th style={{ padding: '10px', border: '1px solid #334155' }}>ID</th>
              <th style={{ padding: '10px', border: '1px solid #334155' }}>Trigger</th>
              <th style={{ padding: '10px', border: '1px solid #334155' }}>Reason</th>
              <th style={{ padding: '10px', border: '1px solid #334155' }}>Feedback Count</th>
              <th style={{ padding: '10px', border: '1px solid #334155' }}>Dataset ID</th>
              <th style={{ padding: '10px', border: '1px solid #334155' }}>Candidate Model ID</th>
              <th style={{ padding: '10px', border: '1px solid #334155' }}>Status</th>
              <th style={{ padding: '10px', border: '1px solid #334155' }}>Timeline</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job) => (
              <tr key={job.id} style={{ borderBottom: '1px solid #334155' }}>
                <td style={{ padding: '10px', border: '1px solid #334155', fontSize: '0.85em' }}>{job.id.substring(0, 8)}...</td>
                <td style={{ padding: '10px', border: '1px solid #334155' }}>{job.trigger_type}</td>
                <td style={{ padding: '10px', border: '1px solid #334155' }}>{job.reason || 'N/A'}</td>
                <td style={{ padding: '10px', border: '1px solid #334155' }}>{job.feedback_count}</td>
                <td style={{ padding: '10px', border: '1px solid #334155', fontSize: '0.85em' }}>{job.dataset_id ? job.dataset_id.substring(0, 8) + '...' : 'N/A'}</td>
                <td style={{ padding: '10px', border: '1px solid #334155', fontSize: '0.85em' }}>{job.candidate_model_version_id ? job.candidate_model_version_id.substring(0, 8) + '...' : 'N/A'}</td>
                <td style={{ padding: '10px', border: '1px solid #334155' }}>
                  <span style={{ 
                    padding: '4px 8px', 
                    borderRadius: '4px',
                    backgroundColor: job.status === 'COMPLETED' ? '#14532d' : 
                                   job.status === 'FAILED' ? '#7f1d1d' : 
                                   job.status === 'RUNNING' ? '#1e3a8a' : '#334155',
                    color: '#fff'
                  }}>
                    {job.status}
                  </span>
                  {job.error_message && <div style={{ color: '#f87171', fontSize: '0.8em', marginTop: '4px' }}>{job.error_message}</div>}
                </td>
                <td style={{ padding: '10px', border: '1px solid #334155', fontSize: '0.85em' }}>
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
