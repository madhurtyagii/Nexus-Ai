import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor - attach JWT token to all requests
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('nexus_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor - handle 401 errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Clear token and redirect to login
            localStorage.removeItem('nexus_token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    signup: (data) => api.post('/auth/signup', data),
    login: (data) => api.post('/auth/login', data),
    getMe: () => api.get('/auth/me'),
};

// Tasks API
export const tasksAPI = {
    create: (data) => api.post('/tasks/', data),
    list: (params) => api.get('/tasks/', { params }),
    get: (id) => api.get(`/tasks/${id}`),
    delete: (id) => api.delete(`/tasks/${id}`),
    getStatus: (id) => api.get(`/tasks/${id}/status`),
};

// Agents API
export const agentsAPI = {
    list: () => api.get('/agents/'),
    get: (id) => api.get(`/agents/${id}`),
    getByName: (name) => api.get(`/agents/name/${name}`),
};

// Projects API
export const projectsAPI = {
    create: (data) => api.post('/projects/', data),
    list: (params) => api.get('/projects/', { params }),
    get: (id) => api.get(`/projects/${id}`),
    update: (id, data) => api.put(`/projects/${id}`, data),
    delete: (id) => api.delete(`/projects/${id}`),
};

export default api;
