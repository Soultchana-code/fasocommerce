import { useEffect, useState } from "react";
import api from "../api/axios";

export default function ProductList() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    api.get("/products/").then((res) => setProducts(res.data));
  }, []);

  return (
    <div>
      <h2>Products</h2>
      <ul>
        {products.map((p) => (
          <li key={p.id}>{p.name} - {p.price} FCFA</li>
        ))}
      </ul>
    </div>
  );
}
