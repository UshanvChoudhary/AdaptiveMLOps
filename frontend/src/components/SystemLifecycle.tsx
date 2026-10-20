import React from 'react';

export const SystemLifecycle: React.FC = () => {
    const steps = [
        "Prediction", "Feedback", "Retraining Trigger", "Training", "Evaluation",
        "Champion vs Challenger", "Quality Gate", "Jenkins", "Docker",
        "Deployment", "Health Check", "Production", "Monitoring", "Rollback"
    ];

    return (
        <div style={{ padding: '20px', border: '1px solid #ccc', margin: '20px', borderRadius: '10px' }}>
            <h2>System Lifecycle</h2>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '5px' }}>
                {steps.map((step, idx) => (
                    <React.Fragment key={idx}>
                        <div style={{ padding: '10px', border: '1px solid #007bff', borderRadius: '5px', width: '250px', textAlign: 'center', background: '#e9ecef', fontWeight: 'bold' }}>
                            {step}
                        </div>
                        {idx < steps.length - 1 && <div style={{ fontSize: '20px' }}>↓</div>}
                    </React.Fragment>
                ))}
            </div>
        </div>
    );
};
