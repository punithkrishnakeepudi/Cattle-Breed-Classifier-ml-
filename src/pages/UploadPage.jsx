import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import './UploadPage.css'

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp']

export default function UploadPage() {
  const [image, setImage] = useState(null)
  const [preview, setPreview] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState('')
  const fileRef = useRef()
  const navigate = useNavigate()

  const handleFile = file => {
    if (!file) return
    if (!ACCEPTED_TYPES.includes(file.type)) {
      setError('Please upload a JPG, PNG, or WEBP image.')
      return
    }
    setError('')
    setImage(file)
    setPreview(URL.createObjectURL(file))
  }

  const onDrop = e => {
    e.preventDefault()
    setDragging(false)
    handleFile(e.dataTransfer.files[0])
  }

  const onDragOver = e => { e.preventDefault(); setDragging(true) }
  const onDragLeave = () => setDragging(false)

  const onInputChange = e => handleFile(e.target.files[0])

  const handlePredict = () => {
    if (!image) return
    setLoading(true)
    setProgress(0)
    const interval = setInterval(() => {
      setProgress(p => {
        if (p >= 100) { clearInterval(interval); return 100 }
        return p + Math.random() * 18
      })
    }, 200)
    setTimeout(() => {
      clearInterval(interval)
      setProgress(100)
      setTimeout(() => {
        setLoading(false)
        navigate('/result', { state: { previewUrl: preview } })
      }, 400)
    }, 2200)
  }

  return (
    <div className="upload-page page-wrapper">
      <div className="container upload-container">
        {/* Header */}
        <div className="upload-header animate-fadeInUp">
          <div className="badge badge-primary">📤 Image Upload</div>
          <h1 className="upload-title">Upload Cattle Image</h1>
          <p className="upload-subtitle">
            Drag &amp; drop or browse to upload a cattle photo for AI breed classification.
          </p>
        </div>

        <div className="upload-layout">
          {/* Drop Zone */}
          <div
            className={`upload-zone card-glass animate-scaleIn ${dragging ? 'upload-zone--dragging' : ''} ${preview ? 'upload-zone--has-preview' : ''}`}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onClick={() => !preview && fileRef.current.click()}
            id="drop-zone"
          >
            {preview ? (
              <div className="preview-wrapper">
                <img src={preview} alt="Uploaded cattle" className="preview-img" />
                <button
                  className="btn btn-ghost preview-remove"
                  onClick={e => { e.stopPropagation(); setPreview(null); setImage(null) }}
                  id="remove-image-btn"
                >
                  ✕ Remove
                </button>
              </div>
            ) : (
              <div className="upload-placeholder">
                <div className="upload-icon">
                  <span>{dragging ? '⬇️' : '📷'}</span>
                </div>
                <h3>{dragging ? 'Drop it here!' : 'Drop your image here'}</h3>
                <p>or <span className="upload-browse-link">browse files</span></p>
                <div className="upload-hints">
                  <span className="badge badge-info">JPG</span>
                  <span className="badge badge-info">PNG</span>
                  <span className="badge badge-info">WEBP</span>
                  <span className="badge badge-info">Max 10MB</span>
                </div>
              </div>
            )}
          </div>

          <input
            ref={fileRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            style={{ display: 'none' }}
            onChange={onInputChange}
            id="file-input"
          />

          {/* Action Panel */}
          <div className="upload-actions-panel animate-slideInRight">
            <div className="card-glass action-card">
              <h3>🔬 Analysis Pipeline</h3>
              <ul className="pipeline-steps">
                {[
                  { step: '01', label: 'YOLOv8 Object Detection', desc: 'Locates cattle in image' },
                  { step: '02', label: 'Region Cropping', desc: 'Isolates cattle region' },
                  { step: '03', label: 'CNN Classification', desc: 'ResNet-50 breed prediction' },
                  { step: '04', label: 'Grad-CAM Heatmap', desc: 'Explainable AI visualization' },
                ].map(s => (
                  <li className="pipeline-step" key={s.step}>
                    <span className="pipeline-num">{s.step}</span>
                    <div>
                      <span className="pipeline-label">{s.label}</span>
                      <span className="pipeline-desc">{s.desc}</span>
                    </div>
                  </li>
                ))}
              </ul>
            </div>

            {error && <div className="error-msg">{error}</div>}

            {/* Progress */}
            {loading && (
              <div className="upload-progress animate-fadeIn">
                <div className="upload-progress-header">
                  <div className="spinner"></div>
                  <span>Analyzing image…</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${Math.min(progress, 100)}%` }}></div>
                </div>
                <span className="upload-progress-pct">{Math.min(Math.round(progress), 100)}%</span>
              </div>
            )}

            <button
              className="btn btn-primary predict-btn"
              disabled={!image || loading}
              onClick={handlePredict}
              id="predict-btn"
            >
              {loading ? 'Analyzing…' : '🔍 Predict Breed'}
            </button>

            {!image && (
              <button
                className="btn btn-secondary"
                onClick={() => fileRef.current.click()}
                id="browse-btn"
              >
                📂 Browse Files
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
