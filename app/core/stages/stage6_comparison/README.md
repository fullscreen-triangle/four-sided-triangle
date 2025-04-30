# Response Comparison Stage (Stage 6)

## Overview

The Response Comparison stage implements ensemble diversification techniques to compare and combine multiple response candidates, creating an optimal integrated response that maximizes both quality and diversity. This stage follows the Response Scoring stage (Stage 5) and precedes the Threshold Verification stage (Stage 7).

## Components

### 1. ResponseComparisonService

**Purpose**: Orchestrates the entire response comparison process by coordinating the ensemble diversifier, diversity calculator, quality-diversity optimizer, and response combiner.

**Key Functions**:

- `process(prompt, context)`: Processes and compares multiple response candidates, returning an optimized combined response.
- `refine(refinement_prompt, context, previous_output)`: Refines a combined response based on feedback, tracking changes.
- `_process_single_response(primary_response, evaluation_metrics)`: Processes a single response when no alternatives are available.
- `_generate_alternative_responses(primary_response, context, max_alternatives)`: Generates alternative responses when none are provided.
- `_track_refinement_changes(previous_output, refined_output)`: Tracks changes between previous and refined output.

### 2. EnsembleDiversifier

**Purpose**: Implements ensemble diversification to create an optimal ensemble of response candidates, balancing between quality and diversity.

**Key Functions**:

- `diversify(primary_response, alternative_responses, diversity_scores, alpha)`: Creates a diversified ensemble of responses.
- `_extract_quality_scores(primary_response, alternative_responses)`: Extracts quality scores for all candidates.
- `_apply_greedy_diversification(candidates, quality_scores, diversity_scores, alpha)`: Applies greedy diversification algorithm.
- `_apply_mmr_diversification(candidates, quality_scores, diversity_scores, alpha)`: Applies Maximal Marginal Relevance (MMR) algorithm.

### 3. DiversityCalculator

**Purpose**: Computes pairwise diversity scores between response candidates, measuring how different they are across multiple dimensions.

**Key Functions**:

- `calculate_diversity(primary_response, alternative_responses)`: Calculates diversity metrics between response candidates.
- `_calculate_content_diversity(response1, response2)`: Measures how different the actual content is.
- `_calculate_structure_diversity(response1, response2)`: Measures how differently the content is organized.
- `_calculate_emphasis_diversity(response1, response2)`: Measures how differently the responses emphasize information.
- `_tokenize(text)`: Tokenizes text into words for comparison.
- `_create_ngrams(tokens, n)`: Creates n-grams from tokens for content comparison.
- `_calculate_type_distribution(elements)`: Calculates distribution of element types.
- `_calculate_distribution_difference(dist1, dist2)`: Calculates difference between distributions.

### 4. QualityDiversityOptimizer

**Purpose**: Optimizes the balance between quality and diversity in the response ensemble using Pareto optimization.

**Key Functions**:

- `optimize(ensemble, evaluation_metrics, diversity_scores)`: Optimizes the quality-diversity trade-off.
- `get_trade_off_metrics()`: Returns metrics from the last optimization.
- `_extract_quality_scores(ensemble, evaluation_metrics)`: Extracts quality scores for candidates.
- `_calculate_candidate_diversity(ensemble, pairwise_diversity)`: Calculates diversity score for each candidate.
- `_identify_pareto_optimal(ensemble, quality_scores, diversity_scores)`: Identifies Pareto-optimal components.
- `_select_optimal_elements(ensemble, pareto_optimal, quality_scores, diversity_scores)`: Selects optimal elements.
- `_calculate_component_weights(ensemble, quality_scores, diversity_scores, pareto_optimal)`: Calculates weights for components.
- `_extract_elements(response)`: Extracts and copies elements from a response.

### 5. ResponseCombiner

**Purpose**: Combines optimized components from multiple response candidates into a coherent, integrated response.

**Key Functions**:

- `combine(optimized_components, primary_response, evaluation_metrics)`: Combines optimized components.
- `_create_base_response(primary_response)`: Creates a base response structure from the primary response.
- `_restructure_sections(optimized_elements, primary_sections, pareto_indices)`: Restructures elements into sections.
- `_add_to_existing_sections(elements, sections)`: Adds elements to existing sections based on relevance.
- `_create_new_section(elements, sections, title_prefix)`: Creates a new section for a group of elements.
- `_calculate_section_match(element, section_info, section)`: Calculates element-section match scores.
- `_ensure_unique_section_titles(sections)`: Ensures all section titles are unique.
- `_count_components(elements)`: Counts elements from each source response.

## Workflow

1. **Input Processing**:
   - The ResponseComparisonService receives the primary response from solution generation and evaluation metrics from response scoring.
   - The service checks for alternative response candidates or generates them if enabled.

2. **Diversity Calculation**:
   - The DiversityCalculator computes pairwise diversity scores between all response candidates.
   - It measures diversity across three dimensions: content, structure, and emphasis.
   - These scores quantify how different each candidate is from the others.

3. **Ensemble Diversification**:
   - The EnsembleDiversifier creates an optimal ensemble of response candidates.
   - It balances between quality and diversity using the alpha parameter (higher values favor quality).
   - Two algorithms are available: greedy diversification and maximal marginal relevance (MMR).
   - The primary response is always included in the ensemble.

4. **Quality-Diversity Optimization**:
   - The QualityDiversityOptimizer finds the optimal trade-off between quality and diversity.
   - It applies Pareto optimization to identify non-dominated components in quality-diversity space.
   - It selects optimal elements from across the ensemble and calculates component weights.
   - The primary response is given significant weight (at least 40%).

5. **Response Combination**:
   - The ResponseCombiner integrates the optimized components into a coherent response.
   - It restructures elements into sections, preserving the primary response's structure.
   - It assigns unassigned elements to existing sections or creates new sections as needed.
   - It ensures all sections have unique titles and balances element distribution.

6. **Output Generation**:
   - The service combines diversity metrics, ensemble metrics, and quality metrics.
   - It calculates the primary contribution ratio showing how much of the final response came from the primary candidate.
   - It tracks component weights and source information for transparency.

7. **Refinement Process** (if needed):
   - If refinement is requested, the service can re-process with updated context.
   - It tracks changes between previous and refined output for analysis.

## Key Algorithms

### Greedy Diversification
The greedy algorithm iteratively selects candidates that maximize marginal contribution to the ensemble:
1. Start with the primary response
2. For each subsequent selection, choose the candidate that maximizes:
   
   `score = quality * alpha + average_diversity * (1 - alpha)`

### Maximal Marginal Relevance (MMR)
The MMR algorithm balances relevance and novelty in each selection:
1. Start with the primary response
2. For each subsequent selection, choose the candidate that maximizes:
   
   `MMR = quality * alpha - max_similarity * (1 - alpha)`

### Pareto Optimization
The Pareto optimization identifies candidates that are not dominated in quality-diversity space:
1. A candidate is Pareto-optimal if no other candidate is better in both quality and diversity
2. The primary response is always included in the Pareto-optimal set

## Configuration Parameters

The Response Comparison stage can be configured with the following parameters:

- **alpha_parameter**: Trade-off between quality and diversity (0-1, higher values favor quality)
- **enable_alternative_generation**: Whether to generate alternatives when none are provided
- **max_alternatives**: Maximum number of alternatives to generate
- **ensemble_diversifier**: Configuration for the ensemble diversification component
  - **min_ensemble_size**: Minimum size of the diversified ensemble
  - **max_ensemble_size**: Maximum size of the diversified ensemble
  - **diversity_threshold**: Threshold for considering candidates diverse
  - **algorithm**: Diversification algorithm ("greedy" or "mmr")
- **diversity_calculator**: Configuration for the diversity calculation component
  - **content_weight**: Weight of content diversity in overall score
  - **structure_weight**: Weight of structure diversity in overall score
  - **emphasis_weight**: Weight of emphasis diversity in overall score
- **quality_diversity_optimizer**: Configuration for the quality-diversity optimization
  - **quality_weight**: Weight of quality in trade-off calculation
  - **diversity_weight**: Weight of diversity in trade-off calculation
  - **pareto_threshold**: Threshold for Pareto dominance comparison
- **response_combiner**: Configuration for the response combination
  - **max_elements**: Maximum number of elements in combined response
  - **max_sections**: Maximum number of sections in combined response
  - **preserve_section_order**: Whether to preserve the original section order

## Integration with Orchestrator

The Response Comparison stage implements the AbstractPipelineStage interface to seamlessly integrate with the metacognitive orchestrator:

- It exposes a standard process() method for comparison
- It supports a refine() method for re-evaluation after refinement
- It maintains metrics about its processing for monitoring
- It has a unique stage_id of "response_comparison"

## Example Usage

```python
# Extract the primary response and evaluation metrics from previous stages
primary_response = context.get("stage_outputs", {}).get("solution_generation", {})
evaluation_metrics = context.get("stage_outputs", {}).get("response_scoring", {})

# Perform response comparison
comparison_result = response_comparison_service.process(prompt, context)

# Access the combined response
combined_response = comparison_result.get("content", {})
primary_contribution = comparison_result.get("primary_contribution_ratio", 1.0)
diversity_metrics = comparison_result.get("diversity_metrics", {})

# Forward to threshold verification
verification_context = context.copy()
verification_context["stage_outputs"]["response_comparison"] = comparison_result
``` 