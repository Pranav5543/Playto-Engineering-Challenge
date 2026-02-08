import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/api/',
});

// For simplicity in this prototype, we'll store the token in localStorage
const TOKEN_KEY = 'playto_auth_token';

api.interceptors.request.use((config) => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
        config.headers.Authorization = `Token ${token}`;
    }
    return config;
});

export const setToken = (token) => {
    localStorage.setItem(TOKEN_KEY, token);
};

export const clearToken = () => {
    localStorage.removeItem(TOKEN_KEY);
};

export default api;
