import OpenAI from 'openai';
import { ModelData, ReasoningPath, Evidence } from '../types/solver.types';
import axios from 'axios';

export class LLMService {
    private openai: OpenAI;
    private claudeEndpoint: string;

    constructor() {
        // Initialize OpenAI
        this.openai = new OpenAI({
            apiKey: process.env.OPENAI_API_KEY,
        });
        
        // Set Claude endpoint
        this.claudeEndpoint = process.env.CLAUDE_API_ENDPOINT || 'https://api.anthropic.com/v1';
    }

    async getStrategy(prompt: string): Promise<string> {
        // Use GPT-4 for strategy selection due to its strong reasoning capabilities
        const response = await this.openai.chat.completions.create({
            model: "gpt-4",
            messages: [{
                role: "system",
                content: "You are a problem-solving strategist. Analyze the given problem and determine the most effective solution strategy."
            }, {
                role: "user",
                content: prompt
            }],
            temperature: 0.7
        });

        return response.choices[0].message?.content || '';
    }

    async exploreReasoning(modelData: ModelData, strategy: string, pathType: 'primary' | 'alternative'): Promise<ReasoningPath> {
        // Use Claude for primary reasoning path due to its strong analytical capabilities
        if (pathType === 'primary') {
            return await this.claudeReasoning(modelData, strategy);
        }

        // Use GPT-4 for alternative reasoning paths
        return await this.gptReasoning(modelData, strategy);
    }

    private async claudeReasoning(modelData: ModelData, strategy: string): Promise<ReasoningPath> {
        const response = await axios.post(
            `${this.claudeEndpoint}/messages`,
            {
                model: "claude-3-opus-20240229",
                messages: [{
                    role: "user",
                    content: this.buildReasoningPrompt(modelData, strategy)
                }],
                temperature: 0.5
            },
            {
                headers: {
                    'Authorization': `Bearer ${process.env.ANTHROPIC_API_KEY}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        return this.parseReasoningResponse(response.data.content[0].text);
    }

    private async gptReasoning(modelData: ModelData, strategy: string): Promise<ReasoningPath> {
        const response = await this.openai.chat.completions.create({
            model: "gpt-4",
            messages: [{
                role: "system",
                content: "You are an expert problem solver exploring alternative solution approaches."
            }, {
                role: "user",
                content: this.buildReasoningPrompt(modelData, strategy)
            }],
            temperature: 0.8
        });

        return this.parseReasoningResponse(response.choices[0].message?.content || '');
    }

    async findSupporting(conclusion: any, modelData: ModelData): Promise<Evidence> {
        // Use Claude for evidence gathering due to its strong knowledge base
        const response = await axios.post(
            `${this.claudeEndpoint}/messages`,
            {
                model: "claude-3-opus-20240229",
                messages: [{
                    role: "user",
                    content: this.buildEvidencePrompt(conclusion, modelData)
                }],
                temperature: 0.3
            },
            {
                headers: {
                    'Authorization': `Bearer ${process.env.ANTHROPIC_API_KEY}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        return this.parseEvidenceResponse(response.data.content[0].text);
    }

    async generateSolutionResponse(params: {
        modelData: ModelData;
        results: any;
        evidence: Evidence[];
        requirementsLevel: string;
    }): Promise<any> {
        // Use GPT-4 for response generation due to its strong natural language capabilities
        const response = await this.openai.chat.completions.create({
            model: "gpt-4",
            messages: [{
                role: "system",
                content: "You are an expert at synthesizing complex information into clear, well-structured responses."
            }, {
                role: "user",
                content: this.buildResponsePrompt(params)
            }],
            temperature: 0.6
        });

        return JSON.parse(response.choices[0].message?.content || '{}');
    }

    async validateSolution(solution: any, originalModel: ModelData): Promise<any> {
        // Use both models for validation and combine their insights
        const [claudeValidation, gptValidation] = await Promise.all([
            this.claudeValidation(solution, originalModel),
            this.gptValidation(solution, originalModel)
        ]);

        return this.combineValidations(claudeValidation, gptValidation);
    }

    async refineSolution(solution: any, issues: string[]): Promise<any> {
        // Use GPT-4 for refinement due to its strong problem-solving capabilities
        const response = await this.openai.chat.completions.create({
            model: "gpt-4",
            messages: [{
                role: "system",
                content: "You are an expert at refining and improving solutions based on identified issues."
            }, {
                role: "user",
                content: this.buildRefinementPrompt(solution, issues)
            }],
            temperature: 0.5
        });

        return JSON.parse(response.choices[0].message?.content || '{}');
    }

    private buildReasoningPrompt(modelData: ModelData, strategy: string): string {
        return `
            Given the following model and strategy:
            Model: ${JSON.stringify(modelData, null, 2)}
            Strategy: ${strategy}

            Develop a detailed reasoning path that:
            1. Follows the provided strategy
            2. Considers all relevant parameters and relationships
            3. Applies appropriate formulas and principles
            4. Accounts for constraints and limitations
            5. Provides clear step-by-step reasoning
            6. Includes confidence levels for each step

            Respond with a structured JSON object containing the reasoning path.
        `;
    }

    private buildEvidencePrompt(conclusion: any, modelData: ModelData): string {
        return `
            For the following conclusion:
            ${JSON.stringify(conclusion, null, 2)}

            In the context of this model:
            ${JSON.stringify(modelData, null, 2)}

            Find supporting evidence that:
            1. Validates the conclusion
            2. References relevant principles or formulas
            3. Considers the problem context
            4. Includes reliability assessment

            Respond with a structured JSON object containing the evidence.
        `;
    }

    private buildResponsePrompt(params: any): string {
        return `
            Given:
            - Model: ${JSON.stringify(params.modelData, null, 2)}
            - Results: ${JSON.stringify(params.results, null, 2)}
            - Evidence: ${JSON.stringify(params.evidence, null, 2)}
            - Requirements Level: ${params.requirementsLevel}

            Generate a comprehensive solution response that:
            1. Clearly presents conclusions
            2. Explains the reasoning process
            3. Cites supporting evidence
            4. Addresses uncertainty
            5. Matches the required technical level
            6. Includes relevant visualizations

            Respond with a structured JSON object containing the complete solution package.
        `;
    }

    private parseReasoningResponse(response: string): ReasoningPath {
        try {
            return JSON.parse(response);
        } catch (error) {
            console.error('Error parsing reasoning response:', error);
            throw error;
        }
    }

    private parseEvidenceResponse(response: string): Evidence {
        try {
            return JSON.parse(response);
        } catch (error) {
            console.error('Error parsing evidence response:', error);
            throw error;
        }
    }

    private async claudeValidation(solution: any, originalModel: ModelData): Promise<any> {
        const response = await axios.post(
            `${this.claudeEndpoint}/messages`,
            {
                model: "claude-3-opus-20240229",
                messages: [{
                    role: "user",
                    content: this.buildValidationPrompt(solution, originalModel)
                }],
                temperature: 0.3
            },
            {
                headers: {
                    'Authorization': `Bearer ${process.env.ANTHROPIC_API_KEY}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        return JSON.parse(response.data.content[0].text);
    }

    private async gptValidation(solution: any, originalModel: ModelData): Promise<any> {
        const response = await this.openai.chat.completions.create({
            model: "gpt-4",
            messages: [{
                role: "system",
                content: "You are an expert at validating solution quality and identifying potential issues."
            }, {
                role: "user",
                content: this.buildValidationPrompt(solution, originalModel)
            }],
            temperature: 0.3
        });

        return JSON.parse(response.choices[0].message?.content || '{}');
    }

    private buildValidationPrompt(solution: any, originalModel: ModelData): string {
        return `
            Validate this solution:
            ${JSON.stringify(solution, null, 2)}

            Against this original model:
            ${JSON.stringify(originalModel, null, 2)}

            Assess:
            1. Accuracy of conclusions
            2. Completeness of reasoning
            3. Consistency with model
            4. Quality of evidence
            5. Handling of uncertainty
            6. Technical accuracy

            Respond with a structured JSON object containing validation results and quality metrics.
        `;
    }

    private buildRefinementPrompt(solution: any, issues: string[]): string {
        return `
            Refine this solution:
            ${JSON.stringify(solution, null, 2)}

            Addressing these issues:
            ${JSON.stringify(issues, null, 2)}

            Provide:
            1. Corrected conclusions
            2. Improved reasoning
            3. Additional evidence if needed
            4. Better uncertainty handling
            5. Enhanced clarity

            Respond with a structured JSON object containing the refined solution.
        `;
    }

    private combineValidations(claudeValidation: any, gptValidation: any): any {
        // Combine and average metrics from both validations
        const metrics = {
            accuracy: (claudeValidation.metrics.accuracy + gptValidation.metrics.accuracy) / 2,
            completeness: (claudeValidation.metrics.completeness + gptValidation.metrics.completeness) / 2,
            consistency: (claudeValidation.metrics.consistency + gptValidation.metrics.consistency) / 2,
            relevance: (claudeValidation.metrics.relevance + gptValidation.metrics.relevance) / 2,
            confidence: (claudeValidation.metrics.confidence + gptValidation.metrics.confidence) / 2
        };

        // Combine unique issues from both validations
        const issues = [...new Set([...claudeValidation.issues, ...gptValidation.issues])];

        return {
            isValid: metrics.accuracy >= 0.8 && metrics.completeness >= 0.8,
            metrics,
            issues
        };
    }
} 