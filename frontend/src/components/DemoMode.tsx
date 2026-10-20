import React, { useState } from 'react';
import axios from 'axios';

interface DemoStep {
  endpoint: string;
  number: string;
  title: string;
  description: string;
  inspectTab: string;
  badgeColor: string;
}

export const DemoMode: React.FC = () => {
  const [loading, setLoading] = useState<string | null>(null);
  const [lastAction, setLastAction] = useState<{
    title: string;
    status: 'success' | 'error';
    message: string;
    inspectTab: string;
    details?: string;
  } | null>(null);

  const demoSteps: DemoStep[] = [
    {
      endpoint: 'seed',
      number: 'Step 0',
      title: 'Seed Production Baseline',
      description: 'Initializes Dataset, TrainingRun, ModelVersion v1.0 (DEPLOYED), and initial production deployment record.',
      inspectTab: 'Model Registry',
      badgeColor: '#2563eb'
    },
    {
      endpoint: 'feedback',
      number: 'Step 1',
      title: 'Generate Production Feedback',
      description: 'Simulates customer interactions and user feedback on model inferences stored in the feedback table.',
      inspectTab: 'Predictions & Feedback',
      badgeColor: '#10b981'
    },
    {
      endpoint: 'retrain',
      number: 'Step 2',
      title: 'Trigger Automated Retraining',
      description: 'Simulates retraining pipeline triggering once feedback volume crosses the configured trigger threshold.',
      inspectTab: 'Retraining Engine',
      badgeColor: '#06b6d4'
    },
    {
      endpoint: 'challenger/good',
      number: 'Step 3a',
      title: 'Train High-Performing Challenger',
      description: 'Spawns Candidate Model v1.1-good with F1=0.94, Accuracy=0.94, and Latency=18ms (passes all quality gates).',
      inspectTab: 'Model Promotion',
      badgeColor: '#f59e0b'
    },
    {
      endpoint: 'challenger/bad',
      number: 'Step 3b',
      title: 'Train Degraded Challenger',
      description: 'Spawns Candidate Model v1.1-bad with F1=0.58, Accuracy=0.62, and Latency=120ms (fails quality gates).',
      inspectTab: 'Model Promotion',
      badgeColor: '#ef4444'
    },
    {
      endpoint: 'quality-gate',
      number: 'Step 4',
      title: 'Evaluate Automated Quality Gate',
      description: 'Executes quality gate rules: v1.1-good is marked APPROVED, and v1.1-bad is marked REJECTED with audit entry.',
      inspectTab: 'Model Registry',
      badgeColor: '#8b5cf6'
    },
    {
      endpoint: 'promote',
      number: 'Step 5',
      title: 'Promote Challenger to Production',
      description: 'Promotes v1.1-good to DEPLOYED champion, archives previous model v1.0, and records zero-downtime deployment.',
      inspectTab: 'Model Promotion',
      badgeColor: '#10b981'
    },
    {
      endpoint: 'deploy/fail',
      number: 'Step 6',
      title: 'Simulate Deployment Failure',
      description: 'Simulates a canary health-check failure (timeout / crash) during a bad release to demonstrate resilience.',
      inspectTab: 'Governance & Audits',
      badgeColor: '#dc2626'
    },
    {
      endpoint: 'rollback',
      number: 'Step 7',
      title: 'Automated Safety Rollback',
      description: 'Instantly rolls traffic back to the last known healthy champion (v1.0) with an immutable governance audit log.',
      inspectTab: 'Governance & Audits',
      badgeColor: '#f97316'
    },
    {
      endpoint: 'drift',
      number: 'Step 8',
      title: 'Simulate Critical Data Drift',
      description: 'Injects severe covariate shift (Drift Score 0.88 > Threshold 0.30) to trigger automated monitoring alerts.',
      inspectTab: 'Monitoring & Drift',
      badgeColor: '#ec4899'
    }
  ];

  const runAction = async (step: DemoStep) => {
    setLoading(step.endpoint);
    try {
      const res = await axios.post(`/api/v1/demo/${step.endpoint}`);
      setLastAction({
        title: step.title,
        status: 'success',
        message: res.data?.status || 'Action executed successfully.',
        inspectTab: step.inspectTab,
        details: JSON.stringify(res.data)
      });
    } catch (e: any) {
      setLastAction({
        title: step.title,
        status: 'error',
        message: e.response?.data?.detail || e.message,
        inspectTab: step.inspectTab
      });
    } finally {
      setLoading(null);
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', textAlign: 'left', color: '#f8fafc' }}>
      <div style={{
        background: 'linear-gradient(135deg, #1e1b4b, #1e293b)',
        border: '1px solid #4338ca',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '24px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.4)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <h2 style={{ margin: 0, fontSize: '22px', color: '#c7d2fe', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span>🎓</span> Interactive Professor Demo Controls
          </h2>
          <span style={{ fontSize: '12px', background: '#312e81', color: '#a5b4fc', padding: '4px 10px', borderRadius: '12px', border: '1px solid #4338ca' }}>
            Autonomous CI/CD & MLOps Lifecycle
          </span>
        </div>
        <p style={{ margin: 0, fontSize: '14px', color: '#94a3b8', lineHeight: '1.5' }}>
          Execute each phase of the adaptive MLOps pipeline with a single click. Every action generates verifiable records in the PostgreSQL database, triggers lifecycle state transitions, and creates immutable audit logs.
        </p>
      </div>

      {/* FEEDBACK STATUS BANNER */}
      {lastAction && (
        <div style={{
          background: lastAction.status === 'success' ? '#064e3b' : '#7f1d1d',
          border: `1px solid ${lastAction.status === 'success' ? '#059669' : '#dc2626'}`,
          borderRadius: '8px',
          padding: '16px 20px',
          marginBottom: '24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <div style={{ fontWeight: 'bold', fontSize: '15px', color: '#fff', marginBottom: '4px' }}>
              {lastAction.status === 'success' ? '✓ Executed: ' : '✗ Error in: '} {lastAction.title}
            </div>
            <div style={{ fontSize: '13px', color: '#e2e8f0' }}>
              {lastAction.message}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '12px', color: '#a7f3d0' }}>
              Inspect output in tab:
            </span>
            <div style={{ fontWeight: 'bold', color: '#fff', fontSize: '14px' }}>
              👉 "{lastAction.inspectTab}"
            </div>
          </div>
        </div>
      )}

      {/* STEP GRID */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(460px, 1fr))', gap: '16px' }}>
        {demoSteps.map((step) => {
          const isCurrentLoading = loading === step.endpoint;
          return (
            <div
              key={step.endpoint}
              style={{
                background: '#1e293b',
                border: '1px solid #334155',
                borderRadius: '8px',
                padding: '18px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{
                    fontSize: '11px',
                    fontWeight: 'bold',
                    background: step.badgeColor,
                    color: '#fff',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    textTransform: 'uppercase'
                  }}>
                    {step.number}
                  </span>
                  <span style={{ fontSize: '12px', color: '#64748b' }}>
                    View in: <strong style={{ color: '#94a3b8' }}>{step.inspectTab}</strong>
                  </span>
                </div>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '16px', color: '#f8fafc' }}>
                  {step.title}
                </h4>
                <p style={{ margin: 0, fontSize: '13px', color: '#94a3b8', lineHeight: '1.4' }}>
                  {step.description}
                </p>
              </div>

              <button
                onClick={() => runAction(step)}
                disabled={loading !== null}
                style={{
                  marginTop: '16px',
                  background: isCurrentLoading ? '#475569' : step.badgeColor,
                  color: '#fff',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '9px 16px',
                  fontSize: '13px',
                  fontWeight: 'bold',
                  cursor: loading !== null ? 'wait' : 'pointer',
                  transition: 'opacity 0.2s',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                {isCurrentLoading ? 'Executing Action...' : `▶ Execute ${step.number}`}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};
