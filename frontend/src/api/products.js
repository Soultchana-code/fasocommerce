import api from "./axios";

export const getProducts = async () => {
  const response = await api.get("/products/");
  return response.data;
};

export const getProductDetail = async (id) => {
  const response = await api.get(`/products/${id}/`);
  return response.data;
};
