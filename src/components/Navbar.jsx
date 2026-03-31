import { NavLink } from 'react-router-dom'
import './Navbar.css'

const NAV_ITEMS = [
  { to: '/',          label: 'Home'      },
  { to: '/upload',    label: 'Classify'  },
  { to: '/breeds',    label: 'Breeds'    },
  { to: '/dashboard', label: 'Dashboard' },
]

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="nav-inner">
        {/* Logo */}
        <NavLink to="/" className="nav-logo">
          <img src="/logo.png" alt="CattleAI Logo" className="nav-logo-img" />
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
