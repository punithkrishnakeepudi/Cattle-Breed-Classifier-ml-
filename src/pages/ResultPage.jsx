import { useLocation, Link } from 'react-router-dom'
import './ResultPage.css'

import BREEDS_DB from '../data/breeds.json'

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

const getBreedInfo = (name) => {
  if (!name) return null;
  // Normalize to lowercase for ID match or try name match
  const idValue = name.toLowerCase().replace(/ /g, '_');
  return BREEDS_DB.find(b => b.id === idValue || b.name.toLowerCase() === name.toLowerCase()) 
         || BREEDS_DB[0]; // fallback
}

const BASE_URL = 'http://localhost:5000'

export default function ResultPage() {
  const { state } = useLocation()
  const result = state?.result
  const breedDetail = getBreedInfo(result?.breed)

  if (!result) {
    return (
      <div className="result-page page-wrapper">
        <div className="container center">
          <h2>No results found. Please upload an image first.</h2>
          <Link to="/upload" className="btn btn-primary">Go to Upload</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="result-page page-wrapper">
      <div className="container">
        <nav className="breadcrumb animate-fadeIn">
          <Link to="/">Home</Link>
          <span>›</span>
          <Link to="/upload">Classifier</Link>
          <span>›</span>
          <span>Results</span>
        </nav>

        <div className="result-header animate-fadeInUp">
          <div className="badge badge-success">✅ Analysis Complete</div>
          <h1>{result.breed} — Prediction Analysis</h1>
        </div>

        <div className="result-layout animate-fadeInUp delay-1">
          {/* LEFT Visuals */}
          <div className="result-visuals">
            <div className="card-glass result-card">
              <h3>🔍 YOLO Detection Output</h3>
              <div className="detection-img-wrapper">
                <img src={`${BASE_URL}${result.detected_image}`} alt="Detection" className="detection-img" />
                <div className="yolo-badge">
                  {result.animal_detected ? 'Cattle detected' : 'No detection (Full img used)'}
                </div>
              </div>
            </div>

            <div className="card-glass result-card">
              <h3>🌡️ Grad-CAM Explainability</h3>
              <div className="gradcam-wrapper">
                <img src={`${BASE_URL}${result.heatmap}`} alt="Explainability" className="detection-img" />
                <div className="gradcam-note">
                  <span>🎯</span>
                  <span>Heatmap shows the primary visual features influencing the prediction.</span>
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT Info */}
          <div className="result-info">
            <div className="card-glass result-card">
              <h3>🏆 Top Prediction</h3>
              <div className="top-prediction">
                <span className="breed-name">{result.breed}</span>
                <div className="confidence-score-row">
                  <span className="confidence-pct">{(result.confidence * 100).toFixed(1)}%</span>
                  <span className="badge badge-primary">Confidence</span>
                </div>
                <div className="progress-bar" style={{ marginTop: '0.75rem' }}>
                  <div className="progress-fill" style={{ width: `${result.confidence * 100}%` }}></div>
                </div>
              </div>
            </div>

            {/* Quick Info from DB */}
            {breedDetail && (
              <div className="card-glass result-card">
                <h3>📝 Breed Profile</h3>
                <dl className="info-list">
                  <div className="info-pair">
                    <dt>Origin</dt>
                    <dd>{breedDetail.origin}</dd>
                  </div>
                  <div className="info-pair">
                    <dt>Typical Milk Yield</dt>
                    <dd>{breedDetail.milkYield}</dd>
                  </div>
                  <div className="info-pair" style={{ display: 'block' }}>
                    <dt>Description</dt>
                    <dd style={{ marginTop: '0.5rem', lineHeight: '1.5' }}>{breedDetail.desc}</dd>
                  </div>
                </dl>
                <div className="info-traits" style={{ marginTop: '1rem' }}>
                  {breedDetail.traits.map(t => (
                    <span key={t} className="badge badge-primary">{t}</span>
                  ))}
                </div>
              </div>
            )}

            <div className="result-actions">
              <button className="btn btn-primary" id="download-result-btn" onClick={() => window.print()}>📄 Print Result</button>
              <Link to="/upload" className="btn btn-secondary" id="new-analysis-btn">🔄 New Analysis</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
