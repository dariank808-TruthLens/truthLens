"""GraphQL type definitions for TruthLens."""
from typing import List, Optional

import strawberry


@strawberry.type
class User:
    id: strawberry.ID
    account_id: str  # unique account identifier
    name: str
    email: Optional[str]
    wallet_address: Optional[str]  # blockchain wallet (e.g., Ethereum address)
    created_at: str


@strawberry.type
class FileRef:
    id: strawberry.ID
    user_id: strawberry.ID  # uploader's user_id
    name: str
    content_type: Optional[str]
    size: Optional[int]
    storage_url: Optional[str]  # object storage reference (e.g., S3 URL)


@strawberry.type
class Source:
    title: Optional[str]
    url: str
    score: Optional[float]


@strawberry.type
class FactCheck:
    id: strawberry.ID
    statement: str
    score: float  # 0.0 to 1.0: statistical confidence that statement is factually sound
    sources_for: List[Source]
    sources_against: List[Source]


@strawberry.type
class Fallacy:
    id: strawberry.ID
    name: str
    statement: str
    context_excerpt: Optional[str]
    position: Optional[str]  # fallacy position in argument (e.g., "premise", "conclusion")
    severity: float  # 0.0 to 1.0: how severe the fallacy is


@strawberry.type
class AICheck:
    id: strawberry.ID
    is_ai: bool
    score: float
    explanation: Optional[str]


@strawberry.type
class AnalysisSummary:
    fact_checks: int
    fallacies: int
    ai_score: Optional[float]


@strawberry.type
class AnalysisBreakdown:
    """Aggregated statistical scores from all checks"""
    fact_check_score: Optional[float]  # 0.0 to 1.0: avg confidence from fact-checking
    logical_fallacy_score: Optional[float]  # 0.0 to 1.0: inverse of fallacy severity (lower = more fallacies)
    ai_generation_score: Optional[float]  # 0.0 to 1.0: likelihood of AI generation
    overall_credibility_score: Optional[float]  # 0.0 to 1.0: weighted overall credibility


@strawberry.type
class Analysis:
    id: strawberry.ID
    upload_id: strawberry.ID
    status: str
    started_at: Optional[str]
    finished_at: Optional[str]
    summary: Optional[AnalysisSummary]
    breakdown: Optional[AnalysisBreakdown]
    fact_checks: Optional[List[FactCheck]]
    fallacies: Optional[List[Fallacy]]
    ai_check: Optional[AICheck]


@strawberry.type
class UploadSettings:
    fact_check: bool
    logical_fallacy_check: bool
    ai_generation_check: bool


@strawberry.type
class Upload:
    id: strawberry.ID
    user_id: Optional[strawberry.ID]
    created_at: str
    status: str
    files: List[FileRef]
    settings: UploadSettings
    analysis_id: Optional[strawberry.ID]


# Input types
@strawberry.input
class FileInput:
    user_id: Optional[strawberry.ID] = None  # uploader's user_id
    name: str
    content_type: Optional[str] = None
    size: Optional[int] = None
    storage_url: Optional[str] = None


@strawberry.input
class CreateUserInput:
    account_id: str
    name: str
    email: Optional[str] = None
    wallet_address: Optional[str] = None


@strawberry.input
class UploadSettingsInput:
    fact_check: Optional[bool] = False
    logical_fallacy_check: Optional[bool] = False
    ai_generation_check: Optional[bool] = False


@strawberry.input
class CreateUploadInput:
    files: List[FileInput]
    user_id: Optional[strawberry.ID] = None  # uploader's user_id; inherited by files if not set
    settings: Optional[UploadSettingsInput] = None
