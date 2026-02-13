"""GraphQL resolvers and mutations for TruthLens."""
import asyncio
from typing import AsyncGenerator, List, Optional

import strawberry

from .graphql_types import (
    User, FileRef, Source, FactCheck, Fallacy, AICheck, AnalysisSummary,
    AnalysisBreakdown, Analysis, UploadSettings, Upload,
    CreateUserInput, CreateUploadInput, FileInput
)

# Import logic modules
from backend.logic.utils import now_iso, make_id
from backend.logic.analysis import compute_breakdown
from backend.logic.fixtures import load_fixture_analysis
from backend.logic import store

# Simple queue for subscription notifications
_analysis_queue: "asyncio.Queue[dict]" = asyncio.Queue()


@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: strawberry.ID) -> Optional[User]:
        u = store.get_user(str(id))
        if not u:
            return None
        return User(**u)

    @strawberry.field
    def upload(self, id: strawberry.ID) -> Optional[Upload]:
        u = store.get_upload(str(id))
        if not u:
            return None
        return Upload(**u)

    @strawberry.field
    def analysis(self, id: strawberry.ID) -> Optional[Analysis]:
        a = store.get_analysis(str(id))
        if not a:
            return None
        return Analysis(**a)


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, input: CreateUserInput) -> User:
        user_id = make_id("user")
        doc = {
            "id": user_id,
            "account_id": input.account_id,
            "name": input.name,
            "email": input.email,
            "wallet_address": input.wallet_address,
            "created_at": now_iso(),
        }
        store.save_user(user_id, doc)
        return User(**doc)

    @strawberry.mutation
    def create_upload(self, input: CreateUploadInput) -> Upload:
        upload_id = make_id("upload")
        files = []
        for f in input.files:
            fid = make_id("file")
            files.append({
                "id": fid,
                "user_id": f.user_id or input.user_id,  # inherit from input if not in file
                "name": f.name,
                "content_type": f.content_type,
                "size": f.size,
                "storage_url": f.storage_url,
            })

        settings = {
            "fact_check": bool(input.settings.fact_check) if input.settings else False,
            "logical_fallacy_check": bool(input.settings.logical_fallacy_check) if input.settings else False,
            "ai_generation_check": bool(input.settings.ai_generation_check) if input.settings else False,
        }

        doc = {
            "id": upload_id,
            "user_id": input.user_id,  # track uploader
            "created_at": now_iso(),
            "status": "pending",
            "files": files,
            "settings": settings,
            "analysis_id": None,
        }
        store.save_upload(upload_id, doc)
        return Upload(**doc)

    @strawberry.mutation
    async def start_analysis(self, upload_id: strawberry.ID) -> Analysis:
        # find upload
        up = store.get_upload(str(upload_id))
        if not up:
            raise Exception("Upload not found")

        # create analysis master
        analysis_id = make_id("analysis")
        started = now_iso()
        # load fixture for detail content where available
        fixture = load_fixture_analysis()
        if fixture:
            # patch ids to link
            fixture["id"] = analysis_id
            fixture["upload_id"] = upload_id
            fixture["started_at"] = started
            fixture["finished_at"] = now_iso()
            fixture["status"] = "ready"
            # compute breakdown scores
            breakdown = compute_breakdown(
                fixture.get("fact_checks", []),
                fixture.get("fallacies", []),
                fixture.get("ai_check", {})
            )
            fixture["breakdown"] = breakdown
            store.save_analysis(analysis_id, fixture)
        else:
            summary = {"fact_checks": 0, "fallacies": 0, "ai_score": None}
            breakdown = {
                "fact_check_score": None,
                "logical_fallacy_score": None,
                "ai_generation_score": None,
                "overall_credibility_score": None,
            }
            doc = {
                "id": analysis_id,
                "upload_id": upload_id,
                "started_at": started,
                "finished_at": now_iso(),
                "status": "ready",
                "summary": summary,
                "breakdown": breakdown,
                "fact_checks": [],
                "fallacies": [],
                "ai_check": {"id": make_id("ai"), "is_ai": False, "score": 0.0, "explanation": "placeholder"},
            }
            store.save_analysis(analysis_id, doc)

        # link upload -> analysis
        up["analysis_id"] = analysis_id
        up["status"] = "ready"
        store.save_upload(str(upload_id), up)

        # notify subscribers
        await _analysis_queue.put(store.get_analysis(analysis_id))

        return Analysis(**store.get_analysis(analysis_id))

    @strawberry.mutation
    def clear_upload(self, upload_id: strawberry.ID) -> bool:
        up = store.get_upload(str(upload_id))
        if not up:
            return False
        # simple clear: remove upload and related analysis
        aid = up.get("analysis_id")
        if aid:
            store.delete_analysis(str(aid))
        store.delete_upload(str(upload_id))
        return True


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def analysis_ready(self, upload_id: strawberry.ID) -> AsyncGenerator[Analysis, None]:
        # yields analysis document when ready
        while True:
            item = await _analysis_queue.get()
            if item.get("upload_id") == str(upload_id):
                yield Analysis(**item)