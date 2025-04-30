/**
 * Types for the modeler module
 */

/**
 * Represents an entity extracted from a query
 */
export interface ModelEntity {
  id: string;
  name: string;
  type: string;
  description: string;
  attributes: string[];
  confidence: number;
}

/**
 * Represents a relationship between entities
 */
export interface ModelRelationship {
  id: string;
  source_entity_id: string;
  target_entity_id: string;
  type: string;
  description: string;
  strength: number;
  direction: 'one_way' | 'bidirectional' | 'none';
  confidence: number;
}

/**
 * Represents a parameter in the model
 */
export interface ModelParameter {
  id: string;
  name: string;
  description: string;
  data_type: string;
  unit?: string;
  range?: {
    min?: number;
    max?: number;
  };
  default_value?: any;
  related_entity_ids: string[];
  formula?: string;
  confidence: number;
}

/**
 * Complete model data structure
 */
export interface ModelData {
  id: string;
  query: string;
  entities: ModelEntity[];
  relationships: ModelRelationship[];
  parameters: ModelParameter[];
  domain_context?: {
    domain: string;
    subdomain?: string;
    constraints?: string[];
    assumptions?: string[];
  };
  metadata: {
    created_at: string;
    updated_at: string;
    version: string;
    confidence_score: number;
  };
  visualization?: {
    graph_data?: any;
    chart_data?: any;
  };
}

/**
 * Model processing options
 */
export interface ModelProcessingOptions {
  context?: Record<string, any>;
  include_visualization?: boolean;
  validation_level?: 'basic' | 'detailed';
  confidence_threshold?: number;
}

/**
 * Model validation results
 */
export interface ModelValidationResults {
  valid: boolean;
  issues: string[];
  warnings: string[];
  suggestions: string[];
  confidence_scores: {
    overall: number;
    entities: number;
    relationships: number;
    parameters: number;
  };
} 