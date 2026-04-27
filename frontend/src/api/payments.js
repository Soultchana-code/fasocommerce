import api from "./axios";

export const initiatePayment = async (orderId, provider, phoneNumber) => {
  const response = await api.post("/payments/initiate/", {
    order_id: orderId,
    provider: provider,
    phone_number: phoneNumber,
  });
  return response.data;
};

export const getPaymentStatus = async (transactionId) => {
  const response = await api.get(`/payments/${transactionId}/`);
  return response.data;
};
