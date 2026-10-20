import { useState, useEffect } from 'react';
import axios from 'axios';

interface Approval {
  id: string;
  model_version_id: string;
  status: string;
  reviewer: string | null;
  comments: string | null;
  created_at: string;
}

interface AuditLog {
  id: string;
  action: string;
  actor: string;
  resource_id: string | null;
  resource_type: string | null;
  details: string | null;
  created_at: string;
}

export function Governance() {
  const [activeTab, setActiveTab] = useState<'approvals' | 'audit_logs' | 'rollback'>('approvals');

  return (
    <div className="p-4 bg-white rounded-lg shadow mt-4">
      <h2 className="text-2xl font-bold mb-4">Governance & Security</h2>
      
      <div className="flex space-x-4 mb-4 border-b">
        <button
          className={"pb-2 " + (activeTab === 'approvals' ? 'border-b-2 border-blue-500 font-bold' : '')}
          onClick={() => setActiveTab('approvals')}
        >
          Approvals
        </button>
        <button
          className={"pb-2 " + (activeTab === 'audit_logs' ? 'border-b-2 border-blue-500 font-bold' : '')}
          onClick={() => setActiveTab('audit_logs')}
        >
          Audit Logs
        </button>
        <button
          className={"pb-2 " + (activeTab === 'rollback' ? 'border-b-2 border-blue-500 font-bold' : '')}
          onClick={() => setActiveTab('rollback')}
        >
          Rollback
        </button>
      </div>

      {activeTab === 'approvals' && <ApprovalsView />}
      {activeTab === 'audit_logs' && <AuditLogsView />}
      {activeTab === 'rollback' && <RollbackView />}
    </div>
  );
}

function ApprovalsView() {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchApprovals = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/v1/governance/approvals', {
        headers: { 'X-API-Key': 'secret-reviewer-key' }
      });
      setApprovals(res.data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchApprovals();
  }, []);

  return (
    <div>
      <h3 className="text-xl mb-2">Pending & Past Approvals</h3>
      <button onClick={fetchApprovals} className="mb-4 bg-gray-200 px-3 py-1 rounded">Refresh</button>
      {loading ? <p>Loading...</p> : (
        <table className="min-w-full text-sm">
          <thead>
            <tr className="bg-gray-100">
              <th className="p-2 text-left">ID</th>
              <th className="p-2 text-left">Model Version</th>
              <th className="p-2 text-left">Status</th>
              <th className="p-2 text-left">Reviewer</th>
              <th className="p-2 text-left">Date</th>
            </tr>
          </thead>
          <tbody>
            {approvals.map(appr => (
              <tr key={appr.id} className="border-b">
                <td className="p-2">{appr.id.substring(0,8)}</td>
                <td className="p-2">{appr.model_version_id.substring(0,8)}</td>
                <td className="p-2">{appr.status}</td>
                <td className="p-2">{appr.reviewer || 'N/A'}</td>
                <td className="p-2">{new Date(appr.created_at).toLocaleString()}</td>
              </tr>
            ))}
            {approvals.length === 0 && (
              <tr><td colSpan={5} className="p-2 text-center text-gray-500">No approvals found.</td></tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}

function AuditLogsView() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/v1/governance/audit-logs', {
        headers: { 'X-API-Key': 'secret-admin-key' }
      });
      setLogs(res.data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <div>
      <h3 className="text-xl mb-2">System Audit Logs</h3>
      <button onClick={fetchLogs} className="mb-4 bg-gray-200 px-3 py-1 rounded">Refresh</button>
      {loading ? <p>Loading...</p> : (
        <table className="min-w-full text-sm">
          <thead>
            <tr className="bg-gray-100">
              <th className="p-2 text-left">Date</th>
              <th className="p-2 text-left">Action</th>
              <th className="p-2 text-left">Actor</th>
              <th className="p-2 text-left">Resource</th>
              <th className="p-2 text-left">Details</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.id} className="border-b">
                <td className="p-2">{new Date(log.created_at).toLocaleString()}</td>
                <td className="p-2 font-mono text-xs">{log.action}</td>
                <td className="p-2">{log.actor}</td>
                <td className="p-2">{log.resource_type}: {log.resource_id?.substring(0,8)}</td>
                <td className="p-2">{log.details}</td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr><td colSpan={5} className="p-2 text-center text-gray-500">No logs found.</td></tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}

function RollbackView() {
  const [version, setVersion] = useState('');
  const [reason, setReason] = useState('');
  const [msg, setMsg] = useState('');
  
  const handleRollback = async () => {
    if (!version) return;
    try {
      const res = await axios.post("/api/v1/governance/models/" + version + "/rollback", { reason }, {
        headers: { 'X-API-Key': 'secret-admin-key' }
      });
      setMsg("Success: Rolled back to " + res.data.rolled_back_to);
    } catch (err: any) {
      setMsg("Error: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="max-w-md">
      <h3 className="text-xl mb-4 text-red-600 font-bold">Emergency Rollback</h3>
      <div className="mb-4">
        <label className="block mb-1">Current Problematic Version Tag (e.g. v2.0)</label>
        <input 
          className="border p-2 w-full"
          value={version}
          onChange={e => setVersion(e.target.value)}
          placeholder="v2.0"
        />
      </div>
      <div className="mb-4">
        <label className="block mb-1">Rollback Reason</label>
        <textarea 
          className="border p-2 w-full"
          value={reason}
          onChange={e => setReason(e.target.value)}
          placeholder="Severe drift detected in production."
        />
      </div>
      <button 
        onClick={handleRollback}
        className="bg-red-500 text-white px-4 py-2 rounded font-bold"
      >
        Trigger Rollback
      </button>
      {msg && <div className="mt-4 p-2 bg-gray-100">{msg}</div>}
    </div>
  );
}

