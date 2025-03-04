import axios from 'axios';
import config from '../config';

const api = axios.create({
  baseURL: config.apiUrl,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Authentication endpoints
export const login = (credentials) => api.post('/login', credentials);
export const register = (userData) => api.post('/register', userData);

// Film endpoints
export const uploadFilm = (filmData) => api.post('/films/upload', filmData);
export const getFilms = () => api.get('/films');
export const getFilm = (id) => api.get(`/films/${id}`);
export const purchaseFilm = (filmId, paymentMethodId) => 
  api.post(`/films/${filmId}/purchase`, { paymentMethodId });

export default api;
