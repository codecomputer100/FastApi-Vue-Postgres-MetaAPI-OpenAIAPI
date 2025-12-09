// src/service/authService.js
import apiClient from './api';

export function loginWithFacebook() {
  window.location.href = `${apiClient.defaults.baseURL}/auth/login`;
}

export function logout() {
  localStorage.removeItem('user');
  window.location.href = '/auth/login';
}

export function saveUser(user) {
  localStorage.setItem('user', JSON.stringify(user));
}

export function getUser() {
  const stored = localStorage.getItem('user');
  return stored ? JSON.parse(stored) : null;
}
