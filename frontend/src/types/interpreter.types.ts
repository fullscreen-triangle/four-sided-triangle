import { SolutionPackage } from './solver.types';

export interface UserContext {
    expertiseLevel: 'beginner' | 'intermediate' | 'expert' | 'general';
    preferredModel?: string;
    detailPreference?: 'minimal' | 'balanced' | 'detailed';
    visualPreference?: boolean;
    previousInteractions?: UserInteraction[];
}

export interface UserInteraction {
    timestamp: number;
    query: string;
    responseId: string;
}

export interface PresentationRequirements {
    format: 'text' | 'structured' | 'visual';
    detailLevel: 'minimal' | 'balanced' | 'detailed';
    focusAreas?: string[];
    highlightParameters?: string[];
}

export interface VisualizationElement {
    id: string;
    type: string;
    title: string;
    description: string;
    data: any;
    config: Record<string, any>;
}

export interface InterpretedSolution {
    technicalExplanation: string;
    userFriendlyExplanation: string;
    keyInsights: string[];
    visualElements?: VisualizationElement[];
    sources?: Array<{
        id: string;
        type: string;
        citation: string;
        url?: string;
    }>;
    followUpSuggestions?: string[];
}

export interface QualityMetrics {
    accuracy: number;
    completeness: number;
    clarity: number;
    relevance: number;
    biasAssessment: number;
    overallQuality: number;
}

export interface InterpretationRequest {
    solutionPackage: SolutionPackage;
    userContext: UserContext;
    presentationRequirements?: PresentationRequirements;
}

export interface InterpretationResponse {
    interpretedSolution: InterpretedSolution;
    qualityMetrics: QualityMetrics;
    metadata: Record<string, any>;
} 