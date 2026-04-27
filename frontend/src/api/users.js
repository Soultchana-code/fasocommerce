import api from "./axios";

export const loginUser = async (credentials) => {
  // credentials: { username: "phone", password: "pwd" } - CustomTokenObtainPairView attend un username ou phone_number selon la config Djoser/SimpleJWT
  // Dans notre backend custom, c'est config pour `phone_number` et `password`
  const response = await api.post("/users/login/", credentials);
  return response.data;
};

export const registerUser = async (data) => {
  const response = await api.post("/users/register/", data);
  return response.data;
};

export const requestOtp = async (phone_number, purpose = "login") => {
  const response = await api.post("/users/otp/request/", { phone_number, purpose });
  return response.data;
};

export const verifyOtp = async (phone_number, otp_code, purpose = "login") => {
  const response = await api.post("/users/otp/verify/", { phone_number, otp_code, purpose });
  return response.data;
};
