import axios from 'axios';

import { setupErrorInterceptors } from '../utils/errorHandler';

// Create axios instance with base configuration
const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Setup global error handling
setupErrorInterceptors(api);

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

// Response interceptor - handle 401 errors specifically for auth redirect
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
    changePassword: (data) => api.put('/auth/password', data),
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
    getProjects: (params = {}) => {
        const queryParams = new URLSearchParams();
        if (params.status) queryParams.append('status_filter', params.status);
        if (params.q) queryParams.append('q', params.q);
        if (params.tags) queryParams.append('tags', params.tags);
        if (params.is_archived) queryParams.append('is_archived', params.is_archived);

        return api.get(`/projects/?${queryParams.toString()}`);
    },
    getProject: (id) => api.get(`/projects/${id}`),
    createProject: (data) => api.post('/projects/', data),
    updateProject: (id, data) => api.patch(`/projects/${id}`, data),
    archiveProject: (id, archive = true) => api.patch(`/projects/${id}/archive?archive=${archive}`),
    pinProject: (id, pin = true) => api.patch(`/projects/${id}/pin?pin=${pin}`),
    updateProjectTags: (id, tags) => api.patch(`/projects/${id}/tags`, tags),
    duplicateProject: (id) => api.post(`/projects/${id}/duplicate`),
    executeProject: (id, data) => api.post(`/projects/${id}/execute`, data),
    delete: (id) => api.delete(`/projects/${id}`),
};

// Files API
export const filesAPI = {
    upload: (formData, params) => api.post('/files/upload', formData, {
        params,
        headers: { 'Content-Type': 'multipart/form-data' }
    }),
    list: (params) => api.get('/files/', { params }),
    getMetadata: (id) => api.get(`/files/${id}`),
    download: (id) => api.get(`/files/${id}/download`, { responseType: 'blob' }),
    delete: (id) => api.delete(`/files/${id}`),
    // RAG methods
    index: (id) => api.post(`/files/${id}/index`),
    query: (data) => api.post('/files/query', data),
    chat: (data) => api.post('/files/chat', data),
};

// Workflow Templates API
export const workflowTemplatesAPI = {
    list: (params) => api.get('/workflow-templates/', { params }),
    get: (id) => api.get(`/workflow-templates/${id}`),
};

// Exports API
export const exportsAPI = {
    exportProject: (id, format) => api.get(`/exports/project/${id}?format=${format}`, { responseType: 'blob' }),
};

export default api;
