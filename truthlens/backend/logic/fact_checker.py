"""Fact-check claims against external APIs.

Uses Google Fact Check Tools API when GOOGLE_FACT_CHECK_API_KEY is set.
Otherwise returns placeholder results for prototype/demo.
"""
from __future__ import annotations

import os
import re
from typing import List, Dict, Any, Optional

from .utils import make_id


def extract_claims(text: str, max_claims: int = 10) -> List[str]:
    """Extract potential factual claims from text for fact-checking.

    Simple heuristic: sentences with numbers, percentages, or
    reporting verbs (said, reported, claimed, etc.)
    """
    if not text or not text.strip():
        return []

    sentences = re.split(r"[.!?]+", text)
    claims = []
    for s in sentences:
        s = s.strip()
        if len(s) < 20:
            continue
        # Prefer sentences that look like factual claims
        has_number = bool(re.search(r"\d+", s))
        has_reporting = bool(re.search(r"\b(said|reported|claimed|stated|according to|announced)\b", s, re.I))
        has_percent = "%" in s or "percent" in s.lower()
        if has_number or has_reporting or has_percent:
            claims.append(s[:500])  # cap length
        if len(claims) >= max_claims:
            break
    return claims[:max_claims]


def fact_check_claims(
    claims: List[str],
    api_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Fact-check a list of claims.

    If api_key is set, queries Google Fact Check Tools API.
    Otherwise returns placeholder results for prototype.
    """
    api_key = api_key or os.getenv("GOOGLE_FACT_CHECK_API_KEY")
    results = []

    for claim in claims:
        if api_key:
            fc = _query_google_fact_check(claim, api_key)
        else:
            fc = _placeholder_fact_check(claim)
        results.append(fc)

    return results


def _placeholder_fact_check(statement: str) -> Dict[str, Any]:
    """Return placeholder fact-check when API is not configured."""
    return {
        "id": make_id("fact"),
        "statement": statement[:500],
        "score": 0.5,  # neutral when unverified
        "sources_for": [],
        "sources_against": [],
        "note": "Fact-check API not configured. Set GOOGLE_FACT_CHECK_API_KEY for real verification.",
    }


def _query_google_fact_check(claim: str, api_key: str) -> Dict[str, Any]:
    """Query Google Fact Check Tools API."""
    try:
        import httpx
        url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        params = {"key": api_key, "query": claim[:500]}
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, params=params)
        if resp.status_code != 200:
            return _placeholder_fact_check(claim)

        data = resp.json()
        reviews = data.get("claims", [])
        if not reviews:
            return _placeholder_fact_check(claim)

        # Use first matching claim review
        r = reviews[0]
        claim_review = r.get("claimReview", [{}])[0] if r.get("claimReview") else {}
        publisher = claim_review.get("publisher", {})
        title = publisher.get("name", "Unknown")
        url_val = claim_review.get("url", "")

        # Map rating to score (simplified)
        rating = (claim_review.get("textualRating") or "").lower()
        score = 0.5
        if any(w in rating for w in ["true", "correct", "accurate"]):
            score = 0.8
        elif any(w in rating for w in ["false", "incorrect", "fake"]):
            score = 0.2
        elif any(w in rating for w in ["misleading", "partially"]):
            score = 0.4

        return {
            "id": make_id("fact"),
            "statement": claim[:500],
            "score": score,
            "sources_for": [{"title": title, "url": url_val, "score": score}] if score >= 0.5 else [],
            "sources_against": [{"title": title, "url": url_val, "score": 1 - score}] if score < 0.5 else [],
            "note": claim_review.get("title") or rating or None,
        }
    except Exception:
        return _placeholder_fact_check(claim)
