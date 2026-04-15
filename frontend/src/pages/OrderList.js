import { useEffect, useState } from "react";
import api from "../api/axios";

export default function OrderList() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    api.get("/orders/").then((res) => setOrders(res.data));
  }, []);

  return (
    <div>
      <h2>Orders</h2>
      <ul>
        {orders.map((o) => (
          <li key={o.id}>Order #{o.id} - {o.status}</li>
        ))}
      </ul>
    </div>
  );
}
