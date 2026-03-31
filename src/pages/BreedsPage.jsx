import { useState } from 'react'
import './BreedsPage.css'

import breedsData from '../data/breeds.json'

const BREEDS = breedsData

const STATUS_COLOR = {
  'Stable': 'badge-success',
  'Near Threatened': 'badge-warning',
}

export default function BreedsPage() {
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState(BREEDS[0])

  const filtered = BREEDS.filter(b =>
    b.name.toLowerCase().includes(search.toLowerCase()) ||
    b.origin.toLowerCase().includes(search.toLowerCase()) ||
    b.traits.some(t => t.toLowerCase().includes(search.toLowerCase()))
  )

  return (
    <div className="breeds-page page-wrapper">
      <div className="container">
        {/* Header */}
        <div className="breeds-header animate-fadeInUp">
          <div className="badge badge-primary">📚 Breed Library</div>
          <h1>Indian Cattle Breeds</h1>
          <p>Explore the rich heritage of India's indigenous cattle breeds</p>
        </div>

        {/* Search */}
        <div className="breeds-search-bar animate-fadeInUp delay-1">
          <span className="search-icon">🔍</span>
          <input
            className="breeds-search-input"
            type="text"
            placeholder="Search breeds, traits, state…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            id="breed-search"
            aria-label="Search breeds"
          />
        </div>

        <div className="breeds-layout">
          {/* Grid */}
          <div className="breeds-grid animate-fadeInUp delay-2">
            {filtered.map(b => (
              <button
                key={b.id}
                className={`breed-card card-glass ${selected?.id === b.id ? 'breed-card--active' : ''}`}
                onClick={() => setSelected(b)}
                id={`breed-card-${b.id}`}
              >
                <div className="breed-card-media">
                  {b.image ? (
                    <img src={b.image} alt={b.name} className="breed-card-img" />
                  ) : (
                    <div className="breed-card-img-placeholder">🐄</div>
                  )}
                </div>
                <div className="breed-card-info">
                  <h4 className="breed-card-name">{b.name}</h4>
                  <p className="breed-card-origin">📍 {b.state}</p>
                  <div className="breed-card-traits">
                    {b.traits.slice(0, 2).map(t => (
                      <span key={t} className="badge badge-primary badge-sm">{t}</span>
                    ))}
                  </div>
                </div>
                <span className={`badge ${STATUS_COLOR[b.status]}`}>{b.status}</span>
              </button>
            ))}
            {filtered.length === 0 && (
              <p className="breeds-empty">No breeds found for "{search}"</p>
            )}
          </div>

          {/* Detail panel */}
          {selected && (
            <div className="breed-detail card-glass animate-scaleIn">
              <div className="breed-detail-header">
                <div className="breed-detail-media">
                   {selected.image ? (
                     <img src={selected.image} alt={selected.name} className="breed-detail-img" />
                   ) : (
                     <div className="breed-detail-img-placeholder">🐄</div>
                   )}
                </div>
                <div>
                  <h2 className="breed-detail-name">{selected.name}</h2>
                  <p className="breed-detail-origin">📍 {selected.state}</p>
                  <span className={`badge ${STATUS_COLOR[selected.status]}`}>{selected.status}</span>
                </div>
              </div>

              <p className="breed-detail-desc">{selected.desc}</p>

              <div className="breed-detail-section">
                <h4>Physical Blueprint</h4>
                <dl className="info-list">
                  {[
                    ['Weight', selected.weight],
                    ['Height', selected.height],
                    ['Coat', selected.coat],
                  ].map(([k, v]) => (
                    <div className="info-pair" key={k}>
                      <dt>{k}</dt><dd>{v}</dd>
                    </div>
                  ))}
                </dl>
              </div>

              <div className="breed-detail-section">
                <h4>🥛 Milk Performance</h4>
                <div className="milk-stat">
                  <span className="milk-value">{selected.milkYield}</span>
                  <span className="milk-label">per lactation</span>
                </div>
              </div>

              <div className="breed-detail-section">
                <h4>Key Traits</h4>
                <div className="info-traits">
                  {selected.traits.map(t => (
                    <span key={t} className="badge badge-primary">{t}</span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
