/**
 * Types related to user context for RAG pipeline
 */

export type ExpertiseLevel = 'beginner' | 'intermediate' | 'expert' | 'general';

export interface UserContext {
  expertiseLevel: ExpertiseLevel;
  domain?: string;
  preferences?: {
    detailLevel?: 'minimal' | 'standard' | 'detailed';
    visualPreference?: 'text' | 'charts' | 'diagrams' | 'mixed';
    responseFormat?: 'concise' | 'elaborate';
  };
  history?: {
    recentQueries?: string[];
    topicInterests?: string[];
  };
} 