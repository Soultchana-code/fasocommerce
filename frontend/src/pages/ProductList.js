import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useSelector } from "react-redux";
import { getProducts } from "../api/products";
import { getGroupBuySessions, joinGroupBuySession, createGroupBuySession } from "../api/orders";
import Header from "../components/Header";

export default function ProductList() {
  const navigate = useNavigate();
  const user = useSelector(state => state.user?.user);
  
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  // Notifications centrales
  const [toast, setToast] = useState({ show: false, message: "", type: "info" });
  
  // Modal d'achat groupé
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [isModalLoading, setIsModalLoading] = useState(false);

  const showToast = (message, type = "info") => {
    setToast({ show: true, message, type });
    setTimeout(() => setToast({ show: false, message: "", type: "info" }), 3500);
  };

  const fetchProducts = async (search = "") => {
    setIsLoading(true);
    try {
      const data = await getProducts(search ? { search } : {});
      setProducts(data.results || data || []);
    } catch (error) {
      console.error("Erreur produits", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchProducts(searchTerm);
  };

  const openGroupBuyModal = async (product) => {
    setSelectedProduct(product);
    setIsModalLoading(true);
    try {
      const data = await getGroupBuySessions({ product: product.id, status: 'open' });
      setSessions(data.results || data || []);
    } catch (error) {
      console.error("Erreur sessions", error);
    } finally {
      setIsModalLoading(false);
    }
  };

  const handleJoinSession = async (sessionId) => {
    if (!user) {
      showToast("Veuillez vous connecter pour rejoindre ce groupe", "error");
      return;
    }
    try {
      await joinGroupBuySession(sessionId, 1);
      showToast("Félicitations ! Vous avez rejoint le groupe d'achat.", "success");
      setSelectedProduct(null);
    } catch (error) {
      showToast(error.response?.data?.error || "Erreur lors de la liaison au groupe.", "error");
    }
  };

  const handleCreateSession = async () => {
    if (!user) {
      showToast("Veuillez vous connecter pour lancer un groupe d'achat.", "error");
      return;
    }
    try {
      const newSession = await createGroupBuySession({ 
        product: selectedProduct.id,
        target_quantity: selectedProduct.bulk_min_quantity || 5, 
        unit_price_at_bulk: selectedProduct.bulk_price || selectedProduct.unit_price
      });
      
      if (newSession && newSession.id) {
        await joinGroupBuySession(newSession.id, 1);
      }

      showToast("Nouveau groupe lancé ! Les autres clients peuvent maintenant vous rejoindre.", "success");
      setSelectedProduct(null);
    } catch (error) {
      let errorMsg = "Action refusée. Vérifiez votre connexion.";
      if (error.response?.data) {
        if (typeof error.response.data === 'object' && !error.response.data.error) {
           const firstKey = Object.keys(error.response.data)[0];
           errorMsg = `${firstKey}: ${error.response.data[firstKey][0] || 'Erreur'}`;
        } else {
           errorMsg = error.response.data.error || errorMsg;
        }
      }
      showToast(errorMsg, "error");
    }
  };

  return (
    <div className="app-layout">
      <Header />

      {/* NOTIFICATIONS CENTRALES */}
      {toast.show && (
        <div className="center-notification-overlay">
          <div className={`center-toast ${toast.type}`}>
            <div className="toast-icon">{toast.type === 'success' ? '🚀' : '⚠️'}</div>
            <div className="toast-text">
               <strong>{toast.type === 'success' ? 'Opération Réussie' : 'Une erreur est survenue'}</strong>
               <p>{toast.message}</p>
            </div>
            {toast.type === 'error' && !user && (
              <button onClick={() => navigate("/login")} className="btn-toast-action">Se connecter</button>
            )}
          </div>
        </div>
      )}

      {/* modal achat groupé reste identique */}
      {selectedProduct && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: '420px', border: '1px solid #333' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
               <h3 style={{ margin: 0, fontSize: '1.2rem' }}>📦 Achats groupés : {selectedProduct.name}</h3>
               <button onClick={() => setSelectedProduct(null)} style={{ background: 'none', border: 'none', color: '#666', fontSize: '1.8rem', cursor: 'pointer' }}>&times;</button>
            </div>
            {isModalLoading ? (
              <div style={{ textAlign: 'center', padding: '2rem' }}>Recherche en cours...</div>
            ) : sessions.length > 0 ? (
              <div>
                <p style={{ fontSize: '0.85rem', color: '#aaa', marginBottom: '1.5rem' }}>Rejoignez un groupe existant !</p>
                {sessions.map(s => (
                  <div key={s.id} className="session-item-row">
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                      <span style={{ fontWeight: 'bold' }}>De {s.organizer_name || "Client"}</span>
                      <span style={{ fontSize: '0.8rem', color: 'var(--secondary)' }}>{s.current_quantity} / {s.target_quantity} {selectedProduct.unit}s</span>
                    </div>
                    <button onClick={() => handleJoinSession(s.id)} className="btn-primary" style={{ padding: '6px 15px', fontSize: '0.8rem' }}>Rejoindre</button>
                  </div>
                ))}
                <button onClick={handleCreateSession} className="btn-secondary" style={{ width: '100%', marginTop: '15px' }}>Lancer un autre groupe</button>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '1rem 0' }}>
                <p style={{ marginBottom: '1.5rem' }}>Aucun groupe ouvert.</p>
                <button onClick={handleCreateSession} className="btn-primary" style={{ width: '100%', padding: '15px' }}>Lancer le premier groupe !</button>
              </div>
            )}
          </div>
        </div>
      )}

      <main className="page-container">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem', flexWrap: 'wrap', gap: '20px' }}>
          <h1 className="page-title" style={{ margin: 0 }}>Catalogue des Produits</h1>
          
          {/* VERSION PRÉCÉDENTE RESTAURÉE À L'IDENTIQUE */}
          <form onSubmit={handleSearchSubmit} className="search-bar-container">
            <input 
              type="text" 
              placeholder="Rechercher un produit (Riz, Huile, Pâtes...)" 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            <button type="submit" className="search-button">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
            </button>
          </form>
        </div>
        
        {isLoading ? (
          <div style={{ textAlign: "center", padding: "5rem", color: "var(--text-muted)" }}>Chargement...</div>
        ) : products.length === 0 ? (
          <div style={{ textAlign: "center", padding: "5rem", color: "var(--text-muted)" }}>Aucun produit trouvé.</div>
        ) : (
          <div className="products-grid">
            {products.map((product) => (
              <div key={product.id} className="product-card">
                <div className="product-image-container">
                  {product.thumbnail ? <img src={product.thumbnail} alt={product.name} className="product-thumbnail" /> : <div className="no-image">No Image</div>}
                </div>
                <div className="product-details">
                  <div className="product-category">{product.category_name || "ALIMENTATION"}</div>
                  <div className="product-name">{product.name}</div>
                  <div className="product-vendor">Vendu par {product.vendor_name || "Faso-Commerce"}</div>
                  <div className="product-price-box">
                    <div className="price-row"><span>Prix unitaire</span><strong>{product.unit_price} FCFA</strong></div>
                    {product.bulk_price && <div className="price-row" style={{ color: 'var(--secondary)' }}><span>Achat Groupé</span><strong>{product.bulk_price} FCFA</strong></div>}
                  </div>
                </div>
                <div className="product-actions" style={{ padding: '1.5rem', display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: '10px' }}>
                  <Link to={`/products/${product.slug}`} className="btn-secondary" style={{ padding: '12px', fontSize: '0.85rem', textAlign: 'center', textDecoration: 'none' }}>Détails</Link>
                  <button onClick={() => openGroupBuyModal(product)} className="btn-primary" style={{ padding: '12px', fontSize: '0.85rem' }} disabled={!product.bulk_price}>Achat Groupé</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      <style>{`
        .center-notification-overlay {
          position: fixed; top: 0; left: 0; right: 0; bottom: 0;
          display: flex; align-items: center; justify-content: center;
          background: rgba(0,0,0,0.6); z-index: 10000; backdrop-filter: blur(4px);
        }
        .center-toast {
          background: #151515; border: 1px solid #333; padding: 40px; border-radius: 20px;
          text-align: center; max-width: 400px; width: 90%;
          box-shadow: 0 20px 40px rgba(0,0,0,0.8);
          animation: popUp 0.4s cubic-bezier(0.17, 0.89, 0.32, 1.28);
        }
        .toast-icon { font-size: 3rem; margin-bottom: 20px; }
        .toast-text strong { display: block; font-size: 1.2rem; margin-bottom: 10px; color: white; }
        .toast-text p { color: #888; font-size: 0.95rem; }
        .btn-toast-action { margin-top: 25px; background: var(--primary); color: white; border: none; padding: 12px 30px; border-radius: 30px; font-weight: bold; cursor: pointer; }
        
        @keyframes popUp { 0% { transform: scale(0.8); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }

        .search-bar-container {
          display: flex; align-items: center; background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 50px;
          padding: 5px 5px 5px 25px; width: 100%; max-width: 500px; transition: 0.3s;
        }
        .search-bar-container:focus-within { border-color: var(--primary); background: rgba(255, 255, 255, 0.08); box-shadow: 0 0 20px rgba(242, 101, 34, 0.1); }
        .search-input { background: none; border: none; color: white; padding: 10px 0; font-size: 1rem; width: 100%; outline: none; }
        .search-button { background: var(--primary); border: none; color: white; width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: 0.3s; }
        
        .session-item-row { display: flex; justify-content: space-between; align-items: center; background: #222; padding: 12px 15px; border-radius: 12px; margin-bottom: 10px; }
        .modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); display: flex; align-items: center; justify-content: center; z-index: 5000; }
        .modal-card { background: #1a1a1a; padding: 25px; border-radius: 20px; border: 1px solid #333; color: white; }
      `}</style>
    </div>
  );
}
