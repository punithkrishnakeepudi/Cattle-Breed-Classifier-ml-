import { useState } from 'react'
import './BreedsPage.css'

const BREEDS = [
  {
    id: 'gir',
    name: 'Gir',
    origin: 'Gujarat',
    state: 'Gujarat, India',
    traits: ['High Milk Yield', 'Heat Tolerant', 'Tick Resistant'],
    status: 'Stable',
    milkYield: '2,000 – 2,500 kg/lactation',
    weight: '400 – 475 kg',
    height: '135 – 145 cm',
    coat: 'Reddish-brown with white patches',
    desc: 'The Gir is one of the principal zebu breeds originating in India. It is known worldwide for its sheer hardiness and adaptability. Its milk has A2 beta-casein protein which is considered healthier.',
    emoji: '🐄',
  },
  {
    id: 'sahiwal',
    name: 'Sahiwal',
    origin: 'Punjab',
    state: 'Punjab, India/Pakistan',
    traits: ['Very High Milk Yield', 'Calm Temperament', 'Disease Resistant'],
    status: 'Stable',
    milkYield: '1,800 – 2,200 kg/lactation',
    weight: '350 – 450 kg',
    height: '130 – 140 cm',
    coat: 'Reddish-dun to pale yellowish-brown',
    desc: 'Sahiwal is considered the best dairy breed in India and Pakistan. It is found in regions of Rajasthan and Punjab. Cows are known for their high milk yield, even under mediocre feeding conditions.',
    emoji: '🐮',
  },
  {
    id: 'ongole',
    name: 'Ongole',
    origin: 'Andhra Pradesh',
    state: 'Andhra Pradesh, India',
    traits: ['Draft Work', 'Drought Resistant', 'Large Build'],
    status: 'Stable',
    milkYield: '900 – 1,200 kg/lactation',
    weight: '550 – 700 kg',
    height: '155 – 165 cm',
    coat: 'White to grey with dark markings',
    desc: 'The Ongole is a dual-purpose breed from the Guntur and Prakasam districts. They are famous for their large frame and use in heavy draft work. Internationally significant as the foundation for Nellore cattle in Brazil.',
    emoji: '🐄',
  },
  {
    id: 'red-sindhi',
    name: 'Red Sindhi',
    origin: 'Sindh Region',
    state: 'India / Pakistan',
    traits: ['High Butterfat', 'Heat Tolerant', 'Tick Resistant'],
    status: 'Near Threatened',
    milkYield: '1,200 – 1,800 kg/lactation',
    weight: '300 – 380 kg',
    height: '120 – 130 cm',
    coat: 'Deep red to reddish-brown',
    desc: 'Red Sindhi is a prominent dairy breed known for richness of milk. It thrives in hot humid conditions and has been exported worldwide. The breed shows exceptional adaptability and disease resistance.',
    emoji: '🐮',
  },
  {
    id: 'tharparkar',
    name: 'Tharparkar',
    origin: 'Rajasthan',
    state: 'Rajasthan, India',
    traits: ['Drought Hardy', 'Moderate Milk', 'Long Horns'],
    status: 'Stable',
    milkYield: '1,400 – 1,700 kg/lactation',
    weight: '330 – 430 kg',
    height: '125 – 140 cm',
    coat: 'White to light grey',
    desc: 'Tharparkar cows are found in the Thar desert region and are well adapted to arid conditions. Known as the "White Sindhi," they are hardy animals that can survive on sparse vegetation and scarce water.',
    emoji: '🐄',
  },
  {
    id: 'kankrej',
    name: 'Kankrej',
    origin: 'Gujarat',
    state: 'Gujarat & Rajasthan, India',
    traits: ['Fast Gait', 'Dual Purpose', 'Strong Build'],
    status: 'Stable',
    milkYield: '1,600 – 2,000 kg/lactation',
    weight: '420 – 560 kg',
    height: '145 – 155 cm',
    coat: 'Silver-grey to iron-grey',
    desc: 'Kankrej is one of the heaviest zebu breeds known for their distinctive lyre-shaped horns and brisk pace. They are dual-purpose animals used for both draft and dairy. The breed is found in the Rann of Kutch region.',
    emoji: '🐮',
  },
]

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
                <div className="breed-card-emoji">{b.emoji}</div>
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
                <span className="breed-detail-emoji">{selected.emoji}</span>
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
