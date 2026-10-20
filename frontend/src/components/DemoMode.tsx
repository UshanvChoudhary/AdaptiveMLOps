import React, { useState } from 'react';
import axios from 'axios';

export const DemoMode: React.FC = () => {
    const [msg, setMsg] = useState('');

    const runAction = async (endpoint: string, label: string) => {
        try {
            await axios.post(`/api/v1/demo/${endpoint}`);
            setMsg(`✅ DEMO: ${label} executed successfully.`);
        } catch (e: any) {
            setMsg(`❌ DEMO Error: ${label} failed - ${e.message}`);
        }
    };

    return (
        <div style={{ padding: '20px', border: '2px solid red', margin: '20px', borderRadius: '10px' }}>
            <h2 style={{ color: 'red' }}>⚠️ PROFESSOR DEMO MODE ⚠️</h2>
            <p>Use these controls to reliably demonstrate the MLOps lifecycle.</p>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '20px' }}>
                <button onClick={() => runAction('seed', 'Seed Database')} style={{ background: '#007bff', color: 'white' }}>Seed Data</button>
                <button onClick={() => runAction('feedback', 'Generate Feedback')} style={{ background: '#28a745', color: 'white' }}>1. Generate Feedback</button>
                <button onClick={() => runAction('retrain', 'Trigger Retraining')} style={{ background: '#17a2b8', color: 'white' }}>2. Trigger Retraining</button>
                <button onClick={() => runAction('challenger/good', 'Create Good Challenger')} style={{ background: '#ffc107' }}>3a. Create Good Challenger</button>
                <button onClick={() => runAction('challenger/bad', 'Create Bad Challenger')} style={{ background: '#dc3545', color: 'white' }}>3b. Create Bad Challenger</button>
                <button onClick={() => runAction('quality-gate', 'Run Quality Gate')} style={{ background: '#6610f2', color: 'white' }}>4. Run Quality Gate</button>
                <button onClick={() => runAction('promote', 'Promote Model')} style={{ background: '#28a745', color: 'white' }}>5. Promote Model</button>
                <button onClick={() => runAction('deploy/fail', 'Simulate Deployment Failure')} style={{ background: '#dc3545', color: 'white' }}>6. Simulate Deploy Fail</button>
                <button onClick={() => runAction('rollback', 'Rollback')} style={{ background: '#ffc107' }}>7. Rollback</button>
                <button onClick={() => runAction('drift', 'Simulate Drift')} style={{ background: '#fd7e14', color: 'white' }}>8. Simulate Drift</button>
            </div>
            {msg && <div style={{ padding: '10px', background: '#f8f9fa', border: '1px solid #ccc' }}>{msg}</div>}
        </div>
    );
};
