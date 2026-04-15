import api from "./axios";

export const processPayment = async (paymentData) => {
  const response = await api.post("/payments/", paymentData);
  return response.data;
};
