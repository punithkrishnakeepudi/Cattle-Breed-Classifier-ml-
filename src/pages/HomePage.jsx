import { Link } from 'react-router-dom'
import './HomePage.css'

const FEATURES = [
  { icon: '🔍', title: 'YOLOv8 Detection', desc: 'Precise bounding-box detection of cattle in any image.' },
  { icon: '🧠', title: 'CNN Classification', desc: 'ResNet-50 backbone classifies 50+ Indian cattle breeds.' },
  { icon: '🌡️', title: 'Grad-CAM XAI', desc: 'Heatmaps show exactly where the model focused its attention.' },
  { icon: '📊', title: 'Confidence Scores', desc: 'Get ranked predictions with % probability for each breed.' },
  { icon: '📚', title: 'Breed Library', desc: 'Rich database of breed traits, origin & characteristics.' },
  { icon: '📈', title: 'Model Dashboard', desc: 'Live accuracy, F1-score, confusion matrix & training graphs.' },
]

const BREEDS_PREVIEW = ['Gir', 'Sahiwal', 'Ongole', 'Red Sindhi', 'Tharparkar', 'Kankrej', 'Hallikar', 'Amrit Mahal']

const STATS = [
  { value: '50+', label: 'Cattle Breeds' },
  { value: '94.2%', label: 'Accuracy' },
  { value: '12K+', label: 'Training Images' },
  { value: '<2s', label: 'Inference Time' },
]

export default function HomePage() {
  return (
    <div className="home page-wrapper">
      {/* ======= Hero ======= */}
      <section className="hero">
        <div className="hero-blobs">
          <div className="blob blob-1"></div>
          <div className="blob blob-2"></div>
        </div>

        <div className="container hero-content">
          <div className="hero-badge badge badge-primary animate-fadeInUp">
            🌿 AI-Powered Agriculture Intelligence
          </div>

          <h1 className="hero-title animate-fadeInUp delay-1">
            Identify Any<br />
            <span className="hero-title-accent">Indian Cattle Breed</span><br />
            Instantly
          </h1>

          <p className="hero-desc animate-fadeInUp delay-2">
            Upload a photo of any cattle and get accurate breed classification
            with YOLO detection, Grad-CAM explanations, and detailed breed insights
            powered by deep learning.
          </p>

          <div className="hero-actions animate-fadeInUp delay-3">
            <Link to="/upload" className="btn btn-primary hero-btn-primary" id="hero-classify-btn">
              🐄 Classify Cattle Now
            </Link>
            <Link to="/breeds" className="btn btn-secondary" id="hero-breeds-btn">
              Explore Breeds →
            </Link>
          </div>

          {/* Stats */}
          <div className="hero-stats animate-fadeInUp delay-4">
            {STATS.map(({ value, label }) => (
              <div className="hero-stat" key={label}>
                <span className="hero-stat-value">{value}</span>
                <span className="hero-stat-label">{label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ======= Breed Tags ======= */}
      <section className="breeds-bar">
        <div className="container">
          <p className="breeds-bar-label">Supported Breeds Include</p>
          <div className="breeds-bar-tags">
            {BREEDS_PREVIEW.map(b => (
              <span key={b} className="badge badge-primary">{b}</span>
            ))}
            <span className="badge badge-info">+42 more</span>
          </div>
        </div>
      </section>

      {/* ======= Features ======= */}
      <section className="section features-section">
        <div className="container">
          <div className="section-header">
            <h2>How It Works</h2>
            <p>A complete pipeline from raw image to breed intelligence</p>
          </div>
          <div className="grid-3 features-grid">
            {FEATURES.map(({ icon, title, desc }, i) => (
              <div className={`card-glass feature-card animate-fadeInUp delay-${i + 1}`} key={title}>
                <div className="feature-icon">{icon}</div>
                <h3 className="feature-title">{title}</h3>
                <p className="feature-desc">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ======= CTA Banner ======= */}
      <section className="cta-banner">
        <div className="container cta-banner-inner">
          <div className="cta-banner-blobs">
            <div className="blob blob-1" style={{ opacity: 0.2 }}></div>
          </div>
          <div className="cta-text">
            <h2>Ready to classify your cattle?</h2>
            <p>Upload an image and get instant AI-powered breed identification with explainable results.</p>
          </div>
          <Link to="/upload" className="btn btn-primary" id="cta-upload-btn">
            Start Classification →
          </Link>
        </div>
      </section>
    </div>
  )
}
