import { NavLink } from 'react-router-dom'
import './Navbar.css'

const NAV_ITEMS = [
  { to: '/',          label: 'Home',      icon: '🏠' },
  { to: '/upload',    label: 'Classify',  icon: '📤' },
  { to: '/breeds',    label: 'Breeds',    icon: '📚' },
  { to: '/dashboard', label: 'Dashboard', icon: '📈' },
]

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="nav-inner">
        {/* Logo */}
        <NavLink to="/" className="nav-logo">
          <div className="nav-logo-icon">🐄</div>
          <div>
            <span className="nav-logo-title">CattleAI</span>
            <span className="nav-logo-sub">Breed Classifier</span>
          </div>
        </NavLink>

        {/* Links */}
        <ul className="nav-links">
          {NAV_ITEMS.map(({ to, label, icon }) => (
            <li key={to}>
              <NavLink
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `nav-link ${isActive ? 'nav-link--active' : ''}`
                }
              >
                <span className="nav-link-icon">{icon}</span>
                {label}
              </NavLink>
            </li>
          ))}
        </ul>

        {/* CTA */}
        <NavLink to="/upload" className="btn btn-primary nav-cta">
          Classify Now
        </NavLink>
      </div>
    </nav>
  )
}
