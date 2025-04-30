export interface ModelData {
    entities: Entity[];
    relationships: Relationship[];
    parameters: Parameter[];
    constraints: Constraint[];
    contextLevel: string;
    domainKnowledge: DomainKnowledge;
}

export interface Entity {
    id: string;
    name: string;
    type: string;
    properties: Record<string, any>;
}

export interface Relationship {
    id: string;
    sourceId: string;
    targetId: string;
    type: string;
    properties: Record<string, any>;
}

export interface Parameter {
    id: string;
    name: string;
    value?: number | string;
    unit?: string;
    constraints?: ParameterConstraint[];
    relationships?: ParameterRelationship[];
}

export interface Constraint {
    id: string;
    type: string;
    condition: string;
    entities: string[];
    parameters: string[];
}

export interface DomainKnowledge {
    formulas: Formula[];
    principles: Principle[];
    contextualInformation: Record<string, any>;
}

export interface Formula {
    id: string;
    expression: string;
    parameters: string[];
    applicabilityConditions?: string[];
}

export interface Principle {
    id: string;
    description: string;
    applicableDomains: string[];
}

export interface ParameterConstraint {
    type: string;
    value: number | string;
    operator: string;
}

export interface ParameterRelationship {
    targetParameterId: string;
    relationship: string;
    formula?: string;
}

export interface ReasoningPath {
    id: string;
    strategy: string;
    steps: ReasoningStep[];
    confidence: number;
    assumptions: string[];
}

export interface ReasoningStep {
    id: string;
    type: string;
    description: string;
    inputs: string[];
    outputs: string[];
    confidence: number;
}

export interface Evidence {
    id: string;
    type: string;
    content: string;
    source: string;
    relevance: number;
    reliability: number;
}

export interface SolutionPackage {
    conclusions: Conclusion[];
    reasoning: ReasoningPath[];
    evidence: Evidence[];
    visualizations?: Visualization[];
    qualityMetrics: QualityMetrics;
    uncertaintyIndicators: UncertaintyIndicator[];
}

export interface Conclusion {
    id: string;
    statement: string;
    confidence: number;
    supportingEvidence: string[];
    parameters: Record<string, any>;
}

export interface Visualization {
    id: string;
    type: string;
    data: any;
    parameters: Record<string, any>;
}

export interface QualityMetrics {
    accuracy: number;
    completeness: number;
    consistency: number;
    relevance: number;
    confidence: number;
}

export interface UncertaintyIndicator {
    aspect: string;
    level: number;
    description: string;
    mitigation?: string;
} 