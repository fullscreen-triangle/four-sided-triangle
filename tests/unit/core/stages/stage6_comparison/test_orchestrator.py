import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from app.core.stages.stage6_comparison.orchestrator import Stage6Orchestrator
from app.core.stages.stage6_comparison.diversity_calculator import DiversityCalculator
from app.core.stages.stage6_comparison.quality_calculator import QualityCalculator
from app.core.stages.stage6_comparison.ranking_calculator import RankingCalculator


@pytest.fixture
def mock_diversity_calculator():
    """Mock DiversityCalculator."""
    calculator = MagicMock(spec=DiversityCalculator)
    calculator.calculate_all_diversity_scores.return_value = {
        "diversity_scores": {
            "0_1": 0.3, "0_2": 0.5, "1_2": 0.4
        },
        "avg_diversity_score": 0.4
    }
    return calculator


@pytest.fixture
def mock_quality_calculator():
    """Mock QualityCalculator."""
    calculator = MagicMock(spec=QualityCalculator)
    calculator.calculate_quality_score.side_effect = lambda response, query: {
        "overall_score": 0.8,
        "structure_score": 0.75,
        "content_score": 0.85,
        "relevance_score": 0.8,
        "feedback": {
            "structure": "Good structure",
            "content": "Good content",
            "relevance": "Relevant to query"
        }
    }
    return calculator


@pytest.fixture
def mock_ranking_calculator():
    """Mock RankingCalculator."""
    calculator = MagicMock(spec=RankingCalculator)
    calculator.rank_responses.return_value = [
        {"response_id": 0, "rank": 1, "score": 0.85},
        {"response_id": 1, "rank": 2, "score": 0.75},
        {"response_id": 2, "rank": 3, "score": 0.65}
    ]
    return calculator


@pytest.fixture
def orchestrator(mock_diversity_calculator, mock_quality_calculator, mock_ranking_calculator):
    """Create a Stage6Orchestrator instance with mocked calculators."""
    config = {
        "diversity": {
            "similarity_method": "embedding",
            "content_weight": 0.7,
            "structure_weight": 0.3,
            "embedding_model": "all-MiniLM-L6-v2"
        },
        "quality": {
            "evaluation_model": "gpt-4o",
            "structure_weight": 0.3,
            "content_weight": 0.5,
            "relevance_weight": 0.2,
            "structure_criteria": ["organization", "formatting"],
            "content_criteria": ["accuracy", "completeness", "clarity"],
            "relevance_criteria": ["query_match", "usefulness"]
        },
        "ranking": {
            "quality_weight": 0.7,
            "diversity_weight": 0.3
        }
    }
    
    orchestrator = Stage6Orchestrator()
    # Inject mock calculators
    orchestrator._diversity_calculator = mock_diversity_calculator
    orchestrator._quality_calculator = mock_quality_calculator
    orchestrator._ranking_calculator = mock_ranking_calculator
    
    return orchestrator


@pytest.fixture
def responses():
    """Create sample responses."""
    return [
        {
            "response_id": 0,
            "content": "This is the first response.",
            "sections": [{"title": "Section 1", "content": "Content 1"}],
            "metadata": {}
        },
        {
            "response_id": 1,
            "content": "This is the second response.",
            "sections": [{"title": "Section 2", "content": "Content 2"}],
            "metadata": {}
        },
        {
            "response_id": 2, 
            "content": "This is the third response.",
            "sections": [{"title": "Section 3", "content": "Content 3"}],
            "metadata": {}
        }
    ]


class TestStage6Orchestrator:
    
    @pytest.mark.asyncio
    async def test_initialize(self):
        """Test initialization of the orchestrator."""
        config = {
            "diversity": {"similarity_method": "embedding"},
            "quality": {"evaluation_model": "gpt-4o"},
            "ranking": {"quality_weight": 0.7}
        }
        
        orchestrator = Stage6Orchestrator()
        await orchestrator.initialize(config)
        
        # Check that calculators were created with the correct config
        assert orchestrator._diversity_calculator is not None
        assert orchestrator._quality_calculator is not None
        assert orchestrator._ranking_calculator is not None
        
    @pytest.mark.asyncio
    async def test_process(self, orchestrator, responses):
        """Test the process method."""
        # Prepare input data
        input_data = {
            "responses": responses,
            "query": "Sample query"
        }
        context = {"session_id": "test_session"}
        
        # Process data
        result = await orchestrator.process(input_data, context)
        
        # Check that calculators were called
        orchestrator._diversity_calculator.calculate_all_diversity_scores.assert_called_once_with(responses)
        
        # Quality calculator should be called for each response
        assert orchestrator._quality_calculator.calculate_quality_score.call_count == 3
        
        # Check ranking was called
        orchestrator._ranking_calculator.rank_responses.assert_called_once()
        
        # Check result structure
        assert "ranked_responses" in result
        assert "diversity_analysis" in result
        assert "quality_scores" in result
        assert len(result["ranked_responses"]) == 3
        
    @pytest.mark.asyncio
    async def test_process_empty_responses(self, orchestrator):
        """Test process with empty responses."""
        input_data = {
            "responses": [],
            "query": "Sample query"
        }
        context = {"session_id": "test_session"}
        
        result = await orchestrator.process(input_data, context)
        
        # Check that diversity calculator was called with empty list
        orchestrator._diversity_calculator.calculate_all_diversity_scores.assert_called_once_with([])
        
        # Quality calculator should not be called
        orchestrator._quality_calculator.calculate_quality_score.assert_not_called()
        
        # Ranking calculator should be called with empty lists
        orchestrator._ranking_calculator.rank_responses.assert_called_once()
        
        # Check result
        assert result["ranked_responses"] == []
        assert "diversity_analysis" in result
        assert result["quality_scores"] == {}
        
    @pytest.mark.asyncio
    async def test_process_single_response(self, orchestrator):
        """Test process with a single response."""
        single_response = [{
            "response_id": 0,
            "content": "This is a response.",
            "sections": [{"title": "Section", "content": "Content"}],
            "metadata": {}
        }]
        
        input_data = {
            "responses": single_response,
            "query": "Sample query"
        }
        context = {"session_id": "test_session"}
        
        result = await orchestrator.process(input_data, context)
        
        # Check that diversity calculator was called
        orchestrator._diversity_calculator.calculate_all_diversity_scores.assert_called_once_with(single_response)
        
        # Quality calculator should be called once
        orchestrator._quality_calculator.calculate_quality_score.assert_called_once()
        
        # Check result
        assert len(result["ranked_responses"]) == 1
        assert result["ranked_responses"][0]["rank"] == 1
        
    @pytest.mark.asyncio
    async def test_cleanup(self, orchestrator):
        """Test cleanup method."""
        await orchestrator.cleanup()
        # Currently nothing to test in cleanup, but method needs to exist
        # Future implementation might add actual cleanup tasks
        
    def test_metadata(self, orchestrator):
        """Test metadata property."""
        metadata = orchestrator.metadata
        assert "name" in metadata
        assert metadata["name"] == "stage6_comparison"
        assert "description" in metadata 