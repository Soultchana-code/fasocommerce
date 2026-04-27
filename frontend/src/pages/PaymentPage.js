import { useState, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { Link, useNavigate } from "react-router-dom";
import { createOrder } from "../api/orders";
import { initiatePayment } from "../api/payments";
import { clearCart } from "../store/slices/cartSlice";
import Header from "../components/Header";

export default function PaymentPage() {
  const { items, totalAmount } = useSelector((state) => state.cart);
  const user = useSelector((state) => state.user.user);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    delivery_city: "Ouagadougou",
    delivery_district: "",
    delivery_landmark: "",
    delivery_phone: user?.phone_number || "",
    delivery_notes: "",
    latitude: null,
    longitude: null
  });

  const [paymentMethod, setPaymentMethod] = useState("orange_money");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [shippingFee, setShippingFee] = useState(0);
  const [distance, setDistance] = useState(0);
  
  const [toast, setToast] = useState({ show: false, message: "", type: "info" });
  const showToast = (message, type = "info") => {
    setToast({ show: true, message, type });
    if (type !== 'success') {
      setTimeout(() => setToast({ show: false, message: "", type: "info" }), 3500);
    }
  };

  // Calcul des frais de livraison (750 F par tranche de 10 Km)
  const calculateShipping = (lat, lon) => {
    // Coordonnées fictives d'un centre de distribution central à Ouaga (ex: Place de la Nation)
    const storeLat = 12.3714;
    const storeLon = -1.5197;
    
    // Calcul simple de distance (vols d'oiseaux)
    const R = 6371; // Rayon de la Terre en km
    const dLat = (lat - storeLat) * Math.PI / 180;
    const dLon = (lon - storeLon) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(storeLat * Math.PI / 180) * Math.cos(lat * Math.PI / 180) * 
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    const dist = R * c;

    setDistance(dist.toFixed(1));
    const fees = Math.max(750, Math.ceil(dist / 10) * 750);
    setShippingFee(fees);
  };

  const getGeoLocation = () => {
    if (!navigator.geolocation) return showToast("Géolocalisation non supportée", "error");
    
    navigator.geolocation.getCurrentPosition((pos) => {
      setFormData(prev => ({ ...prev, latitude: pos.coords.latitude, longitude: pos.coords.longitude }));
      calculateShipping(pos.coords.latitude, pos.coords.longitude);
      showToast("Position récupérée ! Frais de livraison calculés.", "info");
    }, () => {
      showToast("Impossible d'accéder à votre position", "error");
    });
  };

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (items.length === 0) return showToast("Votre panier est vide.", "error");
    
    setIsSubmitting(true);
    try {
      const orderRes = await createOrder({
        ...formData,
        order_type: "individual",
        total_amount: totalAmount + shippingFee,
        items: items.map(item => ({ product: item.id, quantity: item.quantity }))
      });
      
      const ref = orderRes.reference || orderRes.id;
      
      // Si paiement à la livraison, pas besoin d'initier Orange/Moov
      if (paymentMethod === 'cod') {
        showToast(`Commande #${ref} validée ! Paiement à la livraison prévu.`, "success");
        setTimeout(() => { dispatch(clearCart()); navigate("/orders"); }, 4500);
        return;
      }

      try {
        await initiatePayment(orderRes.id, paymentMethod, formData.delivery_phone);
        showToast(`Commande #${ref} validée ! Confirmez sur votre téléphone.`, "success");
        setTimeout(() => { dispatch(clearCart()); navigate("/orders"); }, 4500);
      } catch (payError) {
        showToast(`Commande #${ref} créée, mais échec du paiement mobile.`, "error");
        setTimeout(() => { dispatch(clearCart()); navigate("/orders"); }, 4500);
      }
    } catch (error) {
      showToast("Erreur lors de la commande.", "error");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (items.length === 0) {
    return <div className="app-layout"><Header /><div className="page-container" style={{ textAlign: "center", paddingTop: "5rem" }}><h2>Panier vide</h2><Link to="/products" className="btn-primary">Retour</Link></div></div>;
  }

  return (
    <div className="app-layout">
      <Header />

      {toast.show && (
        <div className="center-notification-overlay">
          <div className={`center-toast ${toast.type}`}>
            <div className="toast-icon">{toast.type === 'success' ? '🚚' : '📍'}</div>
            <div className="toast-text">
               <strong>{toast.type === 'success' ? 'Félicitations' : 'Localisation'}</strong>
               <p>{toast.message}</p>
            </div>
          </div>
        </div>
      )}
      
      <main className="page-container">
        <h1 className="page-title">Finaliser ma commande</h1>
        
        <div className="checkout-grid">
          <form id="checkout-form" onSubmit={handleSubmit}>
            <div className="checkout-section">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <h2 style={{ margin: 0 }}>📍 Livraison (Burkina Faso)</h2>
                <button type="button" onClick={getGeoLocation} style={{ background: '#009e49', color: 'white', border: 'none', padding: '8px 15px', borderRadius: '8px', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 'bold' }}>
                   📍 Ma position réelle
                </button>
              </div>
              
              <div className="form-row">
                <div className="form-group">
                  <label>Ville</label>
                  <select name="delivery_city" value={formData.delivery_city} onChange={handleInputChange}>
                    <option value="Ouagadougou">Ouagadougou</option>
                    <option value="Bobo-Dioulasso">Bobo-Dioulasso</option>
                    <option value="Koudougou">Koudougou</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Quartier</label>
                  <input type="text" name="delivery_district" placeholder="ex: Patte d'Oie" required onChange={handleInputChange} />
                </div>
              </div>
              <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                <label>Repère géographique (Très important au Burkina !)</label>
                <input type="text" name="delivery_landmark" placeholder="ex: Face au goudron" required onChange={handleInputChange} />
              </div>
              <div className="form-group">
                <label>Téléphone pour le livreur</label>
                <input type="text" name="delivery_phone" value={formData.delivery_phone} required onChange={handleInputChange} />
              </div>
            </div>

            <div className="checkout-section">
              <h2>💳 Mode de Paiement</h2>
              <div className="payment-methods">
                <div className={`method-card ${paymentMethod === 'orange_money' ? 'active' : ''}`} onClick={() => setPaymentMethod('orange_money')}>
                  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Orange_logo.svg/1200px-Orange_logo.svg.png" alt="Orange" className="method-logo" />
                  <span>Orange Money</span>
                </div>
                <div className={`method-card ${paymentMethod === 'moov_money' ? 'active' : ''}`} onClick={() => setPaymentMethod('moov_money')}>
                  <img src="https://moov-africa.bf/wp-content/uploads/2021/01/Moov_Africa_Logo.png" alt="Moov" className="method-logo" style={{ background: 'white' }} />
                  <span>Moov Money</span>
                </div>
                {/* OPTION PAIEMENT À LA LIVRAISON */}
                <div className={`method-card ${paymentMethod === 'cod' ? 'active' : ''}`} onClick={() => setPaymentMethod('cod')}>
                  <div style={{ fontSize: '1.5rem', marginBottom: '5px' }}>💵</div>
                  <span>Payé à la livraison</span>
                </div>
              </div>
            </div>
          </form>

          <div className="order-summary">
            <div className="checkout-section shadow-order">
              <h2>📋 Résumé</h2>
              {items.map(item => (
                <div key={item.id} className="summary-item">
                  <span>{item.quantity}x {item.name}</span>
                  <span>{item.unit_price * item.quantity} FCFA</span>
                </div>
              ))}
              
              <div style={{ marginTop: '20px', padding: '15px', background: 'rgba(0,158,73,0.05)', borderRadius: '10px', border: '1px solid rgba(0,158,73,0.2)' }}>
                <div className="summary-item" style={{ color: '#009e49', fontWeight: 'bold' }}>
                  <span>Frais de livraison ({distance} km)</span>
                  <span>{shippingFee > 0 ? `${shippingFee} FCFA` : "Calculés au GPS"}</span>
                </div>
                <small style={{ fontSize: '0.7rem', color: '#666' }}>Tarif : 750 FCFA par tranche de 10 Km</small>
              </div>

              <div className="summary-total" style={{ marginTop: '20px', borderTop: '1px solid #222', paddingTop: '15px' }}>
                <div className="summary-item">
                  <span style={{ fontWeight: 'bold' }}>Total à payer</span>
                  <span style={{ color: 'var(--primary)', fontSize: '1.4rem', fontWeight: '900' }}>{totalAmount + shippingFee} FCFA</span>
                </div>
              </div>
              
              <button type="submit" form="checkout-form" className="btn-primary" style={{ width: '100%', marginTop: '2rem', padding: '1.2rem' }} disabled={isSubmitting}>
                {isSubmitting ? "Traitement..." : `Confirmer ${totalAmount + shippingFee} FCFA`}
              </button>
            </div>
          </div>
        </div>
      </main>

      <style>{`
        .center-notification-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.8); z-index: 10000; backdrop-filter: blur(5px); }
        .center-toast { background: #111; border: 1px solid #333; padding: 40px; border-radius: 20px; text-align: center; max-width: 400px; width: 90%; }
        .toast-icon { font-size: 3rem; margin-bottom: 20px; }
        .toast-text strong { display: block; color: white; margin-bottom: 10px; font-size: 1.2rem; }
        .toast-text p { color: #888; }
        .method-card { border: 1px solid #222; padding: 15px; border-radius: 12px; cursor: pointer; text-align: center; transition: 0.3s; background: #0a0a0a; }
        .method-card.active { border-color: var(--primary); background: rgba(242, 101, 34, 0.05); }
        .method-logo { height: 30px; object-fit: contain; margin-bottom: 5px; }
        .summary-item { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 0.95rem; }
      `}</style>
    </div>
  );
}
