/**
 * API Root Handler
 * 
 * This file handles requests to /api endpoint and forwards them to the backend API.
 */

import axios from 'axios';

export default async function handler(req, res) {
  try {
    const API_BASE_URL = process.env.BACKEND_API_URL || 'http://localhost:8000';
    
    // Forward the request to the backend
    const response = await axios({
      method: req.method,
      url: `${API_BASE_URL}/api`,
      data: req.body,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    // Return the response from the backend
    return res.status(response.status).json(response.data);
  } catch (error) {
    console.error('API request error:', error);
    
    // Return error details
    return res.status(error.response?.status || 500).json({
      error: 'Backend API error',
      message: error.response?.data?.detail || error.message || 'Error connecting to backend API'
    });
  }
} 