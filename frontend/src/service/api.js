import axios from 'axios';
const API_BASE_URL = import.meta.env.VITE_API_URL;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,            // 🔥 importante para enviar la cookie
  headers: { 'Content-Type': 'application/json' },
});

export default apiClient;
