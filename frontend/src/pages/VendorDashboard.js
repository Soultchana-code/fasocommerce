import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getVendorWallet, getVendorProducts, getVendorOrders, requestWithdrawal, getWithdrawals, createProduct } from "../api/vendor";
import { getCategories } from "../api/products";
import Header from "../components/Header";

export default function VendorDashboard() {
  const [wallet, setWallet] = useState({ balance: 0, total_earned: 0 });
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [categories, setCategories] = useState([{ id: 1, name: "Alimentation" }, { id: 2, name: "Électronique" }]);
  const [withdrawals, setWithdrawals] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isWithdrawing, setIsWithdrawing] = useState(false);
  const [withdrawAmount, setWithdrawAmount] = useState("");
  
  const [toast, setToast] = useState({ show: false, message: "", type: "info" });
  const [showAddModal, setShowAddModal] = useState(false);
  const [newProduct, setNewProduct] = useState({
    name: "", description: "", unit_price: "", bulk_price: "", 
    bulk_min_quantity: "5", stock: "100", category_id: "1", unit: "unité",
    status: "active"
  });
  const [productImage, setProductImage] = useState(null);
  const [isCreatingProduct, setIsCreatingProduct] = useState(false);

  const showToast = (message, type = "info") => {
    setToast({ show: true, message, type });
    setTimeout(() => setToast({ show: false, message: "", type: "info" }), 4000);
  };

  const fetchData = async () => {
    try {
      const [walletData, productsData, ordersData, withdrawalsData, catsData] = await Promise.all([
        getVendorWallet().catch(() => ({ balance: 0, total_earned: 0 })),
        getVendorProducts().catch(() => []),
        getVendorOrders().catch(() => []),
        getWithdrawals().catch(() => []),
        getCategories().catch(() => [])
      ]);
      setWallet(walletData);
      setProducts(productsData.results || productsData || []);
      setOrders(ordersData.results || ordersData || []);
      setWithdrawals(withdrawalsData.results || withdrawalsData || []);
      
      const catsList = catsData.results || catsData || [];
      if (catsList.length > 0) {
        setCategories(catsList);
        setNewProduct(prev => ({ ...prev, category_id: catsList[0].id }));
      }
    } catch (error) {
      console.error("Erreur dashboard", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleWithdraw = async (e) => {
    e.preventDefault();
    if (parseFloat(withdrawAmount) > parseFloat(wallet.balance)) {
      showToast("Fonds insuffisants.", "error");
      return;
    }
    setIsWithdrawing(true);
    try {
      await requestWithdrawal(withdrawAmount, "74437107", "orange_money");
      showToast("Demande de retrait envoyée !", "success");
      setWithdrawAmount("");
      fetchData();
    } catch (err) {
      showToast("Échec du retrait.", "error");
    } finally {
      setIsWithdrawing(false);
    }
  };

  const handleAddProduct = async (e) => {
    e.preventDefault();
    setIsCreatingProduct(true);
    try {
      const formData = new FormData();
      Object.keys(newProduct).forEach(key => {
        if (newProduct[key] !== "") formData.append(key, newProduct[key]);
      });
      if (productImage) formData.append("image", productImage);
      
      await createProduct(formData);
      showToast("Produit mis en vente !", "success");
      setShowAddModal(false);
      fetchData();
    } catch (err) {
      showToast("Erreur lors de l'ajout.", "error");
    } finally {
      setIsCreatingProduct(false);
    }
  };

  const shareOnWhatsApp = (product) => {
    const url = `${window.location.origin}/products/${product.slug}`;
    const text = `🛒 Commandez chez moi : ${product.name}. Lien : `;
    window.open(`https://wa.me/?text=${encodeURIComponent(text + url)}`, '_blank');
  };

  if (isLoading) return <div className="app-layout"><Header /><div className="page-container"><h2>Chargement de votre bureau...</h2></div></div>;

  return (
    <div className="app-layout" style={{ backgroundColor: '#000', color: 'white' }}>
      <Header />

      {/* SYSTÈME DE TOAST */}
      {toast.show && (
        <div style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 10000, background: '#111', border: '1px solid #333', padding: '15px 25px', borderRadius: '12px' }}>
          {toast.message}
        </div>
      )}

      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
              <h3>Nouvel Article</h3>
              <button onClick={() => setShowAddModal(false)} style={{ background: 'none', border: 'none', color: 'white', fontSize: '2rem' }}>&times;</button>
            </div>
            <form onSubmit={handleAddProduct}>
               <div className="form-row">
                 <div className="form-group"><label>Nom</label><input type="text" required value={newProduct.name} onChange={e => setNewProduct({...newProduct, name: e.target.value})} /></div>
                 <div className="form-group">
                   <label>Catégorie</label>
                   <select value={newProduct.category_id} onChange={e => setNewProduct({...newProduct, category_id: e.target.value})}>
                     {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                   </select>
                 </div>
               </div>
               <div className="form-group" style={{ marginTop: '15px' }}><label>Description</label><textarea required value={newProduct.description} onChange={e => setNewProduct({...newProduct, description: e.target.value})} /></div>
               <div className="form-row" style={{ marginTop: '15px' }}>
                 <div className="form-group"><label>Prix Unitaire</label><input type="number" required value={newProduct.unit_price} onChange={e => setNewProduct({...newProduct, unit_price: e.target.value})} /></div>
                 <div className="form-group"><label>Unité</label><input type="text" value={newProduct.unit} onChange={e => setNewProduct({...newProduct, unit: e.target.value})} /></div>
               </div>
               <div className="form-row" style={{ marginTop: '15px' }}>
                 <div className="form-group"><label>Prix de Gros</label><input type="number" value={newProduct.bulk_price} onChange={e => setNewProduct({...newProduct, bulk_price: e.target.value})} /></div>
                 <div className="form-group"><label>Min Gros</label><input type="number" value={newProduct.bulk_min_quantity} onChange={e => setNewProduct({...newProduct, bulk_min_quantity: e.target.value})} /></div>
               </div>
               <div className="form-group" style={{ marginTop: '15px' }}><label>Image</label><input type="file" onChange={e => setProductImage(e.target.files[0])} /></div>
               <button className="btn-primary" type="submit" style={{ width: '100%', marginTop: '20px', padding: '15px' }}>PUBLIER L'ARTICLE</button>
            </form>
          </div>
        </div>
      )}

      <main className="page-container" style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '2rem' }}>Tableau de Bord Vendeur</h1>
        
        {/* STATS */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '3rem' }}>
          <div className="stat-card" style={{ borderLeft: '5px solid #009e49' }}>
             <small style={{ color: '#888' }}>SOLDE</small>
             <div style={{ fontSize: '1.8rem', fontWeight: 'bold' }}>{wallet.balance.toLocaleString()} F</div>
          </div>
          <div className="stat-card">
             <small style={{ color: '#888' }}>EARNINGS</small>
             <div style={{ fontSize: '1.8rem', fontWeight: 'bold' }}>{wallet.total_earned.toLocaleString()} F</div>
          </div>
          <div className="stat-card">
             <small style={{ color: '#888' }}>COMMANDES</small>
             <div style={{ fontSize: '1.8rem', fontWeight: 'bold' }}>{orders.length}</div>
          </div>
          <div className="stat-card">
             <small style={{ color: '#888' }}>ARTICLES</small>
             <div style={{ fontSize: '1.8rem', fontWeight: 'bold' }}>{products.length}</div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '30px', marginBottom: '3rem' }}>
           {/* MES PRODUITS */}
           <div className="checkout-section">
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
                 <h2>📦 Mes Articles</h2>
                 <button className="btn-primary" onClick={() => setShowAddModal(true)} style={{ padding: '8px 20px' }}>+ Ajouter</button>
              </div>
              <table className="vendor-table">
                <thead><tr><th>Nom</th><th>Prix</th><th>Statut</th><th>Action</th></tr></thead>
                <tbody>
                  {products.map(p => (
                    <tr key={p.id}>
                      <td>{p.name}</td>
                      <td>{p.unit_price} F</td>
                      <td><span className={`badge-status ${p.status === 'active' ? 'badge-status-success' : ''}`}>{p.status}</span></td>
                      <td><button onClick={() => shareOnWhatsApp(p)} style={{ background: '#25D366', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '5px', cursor: 'pointer' }}>WhatsApp</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
           </div>

           {/* RETRAIT */}
           <div className="checkout-section">
              <h2>💸 Retrait Direct</h2>
              <form onSubmit={handleWithdraw} style={{ marginTop: '1.5rem' }}>
                 <label style={{ fontSize: '0.8rem', color: '#666' }}>MONTANT À VERSER (F)</label>
                 <input type="number" className="auth-input" value={withdrawAmount} onChange={e => setWithdrawAmount(e.target.value)} required />
                 <button className="btn-primary" type="submit" disabled={isWithdrawing} style={{ width: '100%', marginTop: '15px' }}>DÉMANDER LE RETRAIT</button>
              </form>
           </div>
        </div>

        {/* NOUVELLE SECTION : HISTORIQUE DES VENTES */}
        <div className="checkout-section" style={{ width: '100%' }}>
           <h2>🧾 Historique de mes ventes (Ventes Récentes)</h2>
           <table className="vendor-table" style={{ marginTop: '20px' }}>
              <thead>
                <tr>
                  <th>Référence</th>
                  <th>Date</th>
                  <th>Total</th>
                  <th>Statut</th>
                  <th>Détails</th>
                </tr>
              </thead>
              <tbody>
                {orders.length === 0 ? (
                  <tr><td colSpan="5" style={{ textAlign: 'center', padding: '2rem', color: '#555' }}>Aucune vente enregistrée pour le moment.</td></tr>
                ) : (
                  orders.map(o => (
                    <tr key={o.id}>
                      <td><span style={{ fontFamily: 'monospace', color: 'var(--primary)' }}>{o.reference}</span></td>
                      <td>{new Date(o.created_at).toLocaleDateString()}</td>
                      <td>{o.total_amount.toLocaleString()} F</td>
                      <td><span className={`badge-status ${o.status === 'delivered' ? 'badge-status-success' : 'badge-status-pending'}`}>{o.status_display || o.status}</span></td>
                      <td><Link to={`/orders/${o.reference}`} style={{ color: 'white', textDecoration: 'underline', fontSize: '0.9rem' }}>Voir la facture</Link></td>
                    </tr>
                  ))
                )}
              </tbody>
           </table>
        </div>

      </main>

      <style>{`
        .stat-card { background: #111; padding: 25px; borderRadius: 15px; border: 1px solid #222; }
        .badge-status-success { background: rgba(0,158,73,0.1); color: #009e49; }
        .badge-status-pending { background: rgba(255,193,7,0.1); color: #ffc107; }
        .modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); display: flex; align-items: center; justify-content: center; z-index: 5000; }
        .modal-card { background: #151515; padding: 30px; border-radius: 20px; width: 100%; max-width: 500px; border: 1px solid #333; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .form-group label { display: block; font-size: 0.75rem; color: #666; margin-bottom: 5px; }
        .form-group input, .form-group textarea, .form-group select { width: 100%; background: #000; border: 1px solid #222; color: white; padding: 10px; border-radius: 8px; outline: none; }
      `}</style>
    </div>
  );
}
