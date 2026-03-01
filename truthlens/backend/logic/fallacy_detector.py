"""Rule-based logical fallacy detection for text.

Detects common fallacies via pattern matching. Prototype-friendly;
can be replaced with ML models later.
"""
from __future__ import annotations

import re
from typing import List, Dict, Any

from .utils import make_id


# Patterns: (regex, fallacy_name, default_severity 0.0-1.0)
_FALLACY_PATTERNS = [
    # Strawman: misrepresenting opponent's argument
    (r"\b(they|he|she|them)\s+(want|wish|hope|try)\s+to\s+(ban|eliminate|destroy|remove)\s+(all|every)\b", "Strawman", 0.7),
    (r"\b(no one|nobody)\s+(really|actually)\s+(believes|thinks|wants)\b", "Strawman", 0.6),
    # Ad hominem: attacking person instead of argument
    (r"\b(he|she|they)\s+(is|are)\s+(just|simply)\s+(a|an)\s+\w+\s+(so|therefore)\b", "Ad Hominem", 0.7),
    (r"\b(typical|classic)\s+(liberal|conservative|democrat|republican)\b", "Ad Hominem", 0.6),
    (r"\b(obviously|clearly)\s+(he|she|they)\s+(doesn't|don't)\s+understand\b", "Ad Hominem", 0.5),
    # Bandwagon / appeal to popularity
    (r"\beveryone\s+(knows|agrees|believes)\s+(that|this)\b", "Bandwagon", 0.6),
    (r"\ball\s+(real|true|smart)\s+(people|experts)\s+(know|agree)\b", "Bandwagon", 0.6),
    (r"\b(it's|it is)\s+(obvious|clear)\s+(that|to everyone)\b", "Bandwagon", 0.5),
    # False dilemma / false dichotomy
    (r"\beither\s+\.\.\.\s+or\s+(we|they)\s+(will|must)\b", "False Dilemma", 0.6),
    (r"\byou\s+(either|must)\s+(support|oppose)\s+\.\.\.\s+or\s+you\s+(are|support)\b", "False Dilemma", 0.7),
    (r"\b(only|just)\s+two\s+(choices|options|ways)\b", "False Dilemma", 0.5),
    # Slippery slope
    (r"\b(if|once)\s+(we|they)\s+(allow|accept)\s+\.\.\.\s+(then|next)\s+(we|they)\s+will\b", "Slippery Slope", 0.6),
    (r"\b(that|this)\s+will\s+lead\s+to\s+(chaos|disaster|the end)\b", "Slippery Slope", 0.5),
    # Appeal to authority (weak)
    (r"\b(experts|scientists|doctors)\s+(all|unanimously)\s+(say|agree)\b", "Appeal to Authority", 0.4),
    (r"\b(studies|research)\s+(show|prove)\s+(that|this)\b", "Appeal to Authority", 0.3),
    # Hasty generalization
    (r"\b(one|a few)\s+(example|case|incident)\s+(proves|shows)\s+(that|this)\b", "Hasty Generalization", 0.6),
    (r"\b(all|every)\s+\w+\s+(always|never)\s+\w+\b", "Hasty Generalization", 0.5),
    # Loaded language / emotional
    (r"\b(clearly|obviously|undoubtedly)\s+(wrong|false|misleading)\b", "Loaded Language", 0.4),
    (r"\b(disgusting|outrageous|shameful)\s+(that|how)\b", "Loaded Language", 0.5),
]


def detect_fallacies(text: str) -> List[Dict[str, Any]]:
    """Detect logical fallacies in text using pattern matching.

    Args:
        text: Plain text to analyze (e.g. from extractors.extract_text)

    Returns:
        List of fallacy dicts: {id, name, statement, context_excerpt, severity}
    """
    if not text or not text.strip():
        return []

    fallacies: List[Dict[str, Any]] = []
    seen: set = set()  # (name, statement_snippet) to dedupe

    # Split into sentences for context
    sentences = re.split(r"[.!?]+", text)
    full_lower = text.lower()

    for pattern, name, severity in _FALLACY_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            start = max(0, m.start() - 50)
            end = min(len(text), m.end() + 50)
            excerpt = text[start:end].strip()
            if excerpt.startswith("..."):
                excerpt = excerpt[3:].strip()
            if excerpt.endswith("..."):
                excerpt = excerpt[:-3].strip()
            statement = m.group(0).strip()
            key = (name, statement[:60])
            if key in seen:
                continue
            seen.add(key)
            fallacies.append({
                "id": make_id("fallacy"),
                "name": name,
                "statement": statement,
                "context_excerpt": excerpt[:200] if excerpt else None,
                "severity": severity,
            })

    return fallacies
