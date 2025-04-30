import pytest
from unittest.mock import MagicMock

from app.core.stages.stage6_comparison.ensemble_diversifier import EnsembleDiversifier


@pytest.fixture
def diversifier():
    """Create an EnsembleDiversifier instance."""
    return EnsembleDiversifier(config={
        "diversification_method": "greedy",
        "min_responses": 2,
        "max_responses": 4,
        "similarity_threshold": 0.7,
        "alpha": 0.5  # Balance between quality and diversity
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
        },
        {
            "content": "Alternative response 3 content.",
            "sections": [{"title": "Final", "content": "Final content 3."}],
            "metadata": {"quality_score": 0.60}
        }
    ]


@pytest.fixture
def diversity_scores():
    """Create sample diversity scores between pairs of responses."""
    # Format: {(response_index_1, response_index_2): similarity_score}
    return {
        (0, 1): 0.8,  # Primary and Alt 1 are quite similar
        (0, 2): 0.4,  # Primary and Alt 2 are diverse
        (0, 3): 0.3,  # Primary and Alt 3 are very diverse
        (1, 2): 0.5,  # Alt 1 and Alt 2 moderately diverse
        (1, 3): 0.6,  # Alt 1 and Alt 3 moderately diverse
        (2, 3): 0.7   # Alt 2 and Alt 3 somewhat similar
    }


class TestEnsembleDiversifier:
    
    def test_init(self, diversifier):
        """Test initialization with default values."""
        assert diversifier.config["diversification_method"] == "greedy"
        assert diversifier.config["min_responses"] == 2
        assert diversifier.config["max_responses"] == 4
        assert diversifier.config["similarity_threshold"] == 0.7
        assert diversifier.config["alpha"] == 0.5
        
    def test_diversify_greedy_method(self, diversifier, responses, diversity_scores):
        """Test greedy diversification method."""
        # Configure the diversifier
        diversifier.config["diversification_method"] = "greedy"
        
        # Call diversify method
        diversified_ensemble = diversifier.diversify(responses, diversity_scores)
        
        # Check that we get expected number of responses
        assert 2 <= len(diversified_ensemble) <= 4
        
        # Check that primary response is always included
        assert responses[0] in diversified_ensemble
        
        # Verify that the ensemble contains diverse responses
        if len(diversified_ensemble) > 1:
            # The second response should be the one most diverse from primary
            # In our sample data, response 3 is most diverse from primary
            assert responses[3] in diversified_ensemble
            
    def test_diversify_mmr_method(self, diversifier, responses, diversity_scores):
        """Test Maximal Marginal Relevance (MMR) diversification method."""
        # Configure the diversifier to use MMR
        diversifier.config["diversification_method"] = "mmr"
        diversifier.config["alpha"] = 0.7  # Favor quality over diversity
        
        # Call diversify method
        diversified_ensemble = diversifier.diversify(responses, diversity_scores)
        
        # Check that we get expected number of responses
        assert 2 <= len(diversified_ensemble) <= 4
        
        # Check that primary response is always included
        assert responses[0] in diversified_ensemble
        
        # Verify that with high alpha (quality preference), response 2 should be included
        # as it has the second-highest quality score
        if len(diversified_ensemble) > 1:
            assert responses[2] in diversified_ensemble
            
    def test_diversify_with_min_responses(self, diversifier, responses, diversity_scores):
        """Test that diversify respects minimum response count."""
        # Set minimum responses to 3
        diversifier.config["min_responses"] = 3
        
        # Call diversify method
        diversified_ensemble = diversifier.diversify(responses, diversity_scores)
        
        # Check that we get at least min_responses
        assert len(diversified_ensemble) >= 3
        
    def test_diversify_with_max_responses(self, diversifier, responses, diversity_scores):
        """Test that diversify respects maximum response count."""
        # Set maximum responses to 2
        diversifier.config["max_responses"] = 2
        
        # Call diversify method
        diversified_ensemble = diversifier.diversify(responses, diversity_scores)
        
        # Check that we get at most max_responses
        assert len(diversified_ensemble) <= 2
        
    def test_diversify_with_threshold(self, diversifier, responses, diversity_scores):
        """Test that diversify respects similarity threshold."""
        # Set a high similarity threshold to only include very different responses
        diversifier.config["similarity_threshold"] = 0.4
        
        # Call diversify method
        diversified_ensemble = diversifier.diversify(responses, diversity_scores)
        
        # Check that highly similar responses aren't both included
        # Based on our diversity scores, responses 0 and 1 are very similar (0.8)
        # So if response 0 is included, response 1 should not be
        if responses[0] in diversified_ensemble:
            assert responses[1] not in diversified_ensemble
            
    def test_diversify_with_no_diversity_scores(self, diversifier, responses):
        """Test diversification when no diversity scores are provided."""
        # Call diversify with empty diversity scores
        diversified_ensemble = diversifier.diversify(responses, {})
        
        # Should fall back to quality-based ranking only
        assert len(diversified_ensemble) >= 1
        assert responses[0] in diversified_ensemble  # Primary response should be included
        
        # When only using quality scores, the top N responses by quality should be included
        # Since max_responses is 4 and we have 4 responses, all should be included
        # but ordered by quality
        if len(diversified_ensemble) == 4:
            # Check that ordering respects quality scores
            quality_scores = [resp["metadata"]["quality_score"] for resp in diversified_ensemble]
            assert all(quality_scores[i] >= quality_scores[i+1] for i in range(len(quality_scores)-1)) 