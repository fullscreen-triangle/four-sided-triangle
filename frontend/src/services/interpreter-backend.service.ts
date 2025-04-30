import axios from 'axios';
import { 
    InterpretationRequest, 
    InterpretationResponse,
    QualityMetrics,
    InterpretedSolution
} from '../types/interpreter.types';
import { SolutionPackage } from '../types/solver.types';

export class InterpreterBackendService {
    private baseUrl: string;

    constructor() {
        this.baseUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';
    }

    /**
     * Send a solution package to be interpreted by the backend
     */
    async interpretSolution(request: InterpretationRequest): Promise<InterpretationResponse> {
        try {
            const response = await axios.post(
                `${this.baseUrl}/api/interpreter/interpret`,
                request,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            return response.data;
        } catch (error) {
            console.error('Error interpreting solution:', error);
            throw error;
        }
    }

    /**
     * Assess the quality of an interpreted solution
     */
    async assessQuality(
        interpretedSolution: InterpretedSolution,
        originalSolution: SolutionPackage
    ): Promise<QualityMetrics> {
        try {
            const response = await axios.post(
                `${this.baseUrl}/api/interpreter/assess-quality`,
                {
                    interpretedSolution,
                    originalSolution
                },
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            return response.data;
        } catch (error) {
            console.error('Error assessing solution quality:', error);
            throw error;
        }
    }

    /**
     * Generate follow-up suggestions based on the interpreted solution
     */
    async generateFollowUps(
        interpretedSolution: InterpretedSolution,
        userContext: any
    ): Promise<string[]> {
        try {
            const response = await axios.post(
                `${this.baseUrl}/api/interpreter/follow-ups`,
                {
                    interpretedSolution,
                    userContext
                },
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            return response.data.suggestions;
        } catch (error) {
            console.error('Error generating follow-up suggestions:', error);
            throw error;
        }
    }

    /**
     * Enhance the clarity of an explanation
     */
    async enhanceClarity(
        content: string,
        keyConcepts: string[],
        expertiseLevel: string
    ): Promise<string> {
        try {
            const response = await axios.post(
                `${this.baseUrl}/api/interpreter/enhance-clarity`,
                {
                    content,
                    keyConcepts,
                    expertiseLevel
                },
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            return response.data.enhancedContent;
        } catch (error) {
            console.error('Error enhancing clarity:', error);
            throw error;
        }
    }
} 