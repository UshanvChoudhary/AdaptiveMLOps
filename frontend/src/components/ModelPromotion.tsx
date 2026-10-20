import React, { useState, useEffect } from 'react';

interface ModelVersion {
  id: string;
  version: string;
  status: string;
  algorithm: string;
  created_at: string;
  evaluations: any[];
  training_run: {
    git_commit: string;
    dataset: {
      version: string;
    }
  };
}

export const ModelPromotion: React.FC = () => {
  const [models, setModels] = useState<ModelVersion[]>([]);
  const [champion, setChampion] = useState<ModelVersion | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<ModelVersion | null>(null);
  const [promotionResult, setPromotionResult] = useState<any>(null);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/models/');
      const data = await res.json();
      setModels(data.models);
      
      const prodModel = data.models.find((m: any) => m.status === 'PRODUCTION');
      setChampion(prodModel || null);
    } catch (e) {
      console.error(e);
    }
  };

  const handlePromote = async () => {
    if (!selectedCandidate) return;
    try {
      const res = await fetch(`http://localhost:8000/api/v1/models/${selectedCandidate.version}/promote`, {
        method: 'POST',
      });
      const data = await res.json();
      setPromotionResult(data);
      fetchModels();
    } catch (e) {
      console.error(e);
    }
  };

  const candidates = models.filter(m => m.status === 'CANDIDATE');

  const getMetrics = (model: ModelVersion) => {
    if (!model.evaluations || model.evaluations.length === 0) return null;
    return model.evaluations[model.evaluations.length - 1].metrics;
  };

  return (
    <div style={{ padding: '20px', textAlign: 'left' }}>
      <h2>Model Promotion Evaluation</h2>
      
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        {/* CHAMPION */}
        <div style={{ border: '2px solid green', padding: '15px', width: '45%' }}>
          <h3>CHAMPION (Current Production)</h3>
          {champion ? (
            <div>
              <p><strong>Version:</strong> {champion.version}</p>
              <p><strong>Algorithm:</strong> {champion.algorithm}</p>
              <p><strong>Dataset:</strong> {champion.training_run?.dataset?.version}</p>
              <p><strong>Git Commit:</strong> {champion.training_run?.git_commit}</p>
              <p><strong>Date:</strong> {new Date(champion.created_at).toLocaleString()}</p>
              <h4>Metrics</h4>
              {getMetrics(champion) ? (
                <ul>
                  <li>F1: {getMetrics(champion).f1?.toFixed(4)}</li>
                  <li>Accuracy: {getMetrics(champion).accuracy?.toFixed(4)}</li>
                  <li>Latency: {getMetrics(champion).latency_p95_ms?.toFixed(2)} ms</li>
                </ul>
              ) : (
                <p>No metrics available</p>
              )}
            </div>
          ) : (
            <p>No champion model in production.</p>
          )}
        </div>

        {/* CHALLENGER */}
        <div style={{ border: '2px solid blue', padding: '15px', width: '45%' }}>
          <h3>CHALLENGER (Candidate)</h3>
          <select 
            onChange={(e) => {
              const cand = candidates.find(c => c.version === e.target.value);
              setSelectedCandidate(cand || null);
              setPromotionResult(null);
            }}
            value={selectedCandidate?.version || ''}
          >
            <option value="">-- Select Candidate --</option>
            {candidates.map(c => (
              <option key={c.version} value={c.version}>{c.version}</option>
            ))}
          </select>

          {selectedCandidate && (
             <div style={{ marginTop: '10px' }}>
             <p><strong>Version:</strong> {selectedCandidate.version}</p>
             <p><strong>Algorithm:</strong> {selectedCandidate.algorithm}</p>
             <p><strong>Dataset:</strong> {selectedCandidate.training_run?.dataset?.version}</p>
             <p><strong>Git Commit:</strong> {selectedCandidate.training_run?.git_commit}</p>
             <p><strong>Date:</strong> {new Date(selectedCandidate.created_at).toLocaleString()}</p>
             <h4>Metrics</h4>
             {getMetrics(selectedCandidate) ? (
               <ul>
                 <li>F1: {getMetrics(selectedCandidate).f1?.toFixed(4)}</li>
                 <li>Accuracy: {getMetrics(selectedCandidate).accuracy?.toFixed(4)}</li>
                 <li>Latency: {getMetrics(selectedCandidate).latency_p95_ms?.toFixed(2)} ms</li>
               </ul>
             ) : (
               <p>No metrics available</p>
             )}
             
             <button 
                onClick={handlePromote}
                style={{ padding: '10px 20px', background: 'blue', color: 'white', marginTop: '10px', cursor: 'pointer' }}
             >
                Run Quality Gates & Promote
             </button>
           </div>
          )}
          
          {promotionResult && (
            <div style={{ marginTop: '20px', padding: '10px', background: promotionResult.decision === 'PROMOTE' ? '#d4edda' : '#f8d7da', color: 'black' }}>
              <h4>Decision: {promotionResult.decision}</h4>
              <p>Reason: {promotionResult.reason}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
