import api from "./axios";

export const getOrders = async () => {
  const response = await api.get("/orders/");
  return response.data;
};

export const createOrder = async (orderData) => {
  const response = await api.post("/orders/", orderData);
  return response.data;
};
