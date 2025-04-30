/**
 * Relationship Mapping Module
 * 
 * Handles the mapping of relationships between entities in the knowledge model.
 * Uses the distributed backend API to analyze and establish connections.
 */

import { modelerBackendService } from '../../services/modeler-backend.service';

/**
 * Map relationships between entities.
 * 
 * @param {Object} options - Relationship mapping options
 * @param {Array} options.entities - The entities to map relationships between
 * @param {string} options.query - The original query for context
 * @param {Object} [options.context={}] - Additional context information
 * @returns {Promise<Array>} - A promise that resolves to an array of relationships
 */
export const mapRelationships = async ({ entities, query, context = {} }) => {
  if (!entities || !Array.isArray(entities) || entities.length === 0) {
    throw new Error('Entities array is required for relationship mapping');
  }

  if (!query) {
    throw new Error('Original query is required for relationship mapping context');
  }

  try {
    // Use the modeler backend service
    const relationships = await modelerBackendService.mapRelationships(entities, query);
    
    return relationships;
  } catch (error) {
    console.error('Error mapping relationships:', error);
    
    // Return minimal relationships as fallback if we have at least 2 entities
    if (entities.length >= 2) {
      return [{
        id: `relationship_${Date.now()}`,
        source_entity_id: entities[0].id,
        target_entity_id: entities[1].id,
        type: "unknown",
        description: "Relationship mapping failed",
        strength: 0.5,
        direction: "bidirectional",
        confidence: 0.1
      }];
    }
    
    return [];
  }
};

/**
 * Get relationship details by ID.
 * 
 * @param {string} relationshipId - The ID of the relationship to retrieve
 * @returns {Promise<Object>} - A promise that resolves to the relationship details
 */
export const getRelationshipDetails = async (relationshipId) => {
  if (!relationshipId) {
    throw new Error('Relationship ID is required');
  }

  try {
    // For now, we don't have a specific endpoint for this
    // In a real implementation, we would add a specific endpoint or store relationships
    // in a local state management system
    throw new Error('Not implemented');
  } catch (error) {
    console.error('Error getting relationship details:', error);
    throw new Error(`Failed to get relationship details: ${error.message}`);
  }
};

/**
 * Find paths between two entities.
 * 
 * @param {Object} options - Path finding options
 * @param {string} options.sourceEntityId - The ID of the source entity
 * @param {string} options.targetEntityId - The ID of the target entity
 * @param {Array} options.relationships - All existing relationships
 * @param {number} [options.maxDepth=3] - Maximum path depth to search
 * @returns {Array} - An array of paths between the entities
 */
export const findEntityPaths = ({ sourceEntityId, targetEntityId, relationships, maxDepth = 3 }) => {
  if (!sourceEntityId || !targetEntityId || !relationships) {
    throw new Error('Source entity ID, target entity ID, and relationships are required');
  }

  // Build a graph representation from relationships
  const graph = {};
  relationships.forEach(rel => {
    if (!graph[rel.source_entity_id]) {
      graph[rel.source_entity_id] = [];
    }
    
    // Add forward direction
    graph[rel.source_entity_id].push({
      targetId: rel.target_entity_id,
      relationship: rel,
      direction: 'forward'
    });
    
    // Add reverse direction if bidirectional
    if (rel.direction === 'bidirectional') {
      if (!graph[rel.target_entity_id]) {
        graph[rel.target_entity_id] = [];
      }
      
      graph[rel.target_entity_id].push({
        targetId: rel.source_entity_id,
        relationship: rel,
        direction: 'reverse'
      });
    }
  });

  // Use breadth-first search to find paths
  const queue = [{
    node: sourceEntityId,
    path: [],
    visited: new Set([sourceEntityId])
  }];
  
  const paths = [];
  
  while (queue.length > 0) {
    const { node, path, visited } = queue.shift();
    
    // Skip if we've reached max depth
    if (path.length >= maxDepth) {
      continue;
    }
    
    // Get neighbors
    const neighbors = graph[node] || [];
    
    for (const { targetId, relationship, direction } of neighbors) {
      // Skip if already visited
      if (visited.has(targetId)) {
        continue;
      }
      
      // Create a new path
      const newPath = [...path, { relationship, direction }];
      
      // Check if we've reached the target
      if (targetId === targetEntityId) {
        paths.push(newPath);
        continue;
      }
      
      // Add to queue
      const newVisited = new Set(visited);
      newVisited.add(targetId);
      
      queue.push({
        node: targetId,
        path: newPath,
        visited: newVisited
      });
    }
  }
  
  return paths;
}; 