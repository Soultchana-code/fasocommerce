import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getOrders } from "../api/orders";

export default function OrderList() {
  const [orders, setOrders] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const data = await getOrders();
        // Gère la pagination { results: [...] }
        setOrders(data.results ? data.results : data);
      } catch (error) {
        console.error("Erreur chargement commandes", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchOrders();
  }, []);

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'pending': return 'badge-status-pending';
      case 'paid': return 'badge-status-paid';
      case 'delivered': return 'badge-status-success';
      case 'cancelled': return 'badge-status-error';
      default: return '';
    }
  };

  return (
    <div className="app-layout">
      <header className="site-header">
        <Link to="/products" className="header-brand">Faso-Commerce</Link>
        <div className="header-actions">
          <Link to="/products" className="btn-secondary" style={{ padding: '0.5rem 1rem' }}>Retour Boutique</Link>
        </div>
      </header>

      <main className="page-container">
        <h1 className="page-title">Mes Commandes</h1>

        {isLoading ? (
          <div style={{ textAlign: "center", padding: "3rem" }}>Chargement...</div>
        ) : orders.length === 0 ? (
          <div style={{ textAlign: "center", padding: "3rem", background: 'var(--bg-card)', borderRadius: '20px' }}>
            <p style={{ color: '#888' }}>Vous n'avez pas encore passé de commande.</p>
            <Link to="/products" className="btn-primary" style={{ marginTop: '1.5rem', display: 'inline-block' }}>Commencer mes achats</Link>
          </div>
        ) : (
          <div className="orders-container">
            {orders.map((order) => (
              <div key={order.id} className="order-card-premium">
                <div className="order-main-info">
                  <div className="order-ref-box">
                    <span className="order-label">Référence</span>
                    <span className="order-ref">{order.reference}</span>
                  </div>
                  <div className="order-date-box">
                    <span className="order-label">Date</span>
                    <span className="order-date">{new Date(order.created_at).toLocaleDateString()}</span>
                  </div>
                </div>

                <div className="order-details-summary">
                  <div className="order-items-preview">
                    {order.items?.length} article(s)
                  </div>
                  <div className="order-total-amount">
                    {order.total_amount} FCFA
                  </div>
                </div>

                <div className="order-footer">
                  <span className={`badge-status ${getStatusBadgeClass(order.status)}`}>
                    {order.status_display}
                  </span>
                  <Link to={`/orders/${order.reference}`} className="btn-secondary" style={{ fontSize: '0.8rem', padding: '5px 15px' }}>
                    Détails
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
