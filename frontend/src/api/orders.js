import api from "./axios";

export const getOrders = async () => {
  const response = await api.get("/orders/");
  return response.data;
};

export const createOrder = async (orderData) => {
  const response = await api.post("/orders/", orderData);
  return response.data;
};

// --- Group Buy Endpoints ---
export const getGroupBuySessions = async (params = {}) => {
  const response = await api.get("/orders/group-buy/", { params });
  return response.data;
};

export const joinGroupBuySession = async (sessionId, quantity) => {
  const response = await api.post(`/orders/group-buy/${sessionId}/join/`, { quantity });
  return response.data;
};

export const createGroupBuySession = async (sessionData) => {
  const response = await api.post("/orders/group-buy/", sessionData);
  return response.data;
};
