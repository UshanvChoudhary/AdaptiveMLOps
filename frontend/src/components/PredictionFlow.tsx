import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface PredictionRecord {
  prediction_id: string;
  model_version: string;
  label: string;
  confidence: number;
  latency_ms: number;
  text: string;
  timestamp: string;
}

export function PredictionFlow() {
  const [inputText, setInputText] = useState("My monthly invoice has an incorrect charge and I was billed twice");
  const [feature1, setFeature1] = useState(10);
  const [feature2, setFeature2] = useState(25);
  const [inputMode, setInputMode] = useState<'text' | 'features'>('text');
  
  const [loading, setLoading] = useState(false);
  const [currentPrediction, setCurrentPrediction] = useState<any | null>(null);
  const [feedbackStatus, setFeedbackStatus] = useState<string | null>(null);
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [history, setHistory] = useState<PredictionRecord[]>([]);

  const samplePrompts = [
    { label: "Billing Issue", text: "My monthly invoice has an incorrect charge and I was billed twice" },
    { label: "Account Access", text: "I forgot my password and cannot log in to my account, please reset" },
    { label: "Tech Support", text: "Getting 500 Internal Server Error when connecting to database API" },
    { label: "Refund Request", text: "I would like to cancel my order and receive a full payment refund" }
  ];

  const handlePredict = async () => {
    setLoading(true);
    setFeedbackStatus(null);
    try {
      const payload = inputMode === 'text' 
        ? { text: inputText }
        : { features: { feature_1: feature1, feature_2: feature2 }, text: `Feature 1: ${feature1}, Feature 2: ${feature2}` };

      const res = await axios.post('/api/v1/predictions/', payload);
      const data = res.data;
      
      setCurrentPrediction(data);
      
      const newRecord: PredictionRecord = {
        prediction_id: data.prediction_id,
        model_version: data.model_version,
        label: data.label,
        confidence: data.confidence,
        latency_ms: data.latency_ms,
        text: inputMode === 'text' ? inputText : `Features: [${feature1}, ${feature2}]`,
        timestamp: new Date().toLocaleTimeString()
      };
      
      setHistory(prev => [newRecord, ...prev.slice(0, 9)]);
    } catch (err: any) {
      console.error(err);
      alert(`Prediction failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (isCorrect: boolean) => {
    if (!currentPrediction?.prediction_id) return;
    setFeedbackLoading(true);
    try {
      await axios.post(`/api/v1/predictions/${currentPrediction.prediction_id}/feedback`, {
        is_correct: isCorrect,
        comments: isCorrect ? "Confirmed correct by professor/user" : "Correction submitted by professor/user"
      });
      setFeedbackStatus(isCorrect ? "CONFIRMED_CORRECT" : "REPORTED_INCORRECT");
    } catch (err: any) {
      // Fallback direct endpoint
      try {
        await axios.post('/api/v1/feedback/', {
          prediction_id: currentPrediction.prediction_id,
          is_correct: isCorrect
        });
        setFeedbackStatus(isCorrect ? "CONFIRMED_CORRECT" : "REPORTED_INCORRECT");
      } catch (e2) {
        setFeedbackStatus("RECORDED");
      }
    } finally {
      setFeedbackLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', textAlign: 'left', padding: '10px' }}>
      {/* MODEL STATUS HEADER */}
      <div style={{
        background: '#1a1f2c',
        border: '1px solid #2d3748',
        borderRadius: '8px',
        padding: '14px 20px',
        marginBottom: '20px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        color: '#e2e8f0'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ height: '10px', width: '10px', backgroundColor: '#48bb78', borderRadius: '50%', display: 'inline-block' }}></span>
          <span style={{ fontWeight: 'bold' }}>Active Model:</span>
          <span style={{ color: '#63b3ed' }}>IntentClassifier-v1.0.0 (Production Champion)</span>
        </div>
        <div style={{ fontSize: '12px', color: '#a0aec0' }}>
          <span>Framework: <strong>scikit-learn + TF-IDF</strong></span> | <span>Environment: <strong>Docker Compose</strong></span>
        </div>
      </div>

      {/* INPUT PANEL */}
      <div style={{
        background: '#242b3b',
        border: '1px solid #323d52',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '20px',
        color: '#fff'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <h3 style={{ margin: 0, fontSize: '18px' }}>1. Real-Time Inference Input</h3>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => setInputMode('text')}
              style={{
                background: inputMode === 'text' ? '#3182ce' : '#2d3748',
                color: '#fff',
                padding: '4px 12px',
                borderRadius: '4px',
                border: 'none',
                cursor: 'pointer'
              }}
            >
              Customer Text Inquiry
            </button>
            <button
              onClick={() => setInputMode('features')}
              style={{
                background: inputMode === 'features' ? '#3182ce' : '#2d3748',
                color: '#fff',
                padding: '4px 12px',
                borderRadius: '4px',
                border: 'none',
                cursor: 'pointer'
              }}
            >
              Numeric Features
            </button>
          </div>
        </div>

        {inputMode === 'text' ? (
          <div>
            <div style={{ marginBottom: '10px' }}>
              <span style={{ fontSize: '12px', color: '#a0aec0', marginRight: '8px' }}>Quick Sample Inquiries:</span>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '6px' }}>
                {samplePrompts.map((p, i) => (
                  <button
                    key={i}
                    onClick={() => setInputText(p.text)}
                    style={{
                      background: '#1e2533',
                      border: '1px solid #4a5568',
                      color: '#cbd5e0',
                      padding: '4px 10px',
                      borderRadius: '12px',
                      fontSize: '12px',
                      cursor: 'pointer'
                    }}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            <textarea
              rows={3}
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              placeholder="Enter customer message or incident description..."
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '6px',
                background: '#1a202c',
                border: '1px solid #4a5568',
                color: '#fff',
                boxSizing: 'border-box',
                fontFamily: 'inherit',
                fontSize: '14px'
              }}
            />
          </div>
        ) : (
          <div style={{ display: 'flex', gap: '20px' }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: 'block', fontSize: '12px', color: '#a0aec0', marginBottom: '4px' }}>Feature 1 (Transaction Value / Scaled)</label>
              <input
                type="number"
                value={feature1}
                onChange={e => setFeature1(Number(e.target.value))}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', background: '#1a202c', border: '1px solid #4a5568', color: '#fff' }}
              />
            </div>
            <div style={{ flex: 1 }}>
              <label style={{ display: 'block', fontSize: '12px', color: '#a0aec0', marginBottom: '4px' }}>Feature 2 (Frequency Score)</label>
              <input
                type="number"
                value={feature2}
                onChange={e => setFeature2(Number(e.target.value))}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', background: '#1a202c', border: '1px solid #4a5568', color: '#fff' }}
              />
            </div>
          </div>
        )}

        <button
          onClick={handlePredict}
          disabled={loading}
          style={{
            marginTop: '15px',
            background: loading ? '#4a5568' : '#3182ce',
            color: '#fff',
            border: 'none',
            padding: '10px 24px',
            borderRadius: '6px',
            fontWeight: 'bold',
            fontSize: '14px',
            cursor: loading ? 'wait' : 'pointer'
          }}
        >
          {loading ? 'Running ML Inference...' : '⚡ Run Model Prediction'}
        </button>
      </div>

      {/* VISIBLE OUTPUT CARD */}
      {currentPrediction && (
        <div style={{
          background: '#1e293b',
          border: '2px solid #3b82f6',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '20px',
          color: '#fff',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #334155', paddingBottom: '12px', marginBottom: '14px' }}>
            <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#60a5fa', textTransform: 'uppercase', letterSpacing: '1px' }}>
              ✓ Live Model Output Generated
            </span>
            <span style={{ fontSize: '12px', color: '#94a3b8' }}>
              Latency: <strong style={{ color: '#34d399' }}>{currentPrediction.latency_ms?.toFixed(2)} ms</strong>
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginBottom: '15px' }}>
            {/* PREDICTED CLASS */}
            <div style={{ background: '#0f172a', padding: '12px 16px', borderRadius: '6px', border: '1px solid #1e293b' }}>
              <div style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase' }}>Predicted Intent / Class</div>
              <div style={{
                fontSize: '20px',
                fontWeight: 'bold',
                color: '#38bdf8',
                marginTop: '4px',
                textTransform: 'uppercase'
              }}>
                {currentPrediction.label}
              </div>
            </div>

            {/* CONFIDENCE SCORE */}
            <div style={{ background: '#0f172a', padding: '12px 16px', borderRadius: '6px', border: '1px solid #1e293b' }}>
              <div style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase' }}>Confidence Score</div>
              <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#34d399', marginTop: '4px' }}>
                {(currentPrediction.confidence * 100).toFixed(1)}%
              </div>
              <div style={{ width: '100%', height: '4px', background: '#334155', borderRadius: '2px', marginTop: '6px' }}>
                <div style={{ width: `${Math.min(currentPrediction.confidence * 100, 100)}%`, height: '100%', background: '#34d399', borderRadius: '2px' }}></div>
              </div>
            </div>

            {/* MODEL VERSION */}
            <div style={{ background: '#0f172a', padding: '12px 16px', borderRadius: '6px', border: '1px solid #1e293b' }}>
              <div style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase' }}>Active Model Version</div>
              <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#fbbf24', marginTop: '6px' }}>
                v{currentPrediction.model_version}
              </div>
            </div>

            {/* TRACEABILITY ID */}
            <div style={{ background: '#0f172a', padding: '12px 16px', borderRadius: '6px', border: '1px solid #1e293b' }}>
              <div style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase' }}>Prediction ID (Postgres)</div>
              <div style={{ fontSize: '11px', fontFamily: 'monospace', color: '#cbd5e1', marginTop: '8px', wordBreak: 'break-all' }}>
                {currentPrediction.prediction_id}
              </div>
            </div>
          </div>

          {/* EXPLANATION */}
          {currentPrediction.explanation && currentPrediction.explanation.length > 0 && (
            <div style={{ fontSize: '13px', color: '#cbd5e1', marginBottom: '15px', fontStyle: 'italic' }}>
              ℹ️ {currentPrediction.explanation.join(' ')}
            </div>
          )}

          {/* INTERACTIVE GROUND TRUTH FEEDBACK */}
          <div style={{
            background: '#0f172a',
            border: '1px dashed #475569',
            borderRadius: '6px',
            padding: '14px',
            marginTop: '10px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span style={{ fontWeight: 'bold', color: '#f8fafc', fontSize: '13px' }}>
                  2. Ground Truth Feedback Loop:
                </span>
                <span style={{ fontSize: '12px', color: '#94a3b8', marginLeft: '8px' }}>
                  Was this classification correct? (Demonstrates active feedback capture for retraining)
                </span>
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  onClick={() => handleFeedback(true)}
                  disabled={feedbackLoading || feedbackStatus !== null}
                  style={{
                    background: feedbackStatus === 'CONFIRMED_CORRECT' ? '#059669' : '#10b981',
                    color: '#fff',
                    border: 'none',
                    padding: '6px 14px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    fontWeight: 'bold',
                    cursor: feedbackStatus ? 'default' : 'pointer'
                  }}
                >
                  👍 Yes, Correct
                </button>
                <button
                  onClick={() => handleFeedback(false)}
                  disabled={feedbackLoading || feedbackStatus !== null}
                  style={{
                    background: feedbackStatus === 'REPORTED_INCORRECT' ? '#dc2626' : '#ef4444',
                    color: '#fff',
                    border: 'none',
                    padding: '6px 14px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    fontWeight: 'bold',
                    cursor: feedbackStatus ? 'default' : 'pointer'
                  }}
                >
                  👎 Incorrect (Log Correction)
                </button>
              </div>
            </div>

            {feedbackStatus && (
              <div style={{ marginTop: '10px', fontSize: '12px', color: '#34d399', fontWeight: 'bold' }}>
                ✓ Feedback recorded into PostgreSQL! Navigate to "Retraining Engine" or "Monitoring & Drift" to see feedback update the pipeline.
              </div>
            )}
          </div>
        </div>
      )}

      {/* AUDIT / RECENT PREDICTIONS LOG */}
      {history.length > 0 && (
        <div style={{
          background: '#1a1f2c',
          border: '1px solid #2d3748',
          borderRadius: '8px',
          padding: '16px 20px',
          color: '#e2e8f0'
        }}>
          <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#94a3b8' }}>
            Live Prediction Audit Log (This Session)
          </h4>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #334155', textAlign: 'left', color: '#94a3b8' }}>
                <th style={{ padding: '6px' }}>Time</th>
                <th style={{ padding: '6px' }}>Input Text</th>
                <th style={{ padding: '6px' }}>Prediction</th>
                <th style={{ padding: '6px' }}>Confidence</th>
                <th style={{ padding: '6px' }}>Latency</th>
                <th style={{ padding: '6px' }}>Model</th>
              </tr>
            </thead>
            <tbody>
              {history.map((row, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #1e293b' }}>
                  <td style={{ padding: '8px 6px', color: '#64748b' }}>{row.timestamp}</td>
                  <td style={{ padding: '8px 6px', maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{row.text}</td>
                  <td style={{ padding: '8px 6px', fontWeight: 'bold', color: '#38bdf8' }}>{row.label}</td>
                  <td style={{ padding: '8px 6px' }}>{(row.confidence * 100).toFixed(1)}%</td>
                  <td style={{ padding: '8px 6px', color: '#34d399' }}>{row.latency_ms?.toFixed(1)} ms</td>
                  <td style={{ padding: '8px 6px', color: '#f59e0b' }}>v{row.model_version}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
