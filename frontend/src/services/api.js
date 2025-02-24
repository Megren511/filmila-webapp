import axios from 'axios';
import config from '../config';

const api = axios.create({
  baseURL: config.apiUrl,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const login = (credentials) => api.post('/auth/login', credentials);
export const register = (userData) => api.post('/auth/register', userData);
export const uploadFilm = (filmData) => api.post('/films/upload', filmData);
export const getFilms = () => api.get('/films');
export const getFilm = (id) => api.get(`/films/${id}`);
export const purchaseFilm = (filmId, paymentMethodId) => 
  api.post(`/films/${filmId}/purchase`, { paymentMethodId });

export default api;
