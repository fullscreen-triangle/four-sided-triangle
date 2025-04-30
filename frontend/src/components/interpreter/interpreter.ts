import { LLMService } from '../../services/llm.service';
import { InterpreterBackendService } from '../../services/interpreter-backend.service';
import { 
    InterpretationRequest, 
    InterpretationResponse, 
    InterpretedSolution,
    UserContext,
    PresentationRequirements,
    QualityMetrics
} from '../../types/interpreter.types';
import { SolutionPackage } from '../../types/solver.types';

export class Interpreter {
    private llmService: LLMService;
    private backendService: InterpreterBackendService;

    constructor(llmService: LLMService, backendService: InterpreterBackendService) {
        this.llmService = llmService;
        this.backendService = backendService;
    }

    /**
     * Main method to interpret a solution from the solver
     */
    async interpret(
        solutionPackage: SolutionPackage, 
        userContext: UserContext,
        presentationRequirements?: PresentationRequirements
    ): Promise<InterpretationResponse> {
        try {
            // 1. Prepare interpretation request
            const request: InterpretationRequest = {
                solutionPackage,
                userContext,
                presentationRequirements
            };

            // 2. Send to backend for processing
            const interpretation = await this.backendService.interpretSolution(request);
            
            // 3. Apply any additional client-side enhancements
            const enhancedInterpretation = await this.enhanceInterpretation(
                interpretation,
                userContext
            );

            // 4. Return the enhanced interpretation
            return enhancedInterpretation;
        } catch (error) {
            console.error('Error in interpretation process:', error);
            // Provide fallback interpretation
            return this.generateFallbackInterpretation(solutionPackage, userContext);
        }
    }

    /**
     * Apply client-side enhancements to the interpretation
     */
    private async enhanceInterpretation(
        interpretation: InterpretationResponse,
        userContext: UserContext
    ): Promise<InterpretationResponse> {
        // We could add additional client-side enhancements here
        // such as formatting, additional visualizations, etc.
        
        // For now, just return the interpretation as-is
        return interpretation;
    }

    /**
     * Generate a simple fallback interpretation if the backend fails
     */
    private generateFallbackInterpretation(
        solutionPackage: SolutionPackage,
        userContext: UserContext
    ): InterpretationResponse {
        // Extract conclusions from solution package
        const conclusions = solutionPackage.conclusions || [];
        
        // Create a minimal explanation from conclusions
        let explanation = 'Based on the analysis, ';
        
        if (conclusions.length > 0) {
            explanation += 'the following conclusions were reached: ';
            explanation += conclusions
                .slice(0, 3)
                .map(c => c.statement)
                .join('; ');
        } else {
            explanation += 'no clear conclusions could be determined.';
        }
        
        // Create a minimal interpreted solution
        const interpretedSolution: InterpretedSolution = {
            technicalExplanation: explanation,
            userFriendlyExplanation: explanation,
            keyInsights: conclusions.slice(0, 3).map(c => c.statement),
            followUpSuggestions: ['Consider refining your query.']
        };
        
        // Create minimal quality metrics
        const qualityMetrics: QualityMetrics = {
            accuracy: 0.7,
            completeness: 0.7,
            clarity: 0.7,
            relevance: 0.7,
            biasAssessment: 0.1,
            overallQuality: 0.7
        };
        
        return {
            interpretedSolution,
            qualityMetrics,
            metadata: {
                generationMethod: 'fallback',
                error: 'Backend service unavailable'
            }
        };
    }

    /**
     * Adapt an interpretation to a different expertise level
     */
    async adaptToExpertiseLevel(
        interpretation: InterpretationResponse,
        newExpertiseLevel: 'beginner' | 'intermediate' | 'expert' | 'general'
    ): Promise<InterpretationResponse> {
        try {
            // Create a modified user context with the new expertise level
            const userContext: UserContext = {
                expertiseLevel: newExpertiseLevel
            };
            
            // Get key concepts from the existing interpretation
            const keyConcepts = interpretation.interpretedSolution.keyInsights;
            
            // Enhance clarity with the new expertise level
            const enhancedExplanation = await this.backendService.enhanceClarity(
                interpretation.interpretedSolution.userFriendlyExplanation,
                keyConcepts,
                newExpertiseLevel
            );
            
            // Create a new interpreted solution with the adapted explanation
            const adaptedSolution: InterpretedSolution = {
                ...interpretation.interpretedSolution,
                userFriendlyExplanation: enhancedExplanation
            };
            
            // Return the adapted interpretation
            return {
                ...interpretation,
                interpretedSolution: adaptedSolution,
                metadata: {
                    ...interpretation.metadata,
                    adaptedTo: newExpertiseLevel
                }
            };
        } catch (error) {
            console.error('Error adapting to expertise level:', error);
            return interpretation; // Return original if adaptation fails
        }
    }

    /**
     * Generate additional follow-up suggestions
     */
    async generateAdditionalSuggestions(
        interpretation: InterpretationResponse,
        userContext: UserContext
    ): Promise<string[]> {
        try {
            return await this.backendService.generateFollowUps(
                interpretation.interpretedSolution,
                userContext
            );
        } catch (error) {
            console.error('Error generating additional suggestions:', error);
            return [
                'Explore related topics',
                'Refine your query for more specific results'
            ];
        }
    }
} 