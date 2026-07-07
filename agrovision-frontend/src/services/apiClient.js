// src/services/apiClient.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 15000,
});

// Axios Request Interceptor to inject Auth Headers
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

// Custom Exponential Backoff with Jitter Retry Logic
export async function fetchWithRetry(requestFn, retries = 3, delay = 1000) {
  try {
    return await requestFn();
  } catch (error) {
    const isNetworkError = !error.response;
    const is5xxServer = error.response && error.response.status >= 500;
    
    if ((isNetworkError || is5xxServer) && retries > 0) {
      // Calculate delay with randomized jitter: delay * 2^attempt + random(0, 1000)
      const jitter = Math.random() * 1000;
      const nextDelay = (delay * 2) + jitter;
      
      console.warn(`[*] Connection failed. Retrying in ${nextDelay.toFixed(0)}ms... (${retries} attempts left)`);
      await new Promise(resolve => setTimeout(resolve, nextDelay));
      return fetchWithRetry(requestFn, retries - 1, nextDelay);
    }
    throw error;
  }
}
