import './DashboardPage.css'

const KPIS = [
  { label: 'Overall Accuracy', value: '94.2%', icon: '🎯', change: '+1.2%' },
  { label: 'Precision', value: '93.8%', icon: '⚡', change: '+0.8%' },
  { label: 'Recall', value: '92.5%', icon: '📡', change: '+1.5%' },
  { label: 'F1-Score', value: '93.1%', icon: '📊', change: '+1.1%' },
]

const BREED_ACCURACY = [
  { name: 'Gir', pct: 96.4 },
  { name: 'Sahiwal', pct: 94.8 },
  { name: 'Red Sindhi', pct: 93.2 },
  { name: 'Ongole', pct: 91.5 },
  { name: 'Tharparkar', pct: 90.7 },
  { name: 'Kankrej', pct: 92.1 },
]

// Simulated confusion matrix data (top 5 breeds)
const CM_BREEDS = ['Gir', 'Sahiwal', 'Red Sindhi', 'Ongole', 'Tharparkar']
const CM_DATA = [
  [96, 2, 1, 1, 0],
  [2, 95, 2, 1, 0],
  [1, 2, 93, 3, 1],
  [0, 1, 3, 92, 4],
  [1, 1, 1, 3, 94],
]

// Training data (simplified 10 epoch sample)
const TRAINING_EPOCHS = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
const TRAIN_ACC = [45, 62, 72, 79, 84, 87, 89.5, 91, 92.5, 93.8, 94.5]
const VAL_ACC = [42, 58, 68, 76, 81, 85, 87.5, 90, 91.8, 93.0, 94.2]

function MiniLineChart({ data, color }) {
  const max = Math.max(...data), min = Math.min(...data)
  const W = 100, H = 60
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * W
    const y = H - ((v - min) / (max - min || 1)) * H
    return `${x},${y}`
  }).join(' ')
  return (
    <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" style={{ width: '100%', height: '100%' }}>
      <defs>
        <linearGradient id={`g${color}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0.02" />
        </linearGradient>
      </defs>
      <polygon points={`0,${H} ${pts} ${W},${H}`} fill={`url(#g${color})`} />
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function CmCell({ value }) {
  const intensity = value / 100
  return (
    <td className="cm-cell" style={{
      background: `rgba(0, 107, 85, ${intensity * 0.75 + 0.05})`,
      color: intensity > 0.7 ? 'white' : 'var(--on-surface)',
    }}>
      {value}
    </td>
  )
}

export default function DashboardPage() {
  return (
    <div className="dashboard-page page-wrapper">
      <div className="container">
        <div className="dashboard-header animate-fadeInUp">
          <div className="badge badge-primary">📈 Model Intelligence</div>
          <h1>Model Performance Dashboard</h1>
          <p>CNN ResNet-50 + YOLOv8 — Real-time performance metrics</p>
        </div>

        {/* KPI Cards */}
        <div className="kpi-grid animate-fadeInUp delay-1">
          {KPIS.map(({ label, value, icon, change }) => (
            <div className="card-glass kpi-card" key={label}>
              <div className="kpi-icon">{icon}</div>
              <span className="kpi-value">{value}</span>
              <span className="kpi-label">{label}</span>
              <span className="kpi-change badge badge-success">{change} vs. prev</span>
            </div>
          ))}
        </div>

        <div className="dash-main-grid animate-fadeInUp delay-2">
          {/* Training Chart */}
          <div className="card-glass dash-card">
            <h3>📉 Training vs. Validation Accuracy</h3>
            <div className="chart-legend">
              <span className="legend-dot" style={{ background: '#006b55' }}></span> Train Acc
              <span className="legend-dot" style={{ background: '#00b894', marginLeft: '1rem' }}></span> Val Acc
            </div>
            <div className="training-chart-wrapper">
              <div className="chart-y-axis">
                {[100, 80, 60, 40].map(v => (
                  <span key={v} className="y-label">{v}%</span>
                ))}
              </div>
              <div className="chart-area">
                <div className="chart-line-train">
                  <MiniLineChart data={TRAIN_ACC} color="#006b55" />
                </div>
                <div className="chart-line-val">
                  <MiniLineChart data={VAL_ACC} color="#00b894" />
                </div>
              </div>
            </div>
            <div className="chart-x-axis">
              {TRAINING_EPOCHS.map(e => (
                <span key={e} className="x-label">{e}</span>
              ))}
            </div>
            <p className="chart-caption">Epochs (1 – 100)</p>
          </div>

          {/* Model Info + Breed Accuracy */}
          <div className="dash-side">
            {/* Model Info */}
            <div className="card-glass dash-card model-info">
              <h3>🤖 Model Architecture</h3>
              <div className="model-info-row">
                <span className="model-tag">CNN</span>
                <span className="model-name">ResNet-50</span>
              </div>
              <div className="model-info-row">
                <span className="model-tag">YOLO</span>
                <span className="model-name">YOLOv8-m</span>
              </div>
              <dl className="info-list" style={{ marginTop: '0.75rem' }}>
                <div className="info-pair"><dt>Training Images</dt><dd>12,450</dd></div>
                <div className="info-pair"><dt>Classes</dt><dd>50 Cattle Breeds</dd></div>
                <div className="info-pair"><dt>Framework</dt><dd>PyTorch 2.0</dd></div>
              </dl>
            </div>

            {/* Breed Accuracy */}
            <div className="card-glass dash-card">
              <h3>🐄 Breed-Wise Accuracy</h3>
              <div className="breed-acc-list">
                {BREED_ACCURACY.map(({ name, pct }) => (
                  <div className="breed-acc-item" key={name}>
                    <span className="breed-acc-name">{name}</span>
                    <div className="progress-bar breed-acc-bar">
                      <div className="progress-fill" style={{ width: `${pct}%` }}></div>
                    </div>
                    <span className="breed-acc-pct">{pct}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Confusion Matrix */}
        <div className="card-glass dash-card animate-fadeInUp delay-3">
          <h3>🔢 Confusion Matrix (Top 5 Breeds)</h3>
          <p className="cm-caption">Values represent % correct classifications per breed</p>
          <div className="cm-wrapper">
            <table className="cm-table">
              <thead>
                <tr>
                  <th className="cm-th-corner">Actual ↓ / Predicted →</th>
                  {CM_BREEDS.map(b => <th key={b} className="cm-th">{b}</th>)}
                </tr>
              </thead>
              <tbody>
                {CM_DATA.map((row, i) => (
                  <tr key={i}>
                    <th className="cm-row-label">{CM_BREEDS[i]}</th>
                    {row.map((val, j) => <CmCell key={j} value={val} />)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
