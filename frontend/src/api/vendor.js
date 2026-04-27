import api from "./axios";

// Portefeuille et Argent
export const getVendorWallet = async () => {
  const response = await api.get("/payments/wallet/");
  return response.data;
};

export const getWithdrawals = async () => {
  const response = await api.get("/payments/withdrawals/");
  return response.data;
};

export const requestWithdrawal = async (amount, phoneNumber, provider) => {
  const response = await api.post("/payments/withdrawals/", {
    amount,
    phone_number: phoneNumber,
    provider
  });
  return response.data;
};

// Gestion des produits par le vendeur
export const getVendorProducts = async () => {
  const response = await api.get("/products/"); // Utilise le filtre du backend pour VENDOR
  return response.data;
};

export const createProduct = async (productData) => {
  const response = await api.post("/products/", productData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

// Historique des ventes
export const getVendorOrders = async () => {
  const response = await api.get("/orders/");
  return response.data;
};
