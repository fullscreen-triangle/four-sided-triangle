/**
 * Parameter Identification Module
 * 
 * Handles the identification of model parameters from query and entity relationships.
 * Uses the distributed backend API to identify and categorize parameters.
 */

import { modelerBackendService } from '../../services/modeler-backend.service';

/**
 * Identify parameters for the model.
 * 
 * @param {Object} options - Parameter identification options
 * @param {string} options.query - The query text to process
 * @param {Array} options.entities - The entities in the model
 * @param {Array} options.relationships - The relationships in the model
 * @param {Object} [options.context={}] - Additional context information
 * @returns {Promise<Array>} - A promise that resolves to an array of parameters
 */
export const identifyParameters = async ({ query, entities, relationships, context = {} }) => {
  if (!query) {
    throw new Error('Query is required for parameter identification');
  }

  if (!entities || !Array.isArray(entities) || entities.length === 0) {
    throw new Error('Entities array is required for parameter identification');
  }

  try {
    // Use the modeler backend service
    const parameters = await modelerBackendService.identifyParameters(
      query,
      entities,
      relationships || []
    );
    
    return parameters;
  } catch (error) {
    console.error('Error identifying parameters:', error);
    
    // Return minimal parameters as fallback
    if (entities.length > 0) {
      return [{
        id: `parameter_${Date.now()}`,
        name: `Parameter for ${entities[0].name}`,
        description: "Parameter identification failed",
        data_type: "numeric",
        related_entity_ids: [entities[0].id],
        confidence: 0.1
      }];
    }
    
    return [];
  }
};

/**
 * Get parameter details by ID.
 * 
 * @param {string} parameterId - The ID of the parameter to retrieve
 * @returns {Promise<Object>} - A promise that resolves to the parameter details
 */
export const getParameterDetails = async (parameterId) => {
  if (!parameterId) {
    throw new Error('Parameter ID is required');
  }

  try {
    // For now, we don't have a specific endpoint for this
    throw new Error('Not implemented');
  } catch (error) {
    console.error('Error getting parameter details:', error);
    throw new Error(`Failed to get parameter details: ${error.message}`);
  }
};

/**
 * Get parameters for a specific entity.
 * 
 * @param {string} entityId - The ID of the entity
 * @param {Array} parameters - All parameters in the model
 * @returns {Array} - Parameters related to the entity
 */
export const getParametersForEntity = (entityId, parameters) => {
  if (!entityId || !parameters) {
    return [];
  }
  
  return parameters.filter(param => 
    param.related_entity_ids && param.related_entity_ids.includes(entityId)
  );
};

/**
 * Format a parameter for display.
 * 
 * @param {Object} parameter - The parameter to format
 * @returns {string} - Formatted string representation
 */
export const formatParameter = (parameter) => {
  if (!parameter) return '';
  
  let formatted = `${parameter.name}`;
  
  if (parameter.data_type) {
    formatted += ` (${parameter.data_type})`;
  }
  
  if (parameter.unit) {
    formatted += ` [${parameter.unit}]`;
  }
  
  if (parameter.range && (parameter.range.min !== undefined || parameter.range.max !== undefined)) {
    const min = parameter.range.min !== undefined ? parameter.range.min : '-∞';
    const max = parameter.range.max !== undefined ? parameter.range.max : '∞';
    formatted += `: ${min} to ${max}`;
  } else if (parameter.default_value !== undefined) {
    formatted += `: ${parameter.default_value}`;
  }
  
  return formatted;
}; 