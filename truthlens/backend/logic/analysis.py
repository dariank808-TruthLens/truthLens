"""Analysis computation logic for scoring and credibility breakdown."""
from typing import List, Optional, Dict, Any


def compute_breakdown(
    fact_checks: List[Dict[str, Any]],
    fallacies: List[Dict[str, Any]],
    ai_check: Optional[Dict[str, Any]] = None
) -> Dict[str, Optional[float]]:
    """Compute aggregated statistical scores from analysis details.
    
    Combines fact-check, fallacy, and AI-generation scores into a single
    overall credibility score. Uses inverse scoring for fallacies and AI detection.
    
    Args:
        fact_checks: List of fact-check documents, each with 'score' field (0.0-1.0)
        fallacies: List of fallacy documents, each with 'severity' field (0.0-1.0)
        ai_check: Optional AI-check document with 'score' field (0.0-1.0)
    
    Returns:
        Dictionary with breakdown scores:
            - fact_check_score: Average of fact-check scores (None if no fact-checks)
            - logical_fallacy_score: 1.0 - avg fallacy severity (None if no fallacies)
            - ai_generation_score: AI likelihood score (None if no AI check)
            - overall_credibility_score: Weighted average of enabled checks
    """
    fact_score = None
    fallacy_score = None
    ai_score = None
    
    # Compute average fact-check score
    if fact_checks:
        fact_scores = [fc.get("score", 0.5) for fc in fact_checks if "score" in fc]
        if fact_scores:
            fact_score = sum(fact_scores) / len(fact_scores)
    
    # Compute inverse fallacy severity (lower severity = higher credibility score)
    if fallacies:
        fallacy_severities = [f.get("severity", 0.5) for f in fallacies if "severity" in f]
        if fallacy_severities:
            avg_severity = sum(fallacy_severities) / len(fallacy_severities)
            fallacy_score = 1.0 - avg_severity
    
    # Extract AI detection score
    if ai_check:
        ai_score = ai_check.get("score", 0.0)
    
    # Compute overall credibility as weighted average of enabled checks
    scores = []
    if fact_score is not None:
        scores.append(fact_score)
    if fallacy_score is not None:
        scores.append(fallacy_score)
    if ai_score is not None:
        # Invert AI score: high AI likelihood = lower credibility
        scores.append(1.0 - ai_score)
    
    overall_score = None
    if scores:
        overall_score = sum(scores) / len(scores)
    
    return {
        "fact_check_score": fact_score,
        "logical_fallacy_score": fallacy_score,
        "ai_generation_score": ai_score,
        "overall_credibility_score": overall_score,
    }
