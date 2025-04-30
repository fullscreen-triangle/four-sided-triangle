/**
 * Entity Extraction Module
 * 
 * Handles the extraction of domain-relevant entities from queries.
 * Uses the distributed backend API to identify and categorize entities.
 */

import { modelerBackendService } from '../../services/modeler-backend.service';

/**
 * Extract entities from a query.
 * 
 * @param {Object} options - Entity extraction options
 * @param {string} options.query - The query text to process
 * @param {string} [options.context="default"] - The modeling context
 * @returns {Promise<Array>} - A promise that resolves to an array of entities
 */
export const extractEntities = async ({ query, context = "default" }) => {
  if (!query) {
    throw new Error('Query is required for entity extraction');
  }

  try {
    // Use the modeler backend service
    const entities = await modelerBackendService.extractEntities(query, {
      modeling_context: context
    });
    
    return entities;
  } catch (error) {
    console.error('Error extracting entities:', error);
    
    // Return a minimal entity as fallback
    return [{
      id: `entity_${Date.now()}`,
      name: query.split(' ')[0] || "unknown",
      type: "unknown",
      description: "Entity extraction failed",
      attributes: [],
      confidence: 0.1
    }];
  }
};

/**
 * Get detailed information about an entity.
 * 
 * @param {string} entityId - The ID of the entity to get details for
 * @returns {Promise<Object>} - A promise that resolves to the entity details
 */
export const getEntityDetails = async (entityId) => {
  if (!entityId) {
    throw new Error('Entity ID is required');
  }

  try {
    // For now, we don't have a specific endpoint for this, so we'd need to
    // fetch all entities and filter, or implement a specific endpoint
    const allEntities = await modelerBackendService.extractEntities("Retrieve entity details");
    
    // Find the entity by ID
    const entity = allEntities.find(e => e.id === entityId);
    
    if (!entity) {
      throw new Error(`Entity with ID ${entityId} not found`);
    }
    
    return entity;
  } catch (error) {
    console.error('Error getting entity details:', error);
    throw new Error(`Failed to get entity details: ${error.message}`);
  }
}; 