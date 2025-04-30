/**
 * Catch-all API Route Handler
 * 
 * This file handles API routes that aren't explicitly defined.
 * It passes through the request to the actual backend API.
 */

import axios from 'axios';

export default async function handler(req, res) {
  try {
    // Get the API path that was requested
    const path = req.url.replace('/api/', '');
    
    // Determine the backend URL
    const API_BASE_URL = process.env.BACKEND_API_URL || 'http://localhost:8000';
    const backendUrl = `${API_BASE_URL}/api/${path}`;
    
    // Forward the request to the backend
    const response = await axios({
      method: req.method,
      url: backendUrl,
      data: req.body,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    // Return the response from the backend
    return res.status(response.status).json(response.data);
  } catch (error) {
    console.error('API proxy error:', error);
    
    // Return error details
    return res.status(error.response?.status || 500).json({
      error: 'Backend API error',
      message: error.response?.data?.detail || error.message || 'Error connecting to backend API',
      path: req.url
    });
  }
} 