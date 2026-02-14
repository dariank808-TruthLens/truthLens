"""Tests for fixture data loading."""
import pytest
from backend.logic.fixtures import load_fixture_analysis


class TestLoadFixture:
    """Test fixture data loading."""

    def test_load_fixture_analysis_returns_dict(self):
        """load_fixture_analysis() returns a dict when file exists."""
        result = load_fixture_analysis()
        
        # If fixture file exists, should return dict
        if result is not None:
            assert isinstance(result, dict)
            assert "id" in result
            assert "upload_id" in result

    def test_loaded_fixture_structure(self):
        """Loaded fixture has expected structure."""
        fixture = load_fixture_analysis()
        
        if fixture is not None:
            # Expected top-level fields
            assert "status" in fixture
            assert "fact_checks" in fixture or "fallacies" in fixture or "ai_check" in fixture
            
            # Status should be valid
            assert fixture.get("status") in ["pending", "ready", "error"]

    def test_fixture_breakdown_scores(self):
        """Fixture breakdown contains valid scores."""
        fixture = load_fixture_analysis()
        
        if fixture and "breakdown" in fixture:
            breakdown = fixture["breakdown"]
            
            # All scores should be None or float between 0 and 1
            for key in ["fact_check_score", "logical_fallacy_score", 
                       "ai_generation_score", "overall_credibility_score"]:
                if key in breakdown:
                    score = breakdown[key]
                    assert score is None or (isinstance(score, (int, float)) and 0.0 <= score <= 1.0)

    def test_fixture_fact_checks_structure(self):
        """Fact checks in fixture have valid structure."""
        fixture = load_fixture_analysis()
        
        if fixture and "fact_checks" in fixture:
            fact_checks = fixture["fact_checks"]
            
            for fc in fact_checks:
                assert "statement" in fc
                if "score" in fc:
                    assert isinstance(fc["score"], (int, float))
                    assert 0.0 <= fc["score"] <= 1.0

    def test_fixture_fallacies_structure(self):
        """Fallacies in fixture have valid structure."""
        fixture = load_fixture_analysis()
        
        if fixture and "fallacies" in fixture:
            fallacies = fixture["fallacies"]
            
            for f in fallacies:
                assert "name" in f
                assert "statement" in f
                if "severity" in f:
                    assert isinstance(f["severity"], (int, float))
                    assert 0.0 <= f["severity"] <= 1.0

    def test_fixture_ai_check_structure(self):
        """AI check in fixture has valid structure."""
        fixture = load_fixture_analysis()
        
        if fixture and "ai_check" in fixture:
            ai_check = fixture["ai_check"]
            
            assert "is_ai" in ai_check
            assert isinstance(ai_check["is_ai"], bool)
            
            if "score" in ai_check:
                score = ai_check["score"]
                assert isinstance(score, (int, float))
                assert 0.0 <= score <= 1.0
