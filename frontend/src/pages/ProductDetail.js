import { useEffect, useState, useCallback } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { getProductDetail, createProductReview } from "../api/products";
import { getGroupBuySessions, joinGroupBuySession, createGroupBuySession } from "../api/orders";
import { addToCart } from "../store/slices/cartSlice";
import Header from "../components/Header";

export default function ProductDetail() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const user = useSelector(state => state.user?.user);

  const [product, setProduct] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isJoining, setIsJoining] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  
  // Notifications centrales
  const [toast, setToast] = useState({ show: false, message: "", type: "info" });
  
  const [newRating, setNewRating] = useState(5);
  const [newComment, setNewComment] = useState("");
  const [isSubmittingReview, setIsSubmittingReview] = useState(false);
  const [showReviewForm, setShowReviewForm] = useState(false);

  const showToast = (message, type = "info") => {
    setToast({ show: true, message, type });
    setTimeout(() => setToast({ show: false, message: "", type: "info" }), 3500);
  };

  const fetchProductData = useCallback(async () => {
    if (!slug) return;
    try {
      const productData = await getProductDetail(slug);
      setProduct(productData);
      try {
        const sessionData = await getGroupBuySessions({ product: productData?.id, status: 'open' });
        setSessions(sessionData?.results || sessionData || []);
      } catch (sErr) { console.warn(sErr); }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  }, [slug]);

  useEffect(() => {
    fetchProductData();
  }, [fetchProductData]);

  const handleJoinSession = async (sessionId) => {
    if (!user) {
      showToast("Veuillez vous connecter pour rejoindre ce groupe", "error");
      return;
    }
    setIsJoining(true);
    try {
      await joinGroupBuySession(sessionId, 1);
      showToast("Succès ! Vous avez été ajouté au groupe d'achat.", "success");
      fetchProductData();
    } catch (error) {
      showToast(error.response?.data?.error || "Erreur lors de la liaison.", "error");
    } finally { setIsJoining(false); }
  };

  const handleCreateSession = async () => {
    if (!user) {
      showToast("Veuillez vous connecter pour lancer un groupe.", "error");
      return;
    }
    setIsCreating(true);
    try {
      // Envoi des champs obligatoires pour le backend
      const newSession = await createGroupBuySession({ 
        product: product.id,
        target_quantity: product.bulk_min_quantity || 5, 
        unit_price_at_bulk: product.bulk_price || product.unit_price
      });
      
      // L'organisateur rejoint automatiquement son propre groupe
      if (newSession && newSession.id) {
        await joinGroupBuySession(newSession.id, 1);
      }

      showToast("Nouveau groupe créé avec succès ! Partagez le lien pour le remplir vite.", "success");
      fetchProductData();
    } catch (error) {
      let errorMsg = "Erreur lors de la création du groupe.";
      // Extraction des erreurs DRF (qui viennent sous forme de tableau)
      if (error.response?.data) {
        if (typeof error.response.data === 'object' && !error.response.data.error) {
           const firstKey = Object.keys(error.response.data)[0];
           errorMsg = `${firstKey}: ${error.response.data[firstKey][0] || 'Erreur'}`;
        } else {
           errorMsg = error.response.data.error || errorMsg;
        }
      }
      showToast(errorMsg, "error");
    } finally { setIsCreating(false); }
  };

  // FONCTIONNALITÉS DE PARTAGE
  const shareUrl = window.location.href;
  const shareText = `Découvrez ${product?.name} sur Faso-Commerce ! `;

  const shareOnWhatsApp = () => {
    window.open(`https://wa.me/?text=${encodeURIComponent(shareText + shareUrl)}`, '_blank');
  };

  if (isLoading) return <div className="app-layout"><Header /><div className="page-container"><h2>Chargement...</h2></div></div>;

  const ratingsCount = product?.reviews?.length || 0;
  const getStarPercent = (star) => {
    if (ratingsCount === 0) return 0;
    const count = product?.reviews?.filter(r => Math.round(r.rating) === star).length || 0;
    return (count / ratingsCount) * 100;
  };

  return (
    <div className="app-layout" style={{ backgroundColor: '#000', color: 'white' }}>
      <Header />

      {/* NOTIFICATIONS CENTRALES */}
      {toast.show && (
        <div className="center-notification-overlay">
          <div className={`center-toast ${toast.type}`}>
            <div className="toast-icon">{toast.type === 'success' ? '🚀' : '⚠️'}</div>
            <div className="toast-text">
               <strong>{toast.type === 'success' ? 'Félicitations' : 'Information'}</strong>
               <p>{toast.message}</p>
            </div>
            {toast.type === 'error' && !user && <button onClick={() => navigate("/login")} className="btn-toast-action">Se connecter</button>}
          </div>
        </div>
      )}

      <main className="page-container" style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
        
        <div className="detail-grid" style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: '50px' }}>
          <div className="gallery">
            <img src={product?.image || product?.thumbnail || "/placeholder.png"} alt={product?.name} style={{ width: '100%', borderRadius: '30px', border: '1px solid #1a1a1a', boxShadow: '0 30px 60px rgba(0,0,0,0.5)' }} />
            
            <div style={{ marginTop: '3rem' }}>
                <h2 style={{ fontSize: '1.8rem', marginBottom: '2rem' }}>Avis Clients ({ratingsCount})</h2>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>
                    {product?.reviews?.map(r => (
                    <div key={r.id} style={{ background: '#0a0a0a', padding: '20px', borderRadius: '15px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                            <span style={{ fontWeight: 'bold' }}>{r.user_name}</span>
                            <span style={{ color: '#ffc107' }}>{"★".repeat(r.rating)}</span>
                        </div>
                        <p style={{ color: '#888', fontSize: '0.9rem' }}>{r.comment}</p>
                    </div>
                    ))}
                    {ratingsCount === 0 && <p style={{ color: '#555' }}>Aucun avis pour le moment.</p>}
                </div>
            </div>
          </div>

          <div className="info">
            <div style={{ marginBottom: '2rem' }}>
              <span className="badge-category">{product?.category?.name || "EXCLUSIVITÉ"}</span>
              <h1 style={{ fontSize: '3.5rem', fontWeight: '900', margin: '10px 0' }}>{product?.name}</h1>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{ color: '#ffc107' }}>{"★".repeat(Math.round(product?.avg_rating || 5))}</div>
                  <span style={{ color: '#666' }}>({ratingsCount} avis)</span>
              </div>
            </div>

            <div className="price-card-premium">
                <div className="price-item">
                    <span className="price-label">Prix Individuel</span>
                    <span className="price-val">{product?.unit_price?.toLocaleString()} FCFA</span>
                </div>
                <div className="price-item bulk">
                    <span className="price-label">Prix Faso-Gros</span>
                    <span className="price-val-bulk">{product?.bulk_price?.toLocaleString()} FCFA</span>
                    <small>Dès {product?.bulk_min_quantity} {product?.unit}s</small>
                </div>
            </div>

            <div className="group-buy-dynamic-section">
                <h3>👥 Groupes d'achat en cours</h3>
                {sessions.length > 0 ? (
                    <div className="sessions-list">
                        {sessions.map(s => (
                            <div key={s.id} className="session-card-mini">
                                <div>
                                    <div className="organizer">Par {s.organizer_name}</div>
                                    <div className="progress">{s.current_quantity} / {s.target_quantity} {product?.unit}s</div>
                                </div>
                                <button onClick={() => handleJoinSession(s.id)} disabled={isJoining} className="btn-join-mini">Rejoindre</button>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="empty-groups">
                        <p>Aucun groupe pour ce produit. Soyez le premier à profiter du prix de gros !</p>
                    </div>
                )}
                <button onClick={handleCreateSession} disabled={isCreating} className="btn-create-group-full">LANCER UN NOUVEAU GROUPE</button>
            </div>

            <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '15px' }}>
               <button onClick={() => navigate("/checkout")} className="btn-order-now">COMMANDER SEUL (LIVRAISON EXPRESS)</button>
               <button onClick={() => dispatch(addToCart(product))} className="btn-add-cart">Ajouter au panier</button>
            </div>

            <div style={{ marginTop: '2.5rem', borderTop: '1px solid #1a1a1a', paddingTop: '20px' }}>
                <p style={{ fontSize: '0.8rem', color: '#666', marginBottom: '15px' }}>PARTAGER AVEC VOS PROCHES :</p>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button onClick={shareOnWhatsApp} className="btn-share wa">WhatsApp</button>
                    <button onClick={() => window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`, '_blank')} className="btn-share fb">Facebook</button>
                </div>
            </div>
          </div>
        </div>
      </main>

      <style>{`
        .badge-category { background: rgba(242, 101, 34, 0.1); color: var(--primary); padding: 5px 12px; border-radius: 5px; font-weight: bold; font-size: 0.8rem; text-transform: uppercase; }
        .price-card-premium { background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 20px; padding: 25px; margin-bottom: 25px; }
        .price-item { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .price-item.bulk { border-top: 1px solid #1a1a1a; padding-top: 15px; margin-top: 15px; }
        .price-label { color: #666; font-size: 0.9rem; }
        .price-val { font-size: 1.8rem; fontWeight: bold; }
        .price-val-bulk { font-size: 1.8rem; fontWeight: bold; color: #009e49; }
        .price-item small { display: block; font-size: 0.7rem; color: #444; text-align: right; }

        .group-buy-dynamic-section { background: #111; border: 1px dashed #333; border-radius: 20px; padding: 20px; margin-bottom: 30px; }
        .group-buy-dynamic-section h3 { font-size: 1rem; margin-bottom: 15px; color: #eee; }
        .session-card-mini { display: flex; justify-content: space-between; align-items: center; background: #000; padding: 12px 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid #1a1a1a; }
        .organizer { font-weight: bold; font-size: 0.85rem; }
        .progress { font-size: 0.75rem; color: #009e49; }
        .btn-join-mini { background: #009e49; border: none; color: white; padding: 6px 15px; border-radius: 20px; cursor: pointer; font-size: 0.75rem; font-weight: bold; }
        .btn-create-group-full { width: 100%; background: none; border: 1px solid var(--primary); color: var(--primary); padding: 12px; border-radius: 12px; cursor: pointer; font-weight: bold; margin-top: 10px; transition: 0.3s; }
        .btn-create-group-full:hover { background: var(--primary); color: white; }

        .btn-order-now { background: #009e49; color: white; border: none; padding: 20px; border-radius: 12px; font-weight: 800; cursor: pointer; font-size: 1rem; }
        .btn-add-cart { background: #000; border: 1px solid #333; color: white; padding: 15px; border-radius: 12px; font-weight: bold; cursor: pointer; }
        .btn-share { padding: 10px 20px; border-radius: 10px; border: none; color: white; font-weight: bold; cursor: pointer; }
        .btn-share.wa { background: #25D366; }
        .btn-share.fb { background: #1877F2; }

        .center-notification-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.6); z-index: 10000; backdrop-filter: blur(4px); }
        .center-toast { background: #151515; border: 1px solid #333; padding: 40px; border-radius: 20px; text-align: center; max-width: 400px; width: 90%; box-shadow: 0 20px 40px rgba(0,0,0,0.8); animation: popUp 0.4s ease-out; }
      `}</style>
    </div>
  );
}
