/**
 * Modeler Backend Service
 * 
 * Provides integration between the frontend modeler components and the distributed backend.
 * Handles API requests, data transformation, and response processing.
 */

import axios, { AxiosError } from 'axios';
import { ModelEntity, ModelRelationship, ModelParameter, ModelData, ModelValidationResults } from '../types/modeler.types';

class ModelerBackendService {
  private apiBaseUrl: string;
  private requestTimeout: number;

  constructor() {
    this.apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
    this.requestTimeout = 60000; // 60 seconds default timeout
  }

  /**
   * Extract entities from a query text using the distributed backend
   * 
   * @param query The user query text
   * @param context Additional context information
   * @returns A promise that resolves to an array of extracted entities
   */
  async extractEntities(query: string, context: Record<string, any> = {}): Promise<ModelEntity[]> {
    try {
      const response = await axios.post(
        `${this.apiBaseUrl}/modeler/entities`,
        {
          query,
          context,
          options: {
            detailed_attributes: true,
            confidence_threshold: 0.6
          }
        },
        {
          timeout: this.requestTimeout,
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      return response.data.entities;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('Error extracting entities:', error);
      throw new Error(`Entity extraction failed: ${errorMessage}`);
    }
  }

  /**
   * Map relationships between entities
   * 
   * @param entities Array of entities to map relationships between
   * @param query Original query for context
   * @returns A promise resolving to relationship mappings
   */
  async mapRelationships(entities: ModelEntity[], query: string): Promise<ModelRelationship[]> {
    try {
      const response = await axios.post(
        `${this.apiBaseUrl}/modeler/relationships`,
        {
          entities,
          query,
          options: {
            include_indirect: true,
            min_confidence: 0.7
          }
        },
        {
          timeout: this.requestTimeout
        }
      );

      return response.data.relationships;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('Error mapping relationships:', error);
      throw new Error(`Relationship mapping failed: ${errorMessage}`);
    }
  }

  /**
   * Identify parameters for the model
   * 
   * @param query User query
   * @param entities Extracted entities
   * @param relationships Mapped relationships
   * @returns A promise resolving to identified parameters
   */
  async identifyParameters(
    query: string,
    entities: ModelEntity[],
    relationships: ModelRelationship[]
  ): Promise<ModelParameter[]> {
    try {
      const response = await axios.post(
        `${this.apiBaseUrl}/modeler/parameters`,
        {
          query,
          entities,
          relationships,
          options: {
            include_derived: true,
            include_domain_specific: true
          }
        },
        {
          timeout: this.requestTimeout
        }
      );

      return response.data.parameters;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('Error identifying parameters:', error);
      throw new Error(`Parameter identification failed: ${errorMessage}`);
    }
  }

  /**
   * Integrate model components into a complete model
   * 
   * @param modelData Partial model data to integrate
   * @returns A promise resolving to the integrated model
   */
  async integrateModel(modelData: Partial<ModelData>): Promise<ModelData> {
    try {
      const response = await axios.post(
        `${this.apiBaseUrl}/modeler/integrate`,
        {
          model_data: modelData,
          options: {
            validate: true,
            enrich_with_domain_knowledge: true
          }
        },
        {
          timeout: this.requestTimeout * 2 // Double timeout for integration
        }
      );

      return response.data.integrated_model;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('Error integrating model:', error);
      throw new Error(`Model integration failed: ${errorMessage}`);
    }
  }

  /**
   * Validate a model against domain knowledge and constraints
   * 
   * @param model The model to validate
   * @returns A promise resolving to validation results
   */
  async validateModel(model: ModelData): Promise<ModelValidationResults> {
    try {
      const response = await axios.post(
        `${this.apiBaseUrl}/modeler/validate`,
        {
          model,
          validation_level: 'detailed'
        },
        {
          timeout: this.requestTimeout
        }
      );

      return response.data.validation_results;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('Error validating model:', error);
      throw new Error(`Model validation failed: ${errorMessage}`);
    }
  }

  /**
   * Process a complete model workflow from query to validated model
   * 
   * @param query User query
   * @param options Processing options
   * @returns A promise resolving to the complete processed model
   */
  async processModel(
    query: string,
    options: {
      context?: Record<string, any>;
      include_visualization?: boolean;
      validation_level?: 'basic' | 'detailed';
    } = {}
  ): Promise<ModelData> {
    try {
      const response = await axios.post(
        `${this.apiBaseUrl}/modeler/process`,
        {
          query,
          options: {
            context: options.context || {},
            include_visualization: options.include_visualization || false,
            validation_level: options.validation_level || 'detailed'
          }
        },
        {
          timeout: this.requestTimeout * 3 // Triple timeout for full processing
        }
      );

      return response.data.model;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('Error processing model:', error);
      throw new Error(`Model processing failed: ${errorMessage}`);
    }
  }
}

// Export singleton instance
export const modelerBackendService = new ModelerBackendService();
export default modelerBackendService; 