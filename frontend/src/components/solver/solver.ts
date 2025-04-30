import { LLMService } from '../../services/llm.service';
import { SolverBackendService } from '../../services/solver-backend.service';
import { ModelData, SolutionPackage, ReasoningPath, Evidence, Conclusion } from '../../types/solver.types';

export class Solver {
    private llmService: LLMService;
    private backendService: SolverBackendService;

    constructor(llmService: LLMService, backendService: SolverBackendService) {
        this.llmService = llmService;
        this.backendService = backendService;
    }

    async solve(modelData: ModelData): Promise<SolutionPackage> {
        try {
            // 1. Strategy Selection
            const strategy = await this.selectSolutionStrategy(modelData);

            // 2. Multi-path Reasoning
            const reasoningPaths = await this.exploreReasoningPaths(modelData, strategy);

            // 3. Parameter Analysis & Formula Application
            const computedResults = await this.computeResults(modelData, reasoningPaths);

            // 4. Evidence Gathering
            const evidence = await this.gatherEvidence(modelData, computedResults);

            // 5. Response Generation
            const response = await this.generateResponse(modelData, computedResults, evidence);

            // 6. Quality Assessment
            const validatedResponse = await this.validateResponse(response, modelData);

            return validatedResponse;
        } catch (error) {
            console.error('Error in solver process:', error);
            throw error;
        }
    }

    private async selectSolutionStrategy(modelData: ModelData): Promise<string> {
        const prompt = this.buildStrategySelectionPrompt(modelData);
        return await this.llmService.getStrategy(prompt);
    }

    private async exploreReasoningPaths(modelData: ModelData, strategy: string): Promise<ReasoningPath[]> {
        // Parallel exploration of multiple reasoning approaches
        const paths = await Promise.all([
            this.llmService.exploreReasoning(modelData, strategy, 'primary'),
            this.llmService.exploreReasoning(modelData, strategy, 'alternative')
        ]);

        return paths.filter(path => path.confidence > 0.7);
    }

    private async computeResults(modelData: ModelData, reasoningPaths: ReasoningPath[]) {
        // Delegate heavy computation to Python backend
        return await this.backendService.computeResults({
            modelData,
            reasoningPaths
        });
    }

    private async gatherEvidence(modelData: ModelData, results: any): Promise<Evidence[]> {
        const evidencePromises = results.conclusions.map(async (conclusion: Conclusion) => {
            return await this.llmService.findSupporting(conclusion, modelData);
        });

        return await Promise.all(evidencePromises);
    }

    private async generateResponse(modelData: ModelData, results: any, evidence: Evidence[]) {
        return await this.llmService.generateSolutionResponse({
            modelData,
            results,
            evidence,
            requirementsLevel: modelData.contextLevel
        });
    }

    private async validateResponse(response: any, originalModel: ModelData) {
        const validation = await this.llmService.validateSolution(response, originalModel);
        
        if (!validation.isValid) {
            // Attempt to fix issues
            response = await this.llmService.refineSolution(response, validation.issues);
        }

        return {
            ...response,
            qualityMetrics: validation.metrics
        };
    }

    private buildStrategySelectionPrompt(modelData: ModelData): string {
        return `
            Given the following model and parameters:
            ${JSON.stringify(modelData, null, 2)}
            
            Determine the most appropriate solution strategy considering:
            1. The type of problem (computational, logical, comparative)
            2. Available formulas and relationships
            3. Constraints and limitations
            4. Required confidence level
            
            Provide a structured strategy that outlines the solving approach.
        `;
    }
} 