import axios from 'axios';
import { ModelData, ReasoningPath } from '../types/solver.types';

export interface ComputationRequest {
    modelData: ModelData;
    reasoningPaths: ReasoningPath[];
}

export interface ComputationResponse {
    results: any;
    conclusions: Array<{
        id: string;
        statement: string;
        confidence: number;
        parameters: Record<string, any>;
    }>;
    metrics: {
        computationTime: number;
        complexity: number;
        confidence: number;
    };
}

export class SolverBackendService {
    private baseUrl: string;

    constructor() {
        this.baseUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';
    }

    async computeResults(request: ComputationRequest): Promise<ComputationResponse> {
        try {
            const response = await axios.post(
                `${this.baseUrl}/api/solver/compute`,
                request,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            return response.data;
        } catch (error) {
            console.error('Error computing results:', error);
            throw error;
        }
    }

    async validateFormula(formula: string, parameters: Record<string, any>): Promise<boolean> {
        try {
            const response = await axios.post(
                `${this.baseUrl}/api/solver/validate-formula`,
                {
                    formula,
                    parameters
                }
            );

            return response.data.isValid;
        } catch (error) {
            console.error('Error validating formula:', error);
            throw error;
        }
    }

    async evaluateExpression(
        expression: string,
        parameters: Record<string, any>,
        constraints: Array<{condition: string; parameters: string[]}>
    ): Promise<number> {
        try {
            const response = await axios.post(
                `${this.baseUrl}/api/solver/evaluate`,
                {
                    expression,
                    parameters,
                    constraints
                }
            );

            return response.data.result;
        } catch (error) {
            console.error('Error evaluating expression:', error);
            throw error;
        }
    }
} 