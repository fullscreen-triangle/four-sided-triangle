import pytest
from unittest.mock import MagicMock, patch

from app.core.stages.stage6_comparison.diversity_calculator import DiversityCalculator


@pytest.fixture
def calculator():
    """Create a DiversityCalculator instance."""
    return DiversityCalculator(config={
        "similarity_method": "embedding",
        "content_weight": 0.7,
        "structure_weight": 0.3,
        "embedding_model": "text-embedding-ada-002"
    })


@pytest.fixture
def responses():
    """Create a list of sample responses."""
    return [
        {
            "content": "Primary response content.",
            "sections": [{"title": "Introduction", "content": "Primary introduction."}],
            "metadata": {"quality_score": 0.85}
        },
        {
            "content": "Alternative response 1 content.",
            "sections": [{"title": "Alternative", "content": "Alternative content 1."}],
            "metadata": {"quality_score": 0.75}
        },
        {
            "content": "Alternative response 2 content.",
            "sections": [{"title": "Other", "content": "Other content 2."}],
            "metadata": {"quality_score": 0.80}
        }
    ]


class TestDiversityCalculator:
    
    def test_init(self, calculator):
        """Test initialization with default values."""
        assert calculator.config["similarity_method"] == "embedding"
        assert calculator.config["content_weight"] == 0.7
        assert calculator.config["structure_weight"] == 0.3
        assert calculator.config["embedding_model"] == "text-embedding-ada-002"
        
    @patch('app.core.stages.stage6_comparison.diversity_calculator.calculate_embedding_similarity')
    def test_calculate_response_similarity_embedding(self, mock_embedding_similarity, calculator, responses):
        """Test calculation of response similarity using embedding method."""
        # Mock the embedding similarity function to return a fixed value
        mock_embedding_similarity.return_value = 0.75
        
        # Calculate similarity between two responses
        similarity = calculator.calculate_response_similarity(responses[0], responses[1])
        
        # Check that embedding similarity was called with correct params
        mock_embedding_similarity.assert_called_once()
        
        # The similarity should match our mocked embedding similarity
        # with weighting applied (content_weight * embedding_similarity)
        expected_similarity = calculator.config["content_weight"] * 0.75 + \
                             calculator.config["structure_weight"] * calculator._calculate_structure_similarity(
                                 responses[0]["sections"], responses[1]["sections"]
                             )
        assert similarity == pytest.approx(expected_similarity, abs=0.01)
        
    @patch('app.core.stages.stage6_comparison.diversity_calculator.calculate_semantic_similarity')
    def test_calculate_response_similarity_semantic(self, mock_semantic_similarity, calculator, responses):
        """Test calculation of response similarity using semantic method."""
        # Set similarity method to semantic
        calculator.config["similarity_method"] = "semantic"
        
        # Mock the semantic similarity function to return a fixed value
        mock_semantic_similarity.return_value = 0.6
        
        # Calculate similarity between two responses
        similarity = calculator.calculate_response_similarity(responses[0], responses[2])
        
        # Check that semantic similarity was called with correct params
        mock_semantic_similarity.assert_called_once()
        
        # The similarity should match our mocked semantic similarity
        # with weighting applied (content_weight * semantic_similarity)
        expected_similarity = calculator.config["content_weight"] * 0.6 + \
                             calculator.config["structure_weight"] * calculator._calculate_structure_similarity(
                                 responses[0]["sections"], responses[2]["sections"]
                             )
        assert similarity == pytest.approx(expected_similarity, abs=0.01)
        
    def test_calculate_structure_similarity(self, calculator, responses):
        """Test calculation of structure similarity between responses."""
        # Test with different structures
        similarity = calculator._calculate_structure_similarity(
            responses[0]["sections"], responses[1]["sections"]
        )
        
        # Since sections are different, similarity should be low
        assert 0 <= similarity <= 1
        
        # Test with identical structures
        similarity = calculator._calculate_structure_similarity(
            responses[0]["sections"], responses[0]["sections"]
        )
        
        # Identical structures should have similarity 1.0
        assert similarity == 1.0
        
    def test_calculate_all_diversity_scores(self, calculator, responses):
        """Test calculation of all diversity scores between responses."""
        # Mock the calculate_response_similarity method
        calculator.calculate_response_similarity = MagicMock(side_effect=[0.8, 0.4, 0.6])
        
        # Calculate all diversity scores
        diversity_scores = calculator.calculate_all_diversity_scores(responses)
        
        # Check that we have scores for all pairs
        expected_pairs = {(0, 1), (0, 2), (1, 2)}
        assert set(diversity_scores.keys()) == expected_pairs
        
        # Check scores match our mocked values
        assert diversity_scores[(0, 1)] == 0.8
        assert diversity_scores[(0, 2)] == 0.4
        assert diversity_scores[(1, 2)] == 0.6
        
    def test_calculate_all_diversity_scores_empty(self, calculator):
        """Test calculation of diversity scores with empty response list."""
        # Calculate with empty list
        diversity_scores = calculator.calculate_all_diversity_scores([])
        
        # Should return an empty dict
        assert diversity_scores == {}
        
        # Calculate with single response
        diversity_scores = calculator.calculate_all_diversity_scores([{"content": "Single response"}])
        
        # No pairs to compare, so should return empty dict
        assert diversity_scores == {} 