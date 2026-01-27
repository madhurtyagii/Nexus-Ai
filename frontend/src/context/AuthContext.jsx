/**
 * Nexus AI - Auth Context
 * Provides authentication state and methods to the app
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('nexus_token'));
    const [loading, setLoading] = useState(true);

    // Check if user is authenticated on mount
    useEffect(() => {
        const checkAuth = async () => {
            const savedToken = localStorage.getItem('nexus_token');

            if (savedToken) {
                try {
                    // Set the token in API headers
                    api.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`;

                    // Verify token by fetching user profile
                    const response = await api.get('/auth/me');
                    setUser(response.data);
                    setToken(savedToken);
                } catch (error) {
                    console.error('Auth check failed:', error);
                    // Token invalid, clear it
                    localStorage.removeItem('nexus_token');
                    delete api.defaults.headers.common['Authorization'];
                    setUser(null);
                    setToken(null);
                }
            }

            setLoading(false);
        };

        checkAuth();
    }, []);

    const login = async (email, password) => {
        try {
            const response = await api.post('/auth/login', {
                email,
                password
            });

            const { access_token } = response.data;

            // Save token
            localStorage.setItem('nexus_token', access_token);
            api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
            setToken(access_token);

            // Fetch user data
            const userResponse = await api.get('/auth/me');
            setUser(userResponse.data);

            return { success: true };
        } catch (error) {
            console.error('Login error:', error);
            return {
                success: false,
                error: error.response?.data?.detail || 'Login failed'
            };
        }
    };

    const signup = async (username, email, password) => {
        try {
            // Signup returns user data, not token
            await api.post('/auth/signup', {
                username,
                email,
                password
            });

            // After signup, login to get token
            return await login(email, password);
        } catch (error) {
            console.error('Signup error:', error);
            return {
                success: false,
                error: error.response?.data?.detail || 'Signup failed'
            };
        }
    };

    const logout = () => {
        localStorage.removeItem('nexus_token');
        delete api.defaults.headers.common['Authorization'];
        setToken(null);
        setUser(null);
    };

    const value = {
        user,
        token,
        loading,
        isAuthenticated: !!token,
        login,
        signup,
        logout
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}

export default AuthContext;
