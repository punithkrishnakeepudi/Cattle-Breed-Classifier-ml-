import { useLocation, Link } from 'react-router-dom'
import './ResultPage.css'

const RESULT_DATA = {
  breed: 'Gir Cow',
  confidence: 93.0,
  origin: 'Gujarat, India',
  characteristics: 'Large pendulous ears, prominent hump, reddish-brown coat',
  milkYield: '2,000 – 2,500 kg / lactation',
  breakdown: [
    { breed: 'Gir', pct: 93.0 },
    { breed: 'Sahiwal', pct: 4.5 },
    { breed: 'Red Sindhi', pct: 2.5 },
  ],
  traits: ['Heat Tolerant', 'High Milk Yield', 'Tick Resistant', 'Draft Purpose'],
}

function ConfidenceBar({ label, pct, main }) {
  return (
    <div className="confidence-item">
      <div className="confidence-item-header">
        <span className={`confidence-label ${main ? 'confidence-label--main' : ''}`}>{label}</span>
        <span className={`badge ${main ? 'badge-primary' : 'badge-info'}`}>{pct}%</span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${pct}%` }}></div>
      </div>
    </div>
  )
}

export default function ResultPage() {
  const { state } = useLocation()
  const previewUrl = state?.previewUrl

  return (
    <div className="result-page page-wrapper">
      <div className="container">
        {/* Breadcrumb */}
        <nav className="breadcrumb animate-fadeIn">
          <Link to="/">Home</Link>
          <span>›</span>
          <Link to="/upload">Classifier</Link>
          <span>›</span>
          <span>Results</span>
        </nav>

        <div className="result-header animate-fadeInUp">
          <div className="badge badge-success">✅ Analysis Complete</div>
          <h1>Results Analysis</h1>
        </div>

        <div className="result-layout animate-fadeInUp delay-1">
          {/* LEFT — Visualizations */}
          <div className="result-visuals">
            {/* Detection Output */}
            <div className="card-glass result-card">
              <h3>🔍 YOLO Detection Output</h3>
              <div className="detection-img-wrapper">
                {previewUrl
                  ? <img src={previewUrl} alt="Uploaded cattle" className="detection-img" />
                  : <div className="detection-placeholder">
                      <span>🐄</span>
                      <p>Cattle Detected — 98.2% confidence</p>
                    </div>
                }
                <div className="yolo-badge">
                  Cattle <strong>98.2%</strong>
                </div>
                <div className="yolo-box"></div>
              </div>
            </div>

            {/* Grad-CAM */}
            <div className="card-glass result-card">
              <h3>🌡️ Grad-CAM Explainability</h3>
              <div className="gradcam-wrapper">
                <div className="gradcam-overlay gradcam-placeholder">
                  <span className="gradcam-emoji">🌡️</span>
                  <p className="gradcam-text">Heatmap overlay applied</p>
                </div>
                <div className="gradcam-note">
                  <span>🎯</span>
                  <span>Model prioritized: <strong>Hump Shape</strong> and <strong>Horn Curvature</strong></span>
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT — Classification & Info */}
          <div className="result-info">
            {/* Top Prediction */}
            <div className="card-glass result-card">
              <h3>🏆 Top Prediction</h3>
              <div className="top-prediction">
                <span className="breed-name">{RESULT_DATA.breed}</span>
                <div className="confidence-score-row">
                  <span className="confidence-pct">{RESULT_DATA.confidence}%</span>
                  <span className="badge badge-primary">High Confidence</span>
                </div>
                <div className="progress-bar" style={{ marginTop: '0.75rem' }}>
                  <div className="progress-fill" style={{ width: `${RESULT_DATA.confidence}%` }}></div>
                </div>
              </div>
            </div>

            {/* Breakdown */}
            <div className="card-glass result-card">
              <h3>📊 Breed Breakdown</h3>
              <div className="confidence-list">
                {RESULT_DATA.breakdown.map((b, i) => (
                  <ConfidenceBar key={b.breed} label={`${i + 1}. ${b.breed}`} pct={b.pct} main={i === 0} />
                ))}
              </div>
            </div>

            {/* Quick Info */}
            <div className="card-glass result-card">
              <h3>📝 Quick Info</h3>
              <dl className="info-list">
                <div className="info-pair">
                  <dt>Origin</dt>
                  <dd>{RESULT_DATA.origin}</dd>
                </div>
                <div className="info-pair">
                  <dt>Characteristics</dt>
                  <dd>{RESULT_DATA.characteristics}</dd>
                </div>
                <div className="info-pair">
                  <dt>Milk Yield</dt>
                  <dd>{RESULT_DATA.milkYield}</dd>
                </div>
              </dl>
              <div className="info-traits">
                {RESULT_DATA.traits.map(t => (
                  <span key={t} className="badge badge-primary">{t}</span>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="result-actions">
              <button className="btn btn-primary" id="download-result-btn">📄 Download PDF</button>
              <Link to="/upload" className="btn btn-secondary" id="new-analysis-btn">🔄 New Analysis</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
