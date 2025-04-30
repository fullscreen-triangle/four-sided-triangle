/**
 * RAG Pipeline Module
 * 
 * Integrates all components of the 7-stage RAG system into a cohesive pipeline with metacognitive orchestration:
 * 1. Query Analysis: Parse and understand user query
 * 2. Knowledge Retrieval: Retrieve relevant documents from knowledge base
 * 3. Modeler: Transform query and knowledge into structured knowledge model
 * 4. Reasoning: Apply systematic reasoning to analyze the problem
 * 5. Solver: Generate solutions based on reasoning and knowledge
 * 6. Interpreter: Transform solution into user-friendly response
 * 7. Evaluation: Self-assess response quality and completeness
 * 
 * The Metacognitive Orchestrator coordinates between these stages and manages the processing flow.
 */

import { Solver } from './solver/solver';
import { Interpreter } from './interpreter/interpreter';
import { processModel } from './modeler/modelIntegration';
import { LLMService } from '../services/llm.service';
import { SolverBackendService } from '../services/solver-backend.service';
import { InterpreterBackendService } from '../services/interpreter-backend.service';
import { ModelData } from '../types/modeler.types';
import { SolutionPackage } from '../types/solver.types';
import { InterpretationResponse, UserContext } from '../types/interpreter.types';
import { QueryAnalyzer } from './query/queryAnalyzer';
import { KnowledgeRetriever } from './query/knowledgeRetriever';
import { Reasoner } from './solver/reasoner';
import { Evaluator } from './result/evaluator';
import { MetacognitiveOrchestrator } from './orchestrator';

export interface PipelineResult {
  queryAnalysis: any;
  retrievedKnowledge: any;
  model: ModelData;
  reasoning: any;
  solution: SolutionPackage;
  interpretation: InterpretationResponse;
  evaluation: any;
  processingTime: {
    queryAnalysis: number;
    retrieval: number;
    modeling: number;
    reasoning: number;
    solving: number;
    interpreting: number;
    evaluation: number;
    total: number;
  };
  metacognitiveInsights: any;
}

export class RAGPipeline {
  private queryAnalyzer: QueryAnalyzer;
  private knowledgeRetriever: KnowledgeRetriever;
  private reasoner: Reasoner;
  private solver: Solver;
  private interpreter: Interpreter;
  private evaluator: Evaluator;
  private orchestrator: MetacognitiveOrchestrator;
  private llmService: LLMService;
  private solverBackendService: SolverBackendService;
  private interpreterBackendService: InterpreterBackendService;

  constructor() {
    this.llmService = new LLMService();
    this.solverBackendService = new SolverBackendService();
    this.interpreterBackendService = new InterpreterBackendService();
    
    // Initialize all 7 components
    this.queryAnalyzer = new QueryAnalyzer(this.llmService);
    this.knowledgeRetriever = new KnowledgeRetriever();
    this.reasoner = new Reasoner(this.llmService);
    this.solver = new Solver(this.llmService, this.solverBackendService);
    this.interpreter = new Interpreter(this.llmService, this.interpreterBackendService);
    this.evaluator = new Evaluator(this.llmService);
    
    // Initialize the metacognitive orchestrator
    this.orchestrator = new MetacognitiveOrchestrator(
      this.queryAnalyzer,
      this.knowledgeRetriever,
      this.reasoner,
      this.solver, 
      this.interpreter,
      this.evaluator,
      this.llmService
    );
  }

  /**
   * Process a query through the complete 7-stage RAG pipeline with metacognitive orchestration
   * 
   * @param query The user's natural language query
   * @param userContext Context about the user (expertise level, etc.)
   * @param options Additional options for processing
   * @returns Complete pipeline result with all stages and metacognitive insights
   */
  async process(
    query: string,
    userContext: UserContext = { expertiseLevel: 'general' },
    options: {
      queryOptions?: any;
      retrievalOptions?: any;
      modelingOptions?: any;
      reasoningOptions?: any;
      solverOptions?: any;
      interpreterOptions?: any;
      evaluationOptions?: any;
      orchestrationOptions?: any;
    } = {}
  ): Promise<PipelineResult> {
    const startTime = Date.now();
    
    try {
      // Use the orchestrator to coordinate the entire pipeline
      const result = await this.orchestrator.processPipeline(
        query,
        userContext,
        options
      );
      
      const totalTime = Date.now() - startTime;
      result.processingTime.total = totalTime;
      
      return result;
    } catch (error) {
      console.error("Error in RAG pipeline:", error);
      throw new Error(`Pipeline processing failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Process a query but stop after the modeling stage
   */
  async processUntilModel(query: string, options: any = {}): Promise<ModelData> {
    return processModel(query, options);
  }

  /**
   * Process starting from an existing model through solver and interpreter
   */
  async processFromModel(
    model: ModelData,
    userContext: UserContext = { expertiseLevel: 'general' },
    options: {
      solverOptions?: any;
      interpreterOptions?: any;
    } = {}
  ): Promise<Omit<PipelineResult, 'model' | 'processingTime'> & { processingTime: Omit<PipelineResult['processingTime'], 'modeling'> }> {
    const startTime = Date.now();
    
    try {
      // Step 2: Solve - Apply reasoning to solve the problem
      console.log("Pipeline step 2: Solving...");
      const solvingStart = Date.now();
      const solution = await this.solver.solve(model);
      const solvingTime = Date.now() - solvingStart;
      
      // Step 3: Interpret - Transform solution into user-friendly response
      console.log("Pipeline step 3: Interpreting...");
      const interpretingStart = Date.now();
      const interpretation = await this.interpreter.interpret(
        solution, 
        userContext,
        options.interpreterOptions
      );
      const interpretingTime = Date.now() - interpretingStart;
      
      const totalTime = Date.now() - startTime;
      
      return {
        solution,
        interpretation,
        processingTime: {
          solving: solvingTime,
          interpreting: interpretingTime,
          total: totalTime
        }
      };
    } catch (error) {
      console.error("Error in partial RAG pipeline:", error);
      throw new Error(`Pipeline processing failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Re-interpret an existing solution with different user context
   */
  async reinterpret(
    solution: SolutionPackage,
    userContext: UserContext,
    options: any = {}
  ): Promise<InterpretationResponse> {
    return this.interpreter.interpret(solution, userContext, options);
  }

  /**
   * Adapt an existing interpretation to a different expertise level
   */
  async adaptInterpretation(
    interpretation: InterpretationResponse,
    newExpertiseLevel: 'beginner' | 'intermediate' | 'expert' | 'general'
  ): Promise<InterpretationResponse> {
    return this.interpreter.adaptToExpertiseLevel(interpretation, newExpertiseLevel);
  }

  /**
   * Generate additional follow-up suggestions for an interpretation
   */
  async generateFollowUps(
    interpretation: InterpretationResponse,
    userContext: UserContext
  ): Promise<string[]> {
    return this.interpreter.generateAdditionalSuggestions(interpretation, userContext);
  }
} 