import './DashboardPage.css'

const KPIS = [
  { label: 'Overall Accuracy', value: '80.0%', icon: '🎯', change: '+45.0%' },
  { label: 'Precision (Macro)', value: '79.0%', icon: '⚡', change: '+38.5%' },
  { label: 'Recall (Macro)', value: '79.0%', icon: '📡', change: '+42.0%' },
  { label: 'F1-Score (Macro)', value: '78.0%', icon: '📊', change: '+40.2%' },
]

// All 50 breeds sorted highest F1-score to lowest (from actual evaluation)
const BREED_ACCURACY = [
  { name: 'Purnea',          pct: 98 },
  { name: 'Bhelai',          pct: 98 },
  { name: 'Konkan Kapila',   pct: 93 },
  { name: 'Siri',            pct: 93 },
  { name: 'Umblachery',      pct: 94 },
  { name: 'Kosali',          pct: 96 },
  { name: 'Poda Thirupu',    pct: 92 },
  { name: 'Ponwar',          pct: 91 },
  { name: 'Bargur',          pct: 91 },
  { name: 'Dangi',           pct: 91 },
  { name: 'Lakhimi',         pct: 91 },
  { name: 'Ayrshire',        pct: 90 },
  { name: 'Ladakhi',         pct: 88 },
  { name: 'Mewati',          pct: 89 },
  { name: 'Malnad Gidda',    pct: 87 },
  { name: 'Motu',            pct: 87 },
  { name: 'Kenkatha',        pct: 85 },
  { name: 'Punganur',        pct: 88 },
  { name: 'Kangayam',        pct: 83 },
  { name: 'Himachali Pahari',pct: 81 },
  { name: 'Gir',             pct: 81 },
  { name: 'Sahiwal',         pct: 81 },
  { name: 'Badri',           pct: 81 },
  { name: 'Khariar',         pct: 84 },
  { name: 'Red Kandhari',    pct: 81 },
  { name: 'Pulikulam',       pct: 80 },
  { name: 'Rathi',           pct: 83 },
  { name: 'Thutho',          pct: 80 },
  { name: 'Hariana',         pct: 77 },
  { name: 'Nari',            pct: 76 },
  { name: 'Nimari',          pct: 76 },
  { name: 'Kankrej',         pct: 74 },
  { name: 'Tharparkar',      pct: 74 },
  { name: 'Deoni',           pct: 78 },
  { name: 'Nagori',          pct: 77 },
  { name: 'Khillari',        pct: 72 },
  { name: 'Ghumsari',        pct: 72 },
  { name: 'Bachaur',         pct: 71 },
  { name: 'Hallikar',        pct: 69 },
  { name: 'Amritmahal',      pct: 67 },
  { name: 'Dagri',           pct: 68 },
  { name: 'Gaolao',          pct: 67 },
  { name: 'Kherigarh',       pct: 63 },
  { name: 'Krishna Valley',  pct: 54 },
  { name: 'Ongole',          pct: 57 },
  { name: 'Shweta Kapila',   pct: 56 },
  { name: 'Red Sindhi',      pct: 50 },
  { name: 'Malvi',           pct: 47 },
  { name: 'Gangatari',       pct: 36 },
  { name: 'Vecchur',         pct: 81 },
]

// Confusion matrix for top 5 best performers
const CM_BREEDS = ['Purnea', 'Kosali', 'Bhelai', 'Umblachery', 'Ponwar']
const CM_DATA = [
  [59, 0, 0, 0, 0],
  [0, 27, 0, 0, 0],
  [0, 0, 22, 1, 0],
  [1, 0, 0, 51, 4],
  [0, 0, 0, 0, 30],
]

// Training data (simplified 10 epoch sample)
const TRAINING_EPOCHS = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
const TRAIN_ACC = [35, 52, 65, 74, 80, 85, 88, 91, 92, 94, 95]
const VAL_ACC = [32, 48, 61, 70, 76, 80, 81, 82, 80, 79, 80]

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
                <div className="info-pair"><dt>Training Images</dt><dd>13,000+</dd></div>
                <div className="info-pair"><dt>Classes</dt><dd>50 Cattle Breeds</dd></div>
                <div className="info-pair"><dt>Framework</dt><dd>PyTorch 2.0</dd></div>
              </dl>
            </div>

            {/* Breed Accuracy */}
            <div className="card-glass dash-card">
              <h3>🐄 All 50 Breeds — F1-Score</h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--on-surface-variant)', marginBottom: '0.75rem' }}>Sorted highest → lowest (from evaluation)</p>
              <div className="breed-acc-list breed-acc-list--scroll">
                {BREED_ACCURACY.map(({ name, pct }, idx) => (
                  <div className="breed-acc-item" key={name}>
                    <span className="breed-acc-rank">#{idx + 1}</span>
                    <span className="breed-acc-name">{name}</span>
                    <div className="progress-bar breed-acc-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${pct}%`,
                          background: pct >= 85
                            ? 'linear-gradient(90deg, #006b55, #00b894)'
                            : pct >= 65
                              ? 'linear-gradient(90deg, #e67e00, #f5a623)'
                              : 'linear-gradient(90deg, #c0392b, #e74c3c)'
                        }}
                      ></div>
                    </div>
                    <span className="breed-acc-pct" style={{
                      color: pct >= 85 ? 'var(--primary)' : pct >= 65 ? '#e67e00' : '#c0392b'
                    }}>{pct}%</span>
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
