import os

content = """import { useState } from 'react';
import axios from 'axios';

export function PredictionFlow() {
  const [feature1, setFeature1] = useState(0);
  const [feature2, setFeature2] = useState(0);
  const [prediction, setPrediction] = useState<number | null>(null);
  const [predictionId, setPredictionId] = useState<string | null>(null);
  const [feedbackMsg, setFeedbackMsg] = useState("");

  const handlePredict = async () => {
    try {
      const res = await axios.post('/api/v1/predict', { features: { f1: feature1, f2: feature2 } });
      setPrediction(res.data.prediction);
      setPredictionId(res.data.prediction_id || "test-id");
      setFeedbackMsg("");
    } catch (err) {
      console.error(err);
    }
  };

  const handleFeedback = async (correct: boolean) => {
    try {
      await axios.post('/api/v1/feedback', {
        prediction_id: predictionId,
        correct: correct,
        actual_class: correct ? prediction : (prediction === 1 ? 0 : 1)
      });
      setFeedbackMsg("Feedback submitted successfully");
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div>
      <h2>Make Prediction</h2>
      <div>
        <label>Feature 1: <input type="number" value={feature1} onChange={e => setFeature1(Number(e.target.value))} /></label>
      </div>
      <div>
        <label>Feature 2: <input type="number" value={feature2} onChange={e => setFeature2(Number(e.target.value))} /></label>
      </div>
      <button onClick={handlePredict}>Predict</button>
      {prediction !== null && (
        <div style={{ marginTop: '20px' }}>
          <div>Result: {prediction}</div>
          <div style={{ marginTop: '10px' }}>
            <p>Was this prediction correct?</p>
            <button onClick={() => handleFeedback(true)} style={{ marginRight: '10px' }}>Correct</button>
            <button onClick={() => handleFeedback(false)}>Incorrect</button>
          </div>
          {feedbackMsg && <div style={{ color: 'green', marginTop: '10px' }}>{feedbackMsg}</div>}
        </div>
      )}
    </div>
  );
}
"""

with open('frontend/src/components/PredictionFlow.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
