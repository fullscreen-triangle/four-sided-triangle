/**
 * Model Processing Module
 * 
 * Handles the conversion of a query into a structured knowledge model
 * through interactions with the backend API.
 */

import axios from 'axios';

/**
 * Process a query and create a knowledge model.
 * 
 * @param {Object} options - Options for model processing
 * @param {string} options.query - The query text to model
 * @param {string} [options.intent="information"] - Query intent
 * @param {Object} [options.context={}] - Query context
 * @param {Object} [options.parameters={}] - Additional parameters
 * @returns {Promise<Object>} - A promise that resolves to the knowledge model
 */
export const processModel = async ({
  query,
  intent = "information",
  context = {},
  parameters = {}
}) => {
  if (!query) {
    throw new Error('Query is required for model processing');
  }

  try {
    const response = await axios.post('/api/modeler', {
      query,
      intent,
      context,
      parameters
    });

    if (!response.data || !response.data.knowledge_model) {
      throw new Error('Invalid response from modeler API');
    }

    return {
      ...response.data.knowledge_model,
      metadata: response.data.metadata || {}
    };
  } catch (error) {
    console.error('Error processing model:', error);
    throw new Error(
      error.response?.data?.detail || 
      error.message || 
      'Failed to process knowledge model'
    );
  }
};

/**
 * Get model processing status.
 * 
 * @param {string} modelId - The ID of the model being processed
 * @returns {Promise<Object>} - A promise that resolves to the model status
 */
export const getModelStatus = async (modelId) => {
  if (!modelId) {
    throw new Error('Model ID is required to check status');
  }

  try {
    const response = await axios.get(`/api/modeler/status/${modelId}`);
    return response.data;
  } catch (error) {
    console.error('Error checking model status:', error);
    throw new Error(
      error.response?.data?.detail || 
      error.message || 
      'Failed to check model status'
    );
  }
};

/**
 * Cancel a model processing job.
 * 
 * @param {string} modelId - The ID of the model to cancel
 * @returns {Promise<Object>} - A promise that resolves to the cancellation result
 */
export const cancelModelProcessing = async (modelId) => {
  if (!modelId) {
    throw new Error('Model ID is required to cancel processing');
  }

  try {
    const response = await axios.post(`/api/modeler/cancel/${modelId}`);
    return response.data;
  } catch (error) {
    console.error('Error canceling model processing:', error);
    throw new Error(
      error.response?.data?.detail || 
      error.message || 
      'Failed to cancel model processing'
    );
  }
}; 