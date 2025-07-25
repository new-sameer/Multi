import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const authAPI = {
  login: (credentials) => api.post('/api/v1/auth/login', credentials),
  register: (userData) => api.post('/api/v1/auth/register', userData),
  getProfile: () => api.get('/api/v1/users/profile'),
  updateProfile: (data) => api.put('/api/v1/users/profile', data),
  setSuccessGoals: (goals) => api.post('/api/v1/users/success-goals', goals),
};

export const contentAPI = {
  create: (contentData) => api.post('/api/v1/content/create', contentData),
  list: (params = {}) => api.get('/api/v1/content/list', { params }),
  getById: (id) => api.get(`/api/v1/content/${id}`),
  update: (id, data) => api.put(`/api/v1/content/${id}`, data),
  delete: (id) => api.delete(`/api/v1/content/${id}`),
};

export const dashboardAPI = {
  getStats: () => api.get('/api/v1/dashboard/stats'),
  getRecentContent: () => api.get('/api/v1/dashboard/recent-content'),
  getSuccessMetrics: () => api.get('/api/v1/dashboard/success-metrics'),
};

export const healthAPI = {
  check: () => api.get('/api/health'),
};

export default api;