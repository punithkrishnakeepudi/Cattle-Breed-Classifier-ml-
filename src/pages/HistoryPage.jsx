import { useState } from 'react'
import './HistoryPage.css'

const HISTORY_DATA = [
  { id: 1, breed: 'Gir Cow', confidence: 93.0, date: 'Mar 25, 2026', time: '14:32', status: 'Completed', emoji: '🐄' },
  { id: 2, breed: 'Sahiwal', confidence: 87.5, date: 'Mar 25, 2026', time: '11:15', status: 'Completed', emoji: '🐮' },
  { id: 3, breed: 'Ongole', confidence: 91.2, date: 'Mar 24, 2026', time: '16:48', status: 'Completed', emoji: '🐄' },
  { id: 4, breed: 'Red Sindhi', confidence: 79.3, date: 'Mar 24, 2026', time: '09:20', status: 'Completed', emoji: '🐮' },
  { id: 5, breed: 'Tharparkar', confidence: 94.5, date: 'Mar 23, 2026', time: '17:02', status: 'Completed', emoji: '🐄' },
  { id: 6, breed: 'Kankrej', confidence: 88.8, date: 'Mar 23, 2026', time: '10:30', status: 'Completed', emoji: '🐮' },
  { id: 7, breed: 'Gir Cow', confidence: 95.1, date: 'Mar 22, 2026', time: '15:45', status: 'Completed', emoji: '🐄' },
  { id: 8, breed: 'Sahiwal', confidence: 82.0, date: 'Mar 22, 2026', time: '08:55', status: 'Completed', emoji: '🐮' },
  { id: 9, breed: 'Processing…', confidence: null, date: 'Mar 26, 2026', time: '03:01', status: 'Processing', emoji: '⏳' },
  { id: 10, breed: 'Ongole', confidence: 92.7, date: 'Mar 21, 2026', time: '13:10', status: 'Completed', emoji: '🐄' },
]

const STATS_SUMMARY = [
  { label: 'Total Analyses', value: '128', icon: '🔬' },
  { label: 'This Week', value: '23', icon: '📅' },
  { label: 'Avg. Confidence', value: '91.4%', icon: '🎯' },
]

const ITEMS_PER_PAGE = 7

export default function HistoryPage() {
  const [search, setSearch] = useState('')
  const [sortBy, setSortBy] = useState('date')
  const [page, setPage] = useState(1)

  const filtered = HISTORY_DATA
    .filter(
      h => h.breed.toLowerCase().includes(search.toLowerCase()) ||
           h.status.toLowerCase().includes(search.toLowerCase())
    )
    .sort((a, b) => {
      if (sortBy === 'confidence') return (b.confidence || 0) - (a.confidence || 0)
      return b.id - a.id
    })

  const totalPages = Math.ceil(filtered.length / ITEMS_PER_PAGE)
  const paginated = filtered.slice((page - 1) * ITEMS_PER_PAGE, page * ITEMS_PER_PAGE)

  const handleExport = () => {
    const header = 'ID,Breed,Confidence,Date,Time,Status\n'
    const rows = HISTORY_DATA.map(r =>
      `${r.id},"${r.breed}",${r.confidence ?? ''},${r.date},${r.time},${r.status}`
    ).join('\n')
    const blob = new Blob([header + rows], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'cattle_predictions.csv'; a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="history-page page-wrapper">
      <div className="container">
        <div className="history-header animate-fadeInUp">
          <div className="badge badge-primary">📜 Prediction Log</div>
          <h1>Prediction History</h1>
          <p>All your previous cattle breed classifications</p>
        </div>

        {/* Summary Stats */}
        <div className="history-stats animate-fadeInUp delay-1">
          {STATS_SUMMARY.map(({ label, value, icon }) => (
            <div className="card-glass history-stat" key={label}>
              <span className="history-stat-icon">{icon}</span>
              <span className="history-stat-value">{value}</span>
              <span className="history-stat-label">{label}</span>
            </div>
          ))}
        </div>

        {/* Controls */}
        <div className="history-controls animate-fadeInUp delay-2">
          <div className="history-search-bar">
            <span>🔍</span>
            <input
              type="text"
              placeholder="Search by breed or status…"
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(1) }}
              id="history-search"
              aria-label="Search history"
            />
          </div>

          <select
            className="history-sort"
            value={sortBy}
            onChange={e => setSortBy(e.target.value)}
            id="history-sort"
            aria-label="Sort by"
          >
            <option value="date">Sort: Date</option>
            <option value="confidence">Sort: Confidence</option>
          </select>

          <button className="btn btn-secondary history-export-btn" onClick={handleExport} id="export-csv-btn">
            ⬇️ Export CSV
          </button>
        </div>

        {/* Table */}
        <div className="card-glass history-table-wrapper animate-fadeInUp delay-3">
          <table className="history-table">
            <thead>
              <tr>
                <th>Thumbnail</th>
                <th>Breed</th>
                <th>Confidence</th>
                <th>Date & Time</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {paginated.map(row => (
                <tr key={row.id} className="history-row" id={`history-row-${row.id}`}>
                  <td>
                    <div className="history-thumb">{row.emoji}</div>
                  </td>
                  <td>
                    <span className="history-breed">{row.breed}</span>
                  </td>
                  <td>
                    {row.confidence != null
                      ? <span className="badge badge-primary">{row.confidence}%</span>
                      : <span className="badge badge-info">—</span>
                    }
                  </td>
                  <td>
                    <span className="history-date">{row.date}</span>
                    <span className="history-time">{row.time}</span>
                  </td>
                  <td>
                    <span className={`badge ${row.status === 'Completed' ? 'badge-success' : 'badge-warning'}`}>
                      {row.status === 'Processing' ? '⏳ ' : '✅ '}{row.status}
                    </span>
                  </td>
                  <td>
                    <button className="btn btn-ghost history-view-btn" id={`view-btn-${row.id}`}>View →</button>
                  </td>
                </tr>
              ))}
              {paginated.length === 0 && (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '2rem', color: 'var(--on-surface-variant)' }}>
                    No records found for "{search}"
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="pagination animate-fadeIn">
            <button
              className="btn btn-ghost"
              disabled={page === 1}
              onClick={() => setPage(p => p - 1)}
              id="prev-page-btn"
            >
              ← Prev
            </button>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map(p => (
              <button
                key={p}
                className={`btn ${p === page ? 'btn-primary' : 'btn-ghost'} pagination-num`}
                onClick={() => setPage(p)}
                id={`page-btn-${p}`}
              >
                {p}
              </button>
            ))}
            <button
              className="btn btn-ghost"
              disabled={page === totalPages}
              onClick={() => setPage(p => p + 1)}
              id="next-page-btn"
            >
              Next →
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
