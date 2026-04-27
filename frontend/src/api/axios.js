import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api/v1", // URL de ton backend Django
  headers: {
    "Content-Type": "application/json",
  },
});

// Intercepteur pour injecter le token JWT automatiquement
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;
