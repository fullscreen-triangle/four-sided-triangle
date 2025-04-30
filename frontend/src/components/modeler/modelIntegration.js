/**
 * Model Integration Module
 * 
 * Handles the integration of all model components into a unified knowledge model.
 * Uses the distributed backend API to synthesize, validate, and export models.
 */

import { modelerBackendService } from '../../services/modeler-backend.service';

/**
 * Integrate model components into a complete model.
 * 
 * @param {Object} options - Model integration options
 * @param {string} options.query - The original query
 * @param {Array} options.entities - The extracted entities
 * @param {Array} options.relationships - The mapped relationships
 * @param {Array} options.parameters - The identified parameters
 * @param {Object} [options.context={}] - Additional context information
 * @returns {Promise<Object>} - A promise that resolves to the integrated model
 */
export const integrateModel = async ({ query, entities, relationships, parameters, context = {} }) => {
  if (!query) {
    throw new Error('Query is required for model integration');
  }

  if (!entities || !Array.isArray(entities) || entities.length === 0) {
    throw new Error('Entities are required for model integration');
  }

  try {
    // Use the modeler backend service
    const modelData = {
      query,
      entities,
      relationships: relationships || [],
      parameters: parameters || []
    };
    
    const integratedModel = await modelerBackendService.integrateModel(modelData);
    
    return integratedModel;
  } catch (error) {
    console.error('Error integrating model:', error);
    
    // Return a minimal model as fallback
    return {
      id: `model_${Date.now()}`,
      query,
      entities,
      relationships: relationships || [],
      parameters: parameters || [],
      metadata: {
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        version: "1.0.0",
        confidence_score: 0.5
      }
    };
  }
};

/**
 * Validate a model against domain knowledge and constraints.
 * 
 * @param {Object} model - The model to validate
 * @param {string} [validationLevel="detailed"] - Level of validation detail
 * @returns {Promise<Object>} - A promise that resolves to validation results
 */
export const validateModel = async (model, validationLevel = "detailed") => {
  if (!model) {
    throw new Error('Model is required for validation');
  }

  try {
    // Use the modeler backend service
    const validationResults = await modelerBackendService.validateModel(model);
    
    return validationResults;
  } catch (error) {
    console.error('Error validating model:', error);
    
    // Return minimal validation results as fallback
    return {
      valid: false,
      issues: ["Validation failed due to service error"],
      warnings: [`Error: ${error.message}`],
      suggestions: ["Try again later or contact support"],
      confidence_scores: {
        overall: 0.1,
        entities: 0.1,
        relationships: 0.1,
        parameters: 0.1
      }
    };
  }
};

/**
 * Process a complete model workflow from query to validated model.
 * 
 * @param {string} query - The user query
 * @param {Object} [options={}] - Processing options
 * @returns {Promise<Object>} - A promise that resolves to the processed model
 */
export const processModel = async (query, options = {}) => {
  if (!query) {
    throw new Error('Query is required for model processing');
  }

  try {
    // Use the modeler backend service to process the complete model
    const processedModel = await modelerBackendService.processModel(query, options);
    
    return processedModel;
  } catch (error) {
    console.error('Error processing model:', error);
    throw new Error(`Model processing failed: ${error.message}`);
  }
};

/**
 * Export a model for use in external systems.
 * 
 * @param {Object} model - The model to export
 * @param {string} [format="json"] - Export format (json, xml, etc.)
 * @returns {string} - The exported model in the specified format
 */
export const exportModel = (model, format = "json") => {
  if (!model) {
    throw new Error('Model is required for export');
  }
  
  switch (format.toLowerCase()) {
    case 'json':
      return JSON.stringify(model, null, 2);
    
    case 'simplified':
      // Create a simplified version with just core elements
      const simplified = {
        query: model.query,
        entities: model.entities.map(e => ({
          id: e.id,
          name: e.name,
          type: e.type
        })),
        relationships: model.relationships.map(r => ({
          source: r.source_entity_id,
          target: r.target_entity_id,
          type: r.type
        })),
        parameters: model.parameters.map(p => ({
          name: p.name,
          data_type: p.data_type,
          related_entities: p.related_entity_ids
        }))
      };
      return JSON.stringify(simplified, null, 2);
      
    default:
      throw new Error(`Unsupported export format: ${format}`);
  }
}; 