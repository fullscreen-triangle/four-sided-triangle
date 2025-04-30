import pytest
from unittest.mock import MagicMock, patch
import copy

from app.core.stages.stage6_comparison.response_comparison_service import ResponseComparisonService
from app.core.stages.stage6_comparison.ensemble_diversifier import EnsembleDiversifier
from app.core.stages.stage6_comparison.diversity_calculator import DiversityCalculator
from app.core.stages.stage6_comparison.quality_diversity_optimizer import QualityDiversityOptimizer
from app.core.stages.stage6_comparison.response_combiner import ResponseCombiner


@pytest.fixture
def service():
    """Create a ResponseComparisonService instance with mocked dependencies."""
    ensemble_diversifier = MagicMock(spec=EnsembleDiversifier)
    diversity_calculator = MagicMock(spec=DiversityCalculator)
    quality_diversity_optimizer = MagicMock(spec=QualityDiversityOptimizer)
    response_combiner = MagicMock(spec=ResponseCombiner)
    
    service = ResponseComparisonService(
        ensemble_diversifier=ensemble_diversifier,
        diversity_calculator=diversity_calculator,
        quality_diversity_optimizer=quality_diversity_optimizer,
        response_combiner=response_combiner
    )
    
    return service


@pytest.fixture
def primary_response():
    """Create a sample primary response."""
    return {
        "content": "This is the primary response.",
        "sections": [{"title": "Introduction", "content": "This is an introduction."}],
        "metadata": {"quality_score": 0.85}
    }


@pytest.fixture
def alternative_responses():
    """Create sample alternative responses."""
    return [
        {
            "content": "This is alternative response 1.",
            "sections": [{"title": "Alternative", "content": "Alternative content."}],
            "metadata": {"quality_score": 0.75}
        },
        {
            "content": "This is alternative response 2.",
            "sections": [{"title": "Other", "content": "Other content."}],
            "metadata": {"quality_score": 0.80}
        }
    ]


@pytest.fixture
def evaluation_metrics():
    """Create sample evaluation metrics."""
    return {
        "overall_quality": 0.85,
        "coherence": 0.90,
        "relevance": 0.82,
        "accuracy": 0.88
    }


@pytest.fixture
def context(primary_response, alternative_responses, evaluation_metrics):
    """Create a sample context with primary response, alternative responses, and evaluation metrics."""
    return {
        "stage_outputs": {
            "solution_generation": primary_response,
            "response_scoring": evaluation_metrics,
            "alternative_responses": alternative_responses
        }
    }


class TestResponseComparisonService:
    
    def test_init(self, service):
        """Test initialization of ResponseComparisonService."""
        assert service.ensemble_diversifier is not None
        assert service.diversity_calculator is not None
        assert service.quality_diversity_optimizer is not None
        assert service.response_combiner is not None
        assert service.config is not None
        
    def test_process_with_alternatives(self, service, context, primary_response, alternative_responses, evaluation_metrics):
        """Test processing with alternative responses available."""
        # Configure mock behavior
        service.diversity_calculator.calculate_diversity.return_value = {"diversity_scores": {(0, 1): 0.7, (0, 2): 0.6, (1, 2): 0.5}}
        service.ensemble_diversifier.diversify.return_value = [primary_response, alternative_responses[0]]
        service.quality_diversity_optimizer.optimize.return_value = {"optimized_components": [
            {"content": "Optimized content", "source_index": 0},
            {"content": "Other optimized content", "source_index": 1}
        ]}
        service.quality_diversity_optimizer.get_trade_off_metrics.return_value = {"quality_score": 0.85, "diversity_score": 0.7}
        service.response_combiner.combine.return_value = {
            "content": "Combined response",
            "sections": [{"title": "Combined", "content": "Combined content"}],
            "metadata": {"primary_contribution_ratio": 0.7}
        }
        
        # Run process method
        prompt = "Test prompt"
        result = service.process(prompt, context)
        
        # Verify expected interactions with dependencies
        service.diversity_calculator.calculate_diversity.assert_called_once()
        service.ensemble_diversifier.diversify.assert_called_once()
        service.quality_diversity_optimizer.optimize.assert_called_once()
        service.response_combiner.combine.assert_called_once()
        
        # Check result structure and content
        assert "content" in result
        assert "metadata" in result
        assert "diversity_metrics" in result
        assert "ensemble_metrics" in result
        assert "primary_contribution_ratio" in result
        assert result["content"] == "Combined response"
        assert result["primary_contribution_ratio"] == 0.7
        
    def test_process_without_alternatives(self, service, context, primary_response, evaluation_metrics):
        """Test processing with no alternative responses."""
        # Configure context without alternatives
        context_without_alternatives = copy.deepcopy(context)
        context_without_alternatives["stage_outputs"].pop("alternative_responses", None)
        
        # Set config to not generate alternatives
        service.config["enable_alternative_generation"] = False
        
        # Run process method
        prompt = "Test prompt"
        result = service.process(prompt, context_without_alternatives)
        
        # Check that result contains the primary response with some additional metadata
        assert result["content"] == primary_response["content"]
        assert result["primary_contribution_ratio"] == 1.0
        assert "diversity_metrics" in result
        assert "ensemble_metrics" in result
        
    @patch.object(ResponseComparisonService, "_generate_alternative_responses")
    def test_process_with_alternative_generation(self, mock_generate, service, context, primary_response, evaluation_metrics):
        """Test processing with alternative response generation."""
        # Configure context without alternatives
        context_without_alternatives = copy.deepcopy(context)
        context_without_alternatives["stage_outputs"].pop("alternative_responses", None)
        
        # Set config to generate alternatives
        service.config["enable_alternative_generation"] = True
        service.config["max_alternatives"] = 2
        
        # Configure mock behavior for generation
        generated_alternatives = [
            {"content": "Generated alternative 1", "metadata": {"quality_score": 0.75}},
            {"content": "Generated alternative 2", "metadata": {"quality_score": 0.70}}
        ]
        mock_generate.return_value = generated_alternatives
        
        # Configure other mocks
        service.diversity_calculator.calculate_diversity.return_value = {"diversity_scores": {(0, 1): 0.7, (0, 2): 0.6, (1, 2): 0.5}}
        service.ensemble_diversifier.diversify.return_value = [primary_response, generated_alternatives[0]]
        service.quality_diversity_optimizer.optimize.return_value = {"optimized_components": [
            {"content": "Optimized content", "source_index": 0},
            {"content": "Other optimized content", "source_index": 1}
        ]}
        service.quality_diversity_optimizer.get_trade_off_metrics.return_value = {"quality_score": 0.82, "diversity_score": 0.65}
        service.response_combiner.combine.return_value = {
            "content": "Combined response from generated alternatives",
            "sections": [{"title": "Combined", "content": "Combined content"}],
            "metadata": {"primary_contribution_ratio": 0.6}
        }
        
        # Run process method
        prompt = "Test prompt"
        result = service.process(prompt, context_without_alternatives)
        
        # Verify generation was called
        mock_generate.assert_called_once_with(primary_response, context_without_alternatives, 2)
        
        # Verify expected interactions with dependencies
        service.diversity_calculator.calculate_diversity.assert_called_once()
        service.ensemble_diversifier.diversify.assert_called_once()
        service.quality_diversity_optimizer.optimize.assert_called_once()
        service.response_combiner.combine.assert_called_once()
        
        # Check result
        assert result["content"] == "Combined response from generated alternatives"
        assert result["primary_contribution_ratio"] == 0.6
        
    def test_refine(self, service, primary_response, evaluation_metrics):
        """Test refinement of a previous output."""
        # Configure previous output
        previous_output = {
            "content": "Previous combined response",
            "sections": [{"title": "Previous", "content": "Previous content"}],
            "metadata": {"primary_contribution_ratio": 0.8}
        }
        
        # Configure mock behavior for refinement
        service.diversity_calculator.calculate_diversity.return_value = {"diversity_scores": {(0, 1): 0.3}}
        service.ensemble_diversifier.diversify.return_value = [primary_response]
        service.quality_diversity_optimizer.optimize.return_value = {"optimized_components": [
            {"content": "Refined content", "source_index": 0}
        ]}
        service.quality_diversity_optimizer.get_trade_off_metrics.return_value = {"quality_score": 0.90, "diversity_score": 0.4}
        service.response_combiner.combine.return_value = {
            "content": "Refined combined response",
            "sections": [{"title": "Refined", "content": "Refined content"}],
            "metadata": {"primary_contribution_ratio": 0.9}
        }
        
        # Create context for refinement
        refinement_context = {
            "stage_outputs": {
                "solution_generation": primary_response,
                "response_scoring": evaluation_metrics,
                "refinement_feedback": {"improve_clarity": True}
            }
        }
        
        # Run refinement
        refinement_prompt = "Improve clarity"
        result = service.refine(refinement_prompt, refinement_context, previous_output)
        
        # Check result contains refinement metadata
        assert result["content"] == "Refined combined response"
        assert "refinement_changes" in result
        assert "previous_output" in result["refinement_changes"]
        assert "refined_output" in result["refinement_changes"]
        
    def test_track_refinement_changes(self, service):
        """Test tracking of refinement changes."""
        previous_output = {
            "content": "Original content",
            "sections": [{"title": "Original", "content": "Original section content"}]
        }
        
        refined_output = {
            "content": "Refined content",
            "sections": [{"title": "Refined", "content": "Refined section content"}]
        }
        
        changes = service._track_refinement_changes(previous_output, refined_output)
        
        assert "previous_output" in changes
        assert "refined_output" in changes
        assert "content_diff" in changes
        assert "section_changes" in changes 