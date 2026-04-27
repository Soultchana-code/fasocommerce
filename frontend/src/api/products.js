import api from "./axios";

export const getProducts = async (params) => {
  const response = await api.get("/products/", { params });
  return response.data;
};

export const getProductDetail = async (slug) => {
  const response = await api.get(`/products/${slug}/`);
  return response.data;
};

export const createProductReview = async (slug, reviewData) => {
  const response = await api.post(`/products/${slug}/reviews/`, reviewData);
  return response.data;
};

export const getCategories = async () => {
  const response = await api.get("/categories/");
  return response.data;
};
