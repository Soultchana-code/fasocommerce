import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api", // URL de ton backend Django
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;
