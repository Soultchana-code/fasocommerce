import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { logout } from "../store/slices/userSlice";

export default function Header() {
  const user = useSelector((state) => state.user.user);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  const handleLogout = () => {
    dispatch(logout());
    navigate("/login");
  };

  return (
    <header className="site-header">
      {/* LOGO */}
      <Link to="/products" className="header-brand">fasocommerce</Link>

      {/* NAVIGATION CENTRALE */}
      <nav className="header-nav">
        <Link to="/products" className="nav-link">Boutique</Link>
        {user?.role === 'vendor' ? (
          <Link to="/vendor/dashboard" className="nav-link" style={{ color: 'var(--primary)' }}>Dashboard Vendeur</Link>
        ) : (
          <Link to="/register?redirect=/vendor/dashboard" className="nav-link">Devenir Vendeur</Link>
        )}
      </nav>

      {/* ICÔNES DROITE (Alignées selon votre image) */}
      <div className="header-icons-group">
        
        {/* 1. ICÔNE COMMANDES (Presse-papier) */}
        <Link to="/orders" className="icon-btn-modern" title="Mes Commandes">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
            <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
          </svg>
        </Link>

        {/* 2. ICÔNE PANIER */}
        <Link to="/checkout" className="icon-btn-modern" title="Panier">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="9" cy="21" r="1"></circle>
            <circle cx="20" cy="21" r="1"></circle>
            <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
          </svg>
        </Link>

        {/* 3. AVATAR DE PROFIL AVEC MENU DÉROULANT */}
        <div className="profile-wrapper">
          {user ? (
            <div className="avatar-trigger" onClick={() => setShowProfileMenu(!showProfileMenu)}>
              {user.profile_image ? (
                <img src={user.profile_image} alt="Profil" className="avatar-img-circle" />
              ) : (
                <div className="avatar-initials">
                  {user.full_name ? user.full_name[0].toUpperCase() : user.email ? user.email[0].toUpperCase() : "U"}
                </div>
              )}
              
              {/* Menu Déroulant (Dropdown) */}
              {showProfileMenu && (
                <div className="profile-dropdown">
                  <div className="dropdown-header">
                     <strong>{user.full_name || "Utilisateur"}</strong>
                     <span>{user.email || user.phone_number}</span>
                  </div>
                  <hr />
                  <Link to="/orders" className="dropdown-item">Mes Achats</Link>
                  {user.role === 'vendor' && <Link to="/vendor/dashboard" className="dropdown-item">Mon Dashboard</Link>}
                  <button onClick={handleLogout} className="dropdown-item logout-btn">Déconnexion</button>
                </div>
              )}
            </div>
          ) : (
            <Link to="/login" className="login-btn-circle" title="Connexion">
              Connexion
            </Link>
          )}
        </div>
      </div>

      <style>{`
        .header-icons-group {
          display: flex;
          align-items: center;
          gap: 1.5rem;
        }
        .icon-btn-modern {
          color: white;
          opacity: 0.8;
          transition: 0.3s;
          display: flex;
          align-items: center;
        }
        .icon-btn-modern:hover {
          color: var(--primary);
          opacity: 1;
          transform: translateY(-2px);
        }
        .profile-wrapper {
          position: relative;
          cursor: pointer;
        }
        .avatar-img-circle {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          border: 2px solid var(--primary);
          object-fit: cover;
        }
        .avatar-initials {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: linear-gradient(135deg, var(--primary), #ffa07a);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 1rem;
          border: 2px solid rgba(255,255,255,0.1);
        }
        .avatar-initials:hover {
          border-color: var(--primary);
        }
        .profile-dropdown {
          position: absolute;
          top: 50px;
          right: 0;
          background: #1a1a1a;
          border: 1px solid #333;
          border-radius: 12px;
          width: 220px;
          box-shadow: 0 10px 25px rgba(0,0,0,0.5);
          z-index: 2000;
          padding: 10px 0;
          animation: slideDown 0.3s ease-out;
        }
        .dropdown-header {
          padding: 10px 20px;
          display: flex;
          flex-direction: column;
        }
        .dropdown-header span {
          font-size: 0.75rem;
          color: #888;
        }
        .dropdown-item {
          display: block;
          padding: 12px 20px;
          color: #eee;
          text-decoration: none;
          font-size: 0.9rem;
          transition: 0.2s;
        }
        .dropdown-item:hover {
          background: #222;
          color: var(--primary);
        }
        .logout-btn {
          width: 100%;
          text-align: left;
          background: none;
          border: none;
          border-top: 1px solid #333;
          color: #ff4444 !important;
          cursor: pointer;
        }
        @keyframes slideDown {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .login-btn-circle {
          padding: 8px 15px;
          background: var(--primary);
          color: white;
          border-radius: 20px;
          text-decoration: none;
          font-size: 0.8rem;
          font-weight: bold;
        }
      `}</style>
    </header>
  );
}
