"""Tests for backend.logic.analysis module."""
import pytest
from backend.logic.analysis import compute_breakdown


class TestComputeBreakdown:
    """Test analysis scoring and breakdown computation."""

    def test_empty_inputs(self):
        """compute_breakdown() handles empty lists gracefully."""
        result = compute_breakdown([], [], None)
        
        assert result["fact_check_score"] is None
        assert result["logical_fallacy_score"] is None
        assert result["ai_generation_score"] is None
        assert result["overall_credibility_score"] is None

    def test_fact_check_score_only(self):
        """compute_breakdown() computes average fact-check score."""
        fact_checks = [
            {"score": 0.8},
            {"score": 0.9},
            {"score": 0.7},
        ]
        
        result = compute_breakdown(fact_checks, [], None)
        
        assert result["fact_check_score"] == pytest.approx(0.8)
        assert result["logical_fallacy_score"] is None
        assert result["ai_generation_score"] is None
        assert result["overall_credibility_score"] == pytest.approx(0.8)

    def test_fallacy_score_inverse(self):
        """compute_breakdown() inverts fallacy severity (1.0 - severity)."""
        fallacies = [
            {"severity": 0.2},  # low severity -> high credibility
            {"severity": 0.4},
        ]
        
        result = compute_breakdown([], fallacies, None)
        
        # Average severity = 0.3, inverted = 1.0 - 0.3 = 0.7
        assert result["logical_fallacy_score"] == pytest.approx(0.7)
        assert result["fact_check_score"] is None

    def test_ai_generation_score(self):
        """compute_breakdown() extracts AI generation score."""
        ai_check = {"score": 0.25}  # 25% likely AI-generated
        
        result = compute_breakdown([], [], ai_check)
        
        assert result["ai_generation_score"] == pytest.approx(0.25)
        # Overall score inverts AI: 1.0 - 0.25 = 0.75
        assert result["overall_credibility_score"] == pytest.approx(0.75)

    def test_all_scores_combined(self):
        """compute_breakdown() combines all three scores with equal weight."""
        fact_checks = [{"score": 0.6}]
        fallacies = [{"severity": 0.4}]  # inverted: 0.6
        ai_check = {"score": 0.2}  # inverted: 0.8
        
        result = compute_breakdown(fact_checks, fallacies, ai_check)
        
        assert result["fact_check_score"] == pytest.approx(0.6)
        assert result["logical_fallacy_score"] == pytest.approx(0.6)
        assert result["ai_generation_score"] == pytest.approx(0.2)
        # Overall = (0.6 + 0.6 + 0.8) / 3 = 0.667
        assert result["overall_credibility_score"] == pytest.approx(0.667, abs=0.01)

    def test_missing_score_fields(self):
        """compute_breakdown() skips items without required score fields."""
        fact_checks = [
            {"score": 0.8},
            {"statement": "no score here"},  # missing score
            {"score": 0.9},
        ]
        fallacies = [{"severity": 0.3}]
        ai_check = {"score": 0.1}
        
        result = compute_breakdown(fact_checks, fallacies, ai_check)
        
        # Should average only fact_checks with scores: (0.8 + 0.9) / 2 = 0.85
        assert result["fact_check_score"] == pytest.approx(0.85)

    def test_boundary_scores(self):
        """compute_breakdown() handles boundary scores (0.0, 1.0)."""
        fact_checks = [{"score": 0.0}, {"score": 1.0}]
        fallacies = [{"severity": 0.0}, {"severity": 1.0}]
        ai_check = {"score": 0.0}
        
        result = compute_breakdown(fact_checks, fallacies, ai_check)
        
        assert result["fact_check_score"] == pytest.approx(0.5)
        assert result["logical_fallacy_score"] == pytest.approx(0.5)
        assert result["ai_generation_score"] == pytest.approx(0.0)

    def test_single_item_each(self):
        """compute_breakdown() works with single items."""
        fact_checks = [{"score": 0.75}]
        fallacies = [{"severity": 0.25}]
        ai_check = {"score": 0.1}
        
        result = compute_breakdown(fact_checks, fallacies, ai_check)
        
        assert result["fact_check_score"] == pytest.approx(0.75)
        assert result["logical_fallacy_score"] == pytest.approx(0.75)
        assert result["ai_generation_score"] == pytest.approx(0.1)
