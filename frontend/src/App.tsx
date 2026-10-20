import { useState, useEffect } from 'react';
import axios from 'axios';
import { PredictionFlow } from './components/PredictionFlow';
import { ModelRegistry } from './components/ModelRegistry';
import { Retraining } from './components/Retraining';
import { ModelPromotion } from './components/ModelPromotion';
import { MonitoringDashboard } from './components/MonitoringDashboard';
import { DriftDashboard } from './components/DriftDashboard';
import { Governance } from './components/Governance';
import { DemoMode } from './components/DemoMode';
import { SystemLifecycle } from './components/SystemLifecycle';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState<'prediction' | 'registry' | 'retraining' | 'promotion' | 'monitoring' | 'governance' | 'demo' | 'lifecycle'>('prediction');
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('password');

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    try {
      const res = await axios.post('/api/v1/auth/token', params);
      const access_token = res.data.access_token;
      setToken(access_token);
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    } catch (err) {
      alert("Login failed");
    }
  };

  if (!token) {
    return (
      <div style={{ padding: '50px', textAlign: 'center', background: '#0f172a', minHeight: '100vh', color: '#fff' }}>
        <h2>Login to AdaptiveMLOps</h2>
        <form onSubmit={handleLogin} style={{ maxWidth: '300px', margin: '0 auto', background: '#1e293b', padding: '30px', borderRadius: '8px' }}>
          <input 
            value={username} 
            onChange={e => setUsername(e.target.value)} 
            placeholder="Username" 
            style={{ width: '100%', padding: '10px', marginBottom: '10px', borderRadius: '4px', background: '#0f172a', color: '#fff', border: '1px solid #334155' }} 
          /><br/>
          <input 
            type="password" 
            value={password} 
            onChange={e => setPassword(e.target.value)} 
            placeholder="Password" 
            style={{ width: '100%', padding: '10px', marginBottom: '20px', borderRadius: '4px', background: '#0f172a', color: '#fff', border: '1px solid #334155' }} 
          /><br/>
          <button 
            type="submit" 
            style={{ width: '100%', padding: '10px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: '4px', fontWeight: 'bold', cursor: 'pointer' }}
          >
            Sign In
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="App" style={{ minHeight: '100vh', background: '#0f172a', color: '#f8fafc' }}>
      <header className="App-header" style={{ padding: '20px', borderBottom: '1px solid #1e293b' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', maxWidth: '1200px', margin: '0 auto 20px auto' }}>
          <h1 style={{ margin: 0, fontSize: '24px', letterSpacing: '-0.5px' }}>
            AdaptiveMLOps <span style={{ fontSize: '13px', background: '#2563eb', padding: '3px 8px', borderRadius: '4px', verticalAlign: 'middle' }}>v1.0 Production</span>
          </h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
            <span style={{ fontSize: '13px', color: '#94a3b8' }}>User: <strong style={{ color: '#f8fafc' }}>{username} (Admin)</strong></span>
            <button 
              onClick={() => { setToken(null); localStorage.removeItem('token'); }} 
              style={{ fontSize: '12px', padding: '5px 12px', background: '#ef4444', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            >
              Logout
            </button>
          </div>
        </div>
        
        <nav style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', justifyContent: 'center' }}>
          {[
            { key: 'prediction', label: 'Predictions & Feedback' },
            { key: 'registry', label: 'Model Registry' },
            { key: 'retraining', label: 'Retraining Engine' },
            { key: 'promotion', label: 'Model Promotion' },
            { key: 'monitoring', label: 'Monitoring & Drift' },
            { key: 'demo', label: '★ Professor Demo Controls', highlight: true },
            { key: 'lifecycle', label: 'System Lifecycle' },
            { key: 'governance', label: 'Governance & Audits' },
          ].map(tab => (
            <button 
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              style={{ 
                padding: '8px 16px',
                borderRadius: '6px',
                border: tab.key === activeTab ? '1px solid #3b82f6' : '1px solid #334155',
                background: tab.key === activeTab ? '#1e3a8a' : (tab.highlight ? '#450a0a' : '#1e293b'),
                color: tab.key === activeTab ? '#60a5fa' : (tab.highlight ? '#f87171' : '#cbd5e1'),
                fontWeight: tab.key === activeTab ? 'bold' : 'normal',
                cursor: 'pointer',
                fontSize: '13px',
                transition: 'all 0.15s ease-in-out'
              }}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </header>
      
      <main style={{ padding: '30px 20px', maxWidth: '1200px', margin: '0 auto' }}>
        {activeTab === 'prediction' && <PredictionFlow />}
        {activeTab === 'registry' && <ModelRegistry />}
        {activeTab === 'retraining' && <Retraining />}
        {activeTab === 'promotion' && <ModelPromotion />}
        {activeTab === 'monitoring' && <><MonitoringDashboard /><DriftDashboard /></>}
        {activeTab === 'governance' && <Governance />}
        {activeTab === 'demo' && <><DemoMode /><SystemLifecycle /></>}
        {activeTab === 'lifecycle' && <SystemLifecycle />}
      </main>
    </div>
  );
}

export default App;
