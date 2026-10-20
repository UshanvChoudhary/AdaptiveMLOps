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
      // fixed below
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
      // fixed below
    } catch (err) {
      alert("Login failed");
    }
  };

  if (!token) {
    return (
      <div style={{ padding: '50px', textAlign: 'center' }}>
        <h2>Login to AdaptiveMLOps</h2>
        <form onSubmit={handleLogin}>
          <input value={username} onChange={e => setUsername(e.target.value)} placeholder="Username" /><br/><br/>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" /><br/><br/>
          <button type="submit">Login</button>
        </form>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>AdaptiveMLOps <button onClick={() => { setToken(null); localStorage.removeItem('token'); }} style={{fontSize: '12px', marginLeft: '20px'}}>Logout</button></h1>
        <nav style={{ marginBottom: '20px' }}>
          <button 
            onClick={() => setActiveTab('prediction')}
            style={{ fontWeight: activeTab === 'prediction' ? 'bold' : 'normal', marginRight: '10px' }}
          >
            Predictions & Feedback
          </button>
          <button 
            onClick={() => setActiveTab('registry')}
            style={{ fontWeight: activeTab === 'registry' ? 'bold' : 'normal', marginRight: '10px' }}
          >
            Model Registry
          </button>
          <button 
            onClick={() => setActiveTab('retraining')}
            style={{ fontWeight: activeTab === 'retraining' ? 'bold' : 'normal', marginRight: '10px' }}
          >
            Retraining Engine
          </button>
          <button 
            onClick={() => setActiveTab('promotion')}
            style={{ fontWeight: activeTab === 'promotion' ? 'bold' : 'normal', marginRight: '10px' }}
          >
            Model Promotion
          </button>
          <button 
            onClick={() => setActiveTab('monitoring')}
            style={{ fontWeight: activeTab === 'monitoring' ? 'bold' : 'normal', marginRight: '10px' }}
          >
            Monitoring & Drift
          </button>
          <button 
            onClick={() => setActiveTab('demo')}
            style={{ fontWeight: activeTab === 'demo' ? 'bold' : 'normal', marginRight: '10px', color: 'red' }}
          >
            Demo Controls
          </button>
          <button 
            onClick={() => setActiveTab('lifecycle')}
            style={{ fontWeight: activeTab === 'lifecycle' ? 'bold' : 'normal', marginRight: '10px' }}
          >
            Lifecycle
          </button>
          <button 
            onClick={() => setActiveTab('governance')}
            style={{ fontWeight: activeTab === 'governance' ? 'bold' : 'normal' }}
          >
            Governance
          </button>
        </nav>
      </header>
      <main>
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
