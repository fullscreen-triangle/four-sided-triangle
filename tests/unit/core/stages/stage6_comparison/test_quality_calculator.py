import pytest
from unittest.mock import MagicMock, patch

from app.core.stages.stage6_comparison.quality_calculator import QualityCalculator


@pytest.fixture
def calculator():
    """Create a QualityCalculator instance."""
    return QualityCalculator(config={
        "evaluation_model": "gpt-4o",
        "structure_weight": 0.3,
        "content_weight": 0.5,
        "relevance_weight": 0.2,
        "structure_criteria": ["organization", "formatting"],
        "content_criteria": ["accuracy", "completeness", "clarity"],
        "relevance_criteria": ["query_match", "usefulness"]
    })


@pytest.fixture
def response():
    """Create a sample response."""
    return {
        "content": "This is a sample response that addresses the query.",
        "sections": [
            {"title": "Introduction", "content": "Introduction content."},
            {"title": "Main Points", "content": "Main points content."},
            {"title": "Conclusion", "content": "Conclusion content."}
        ],
        "metadata": {}
    }


@pytest.fixture
def query():
    """Create a sample query."""
    return "What are the main points to consider?"


class TestQualityCalculator:
    
    def test_init(self, calculator):
        """Test initialization with default values."""
        assert calculator.config["evaluation_model"] == "gpt-4o"
        assert calculator.config["structure_weight"] == 0.3
        assert calculator.config["content_weight"] == 0.5
        assert calculator.config["relevance_weight"] == 0.2
        assert "structure_criteria" in calculator.config
        assert "content_criteria" in calculator.config
        assert "relevance_criteria" in calculator.config
        
    @patch('app.core.stages.stage6_comparison.quality_calculator.evaluate_response_structure')
    def test_evaluate_structure(self, mock_evaluate_structure, calculator, response):
        """Test structure evaluation."""
        # Mock the structure evaluation function
        mock_evaluate_structure.return_value = {"score": 0.85, "feedback": "Good structure"}
        
        # Evaluate the structure
        structure_result = calculator._evaluate_structure(response)
        
        # Check that evaluation was called with correct params
        mock_evaluate_structure.assert_called_once_with(
            response, calculator.config["structure_criteria"]
        )
        
        # Check that the result matches our mock
        assert structure_result["score"] == 0.85
        assert structure_result["feedback"] == "Good structure"
        
    @patch('app.core.stages.stage6_comparison.quality_calculator.evaluate_response_content')
    def test_evaluate_content(self, mock_evaluate_content, calculator, response):
        """Test content evaluation."""
        # Mock the content evaluation function
        mock_evaluate_content.return_value = {"score": 0.78, "feedback": "Good content"}
        
        # Evaluate the content
        content_result = calculator._evaluate_content(response)
        
        # Check that evaluation was called with correct params
        mock_evaluate_content.assert_called_once_with(
            response, calculator.config["content_criteria"], calculator.config["evaluation_model"]
        )
        
        # Check that the result matches our mock
        assert content_result["score"] == 0.78
        assert content_result["feedback"] == "Good content"
        
    @patch('app.core.stages.stage6_comparison.quality_calculator.evaluate_response_relevance')
    def test_evaluate_relevance(self, mock_evaluate_relevance, calculator, response, query):
        """Test relevance evaluation."""
        # Mock the relevance evaluation function
        mock_evaluate_relevance.return_value = {"score": 0.92, "feedback": "Very relevant"}
        
        # Evaluate the relevance
        relevance_result = calculator._evaluate_relevance(response, query)
        
        # Check that evaluation was called with correct params
        mock_evaluate_relevance.assert_called_once_with(
            response, query, calculator.config["relevance_criteria"], calculator.config["evaluation_model"]
        )
        
        # Check that the result matches our mock
        assert relevance_result["score"] == 0.92
        assert relevance_result["feedback"] == "Very relevant"
        
    def test_calculate_overall_quality(self, calculator):
        """Test calculation of overall quality score."""
        # Define individual scores
        structure_score = 0.8
        content_score = 0.9
        relevance_score = 0.7
        
        # Calculate overall quality
        overall_score = calculator._calculate_overall_quality(structure_score, content_score, relevance_score)
        
        # Expected weighted average
        expected_score = (
            structure_score * calculator.config["structure_weight"] +
            content_score * calculator.config["content_weight"] +
            relevance_score * calculator.config["relevance_weight"]
        )
        
        assert overall_score == expected_score
        
    @patch.object(QualityCalculator, '_evaluate_structure')
    @patch.object(QualityCalculator, '_evaluate_content')
    @patch.object(QualityCalculator, '_evaluate_relevance')
    @patch.object(QualityCalculator, '_calculate_overall_quality')
    def test_calculate_quality_score(self, mock_calc_overall, mock_eval_relevance, 
                                    mock_eval_content, mock_eval_structure, 
                                    calculator, response, query):
        """Test calculation of quality score for a response."""
        # Mock evaluation functions
        mock_eval_structure.return_value = {"score": 0.8, "feedback": "Good structure"}
        mock_eval_content.return_value = {"score": 0.9, "feedback": "Great content"}
        mock_eval_relevance.return_value = {"score": 0.7, "feedback": "Relevant enough"}
        mock_calc_overall.return_value = 0.83
        
        # Calculate quality score
        score_result = calculator.calculate_quality_score(response, query)
        
        # Verify all methods were called
        mock_eval_structure.assert_called_once_with(response)
        mock_eval_content.assert_called_once_with(response)
        mock_eval_relevance.assert_called_once_with(response, query)
        mock_calc_overall.assert_called_once_with(0.8, 0.9, 0.7)
        
        # Check that score result contains expected values
        assert score_result["overall_score"] == 0.83
        assert score_result["structure_score"] == 0.8
        assert score_result["content_score"] == 0.9
        assert score_result["relevance_score"] == 0.7
        assert score_result["feedback"]["structure"] == "Good structure"
        assert score_result["feedback"]["content"] == "Great content"
        assert score_result["feedback"]["relevance"] == "Relevant enough" 