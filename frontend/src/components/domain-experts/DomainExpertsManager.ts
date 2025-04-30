/**
 * Domain Experts Manager
 * 
 * Manages multiple domain expert LLMs and routes queries to the appropriate expert
 * based on the query content and user selection.
 */

import { UserContext } from '../../types/interpreter.types';

export interface DomainExpert {
  id: string;
  name: string;
  description: string;
  icon: string;
  isAvailable: boolean;
  isExperimental: boolean;
  domains: string[];
}

export interface DomainExpertQuery {
  query: string;
  context: any;
  expertId: string;
}

export interface DomainExpertResponse {
  result: any;
  confidence: number;
  metadata: {
    processingTime: number;
    model: string;
    reasoningSteps: any[];
  };
}

export class DomainExpertsManager {
  private experts: Map<string, DomainExpert> = new Map();
  
  constructor() {
    // Register default experts
    this.registerExpert({
      id: 'sprint-llm',
      name: 'Sprint Biomechanics',
      description: 'Expert in human biomechanics, sprint mechanics, and athletic performance',
      icon: 'running',
      isAvailable: true,
      isExperimental: false,
      domains: ['athletics', 'biomechanics', 'sport-science']
    });
    
    this.registerExpert({
      id: 'olympic-llm',
      name: 'Olympic Performance',
      description: 'Expert in Olympic standards, competitive analytics and athletic benchmarking',
      icon: 'medal',
      isAvailable: true,
      isExperimental: false,
      domains: ['olympics', 'sports-analytics', 'competition']
    });
    
    // Register experimental experts
    this.registerExpert({
      id: 'nutrition-llm',
      name: 'Athletic Nutrition',
      description: 'Specialist in sports nutrition, metabolic optimization and dietary planning',
      icon: 'nutrition',
      isAvailable: false,
      isExperimental: true,
      domains: ['nutrition', 'metabolism', 'supplements']
    });
    
    this.registerExpert({
      id: 'injury-llm',
      name: 'Injury Prevention',
      description: 'Expert in athletic injury prevention, recovery protocols and rehabilitation',
      icon: 'medical',
      isAvailable: false,
      isExperimental: true,
      domains: ['injury', 'rehabilitation', 'prevention']
    });
  }
  
  /**
   * Register a new domain expert LLM
   */
  registerExpert(expert: DomainExpert): void {
    this.experts.set(expert.id, expert);
    console.log(`Registered domain expert: ${expert.name}`);
  }
  
  /**
   * Get all available domain experts
   */
  getAvailableExperts(): DomainExpert[] {
    return Array.from(this.experts.values())
      .filter(expert => expert.isAvailable || expert.isExperimental);
  }
  
  /**
   * Get a specific domain expert by ID
   */
  getExpertById(id: string): DomainExpert | undefined {
    return this.experts.get(id);
  }
  
  /**
   * Find the most suitable expert for a given query
   */
  findSuitableExpert(query: string): DomainExpert | undefined {
    // Simple keyword matching for now - could be enhanced with embeddings
    const queryLower = query.toLowerCase();
    
    // Check for explicit domain keywords
    for (const expert of this.experts.values()) {
      if (!expert.isAvailable) continue;
      
      for (const domain of expert.domains) {
        if (queryLower.includes(domain)) {
          return expert;
        }
      }
      
      // Check for expert name in query
      if (queryLower.includes(expert.name.toLowerCase())) {
        return expert;
      }
    }
    
    // Default to sprint expert if no clear match
    return this.getExpertById('sprint-llm');
  }
  
  /**
   * Process a query with the appropriate domain expert
   */
  async processExpertQuery(
    query: string, 
    expertId: string | null,
    userContext: UserContext
  ): Promise<DomainExpertResponse> {
    const startTime = Date.now();
    
    // Determine which expert to use
    let expert: DomainExpert | undefined;
    
    if (expertId) {
      expert = this.getExpertById(expertId);
    }
    
    if (!expert) {
      expert = this.findSuitableExpert(query);
    }
    
    if (!expert || !expert.isAvailable) {
      throw new Error('No suitable domain expert available for this query');
    }
    
    console.log(`Processing query with domain expert: ${expert.name}`);
    
    // TODO: Connect to actual domain expert LLMs
    // For now, return a mock response
    const processingTime = Date.now() - startTime;
    
    return {
      result: {
        answer: `This is a simulated response from the ${expert.name} domain expert.`,
        analysis: `The query was analyzed using ${expert.name} specialized knowledge.`,
        references: []
      },
      confidence: 0.85,
      metadata: {
        processingTime,
        model: expert.id,
        reasoningSteps: []
      }
    };
  }
  
  /**
   * Update the availability status of domain experts
   * Used when new models become available or when existing ones go offline
   */
  updateExpertAvailability(expertId: string, isAvailable: boolean): void {
    const expert = this.experts.get(expertId);
    if (expert) {
      expert.isAvailable = isAvailable;
      console.log(`Updated availability for ${expert.name}: ${isAvailable}`);
    }
  }
}

export default DomainExpertsManager;
