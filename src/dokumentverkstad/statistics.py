from __future__ import annotations

from dataclasses import dataclass, field

from .archive import Archive
from .ai import AiRunRecord
from .knowledge import KnowledgeObject


@dataclass(frozen=True)
class UsageSummary:
    runs: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0

    def add_run(self, run: AiRunRecord) -> "UsageSummary":
        return UsageSummary(
            runs=self.runs + 1,
            input_tokens=self.input_tokens + run.actual_input_tokens,
            output_tokens=self.output_tokens + run.actual_output_tokens,
            cost=round(self.cost + run.actual_cost, 6),
        )


@dataclass(frozen=True)
class CandidateReviewSummary:
    total: int = 0
    accepted: int = 0
    edited_accepted: int = 0
    rejected: int = 0
    pending: int = 0
    later: int = 0
    handled: int = 0

    def add_candidate(self, candidate: KnowledgeObject) -> "CandidateReviewSummary":
        return CandidateReviewSummary(
            total=self.total + 1,
            accepted=self.accepted + (1 if candidate.review_status == "accepted" else 0),
            edited_accepted=self.edited_accepted
            + (1 if _is_edited_accept(candidate) else 0),
            rejected=self.rejected + (1 if candidate.review_status == "rejected" else 0),
            pending=self.pending + (1 if candidate.review_status == "candidate" else 0),
            later=self.later + (1 if candidate.review_status == "later" else 0),
            handled=self.handled + (1 if candidate.review_status == "handled" else 0),
        )


@dataclass(frozen=True)
class AiStatistics:
    completed_runs: int
    total_usage: UsageSummary
    candidate_reviews: CandidateReviewSummary
    usage_by_model: dict[str, UsageSummary] = field(default_factory=dict)
    usage_by_prompt_version: dict[str, UsageSummary] = field(default_factory=dict)
    usage_by_month: dict[str, UsageSummary] = field(default_factory=dict)
    review_by_candidate_type: dict[str, CandidateReviewSummary] = field(default_factory=dict)
    rejection_reasons: dict[str, int] = field(default_factory=dict)


def build_ai_statistics(archive: Archive) -> AiStatistics:
    runs = [run for run in archive.list_ai_runs() if run.status == "completed"]
    candidates = [
        item
        for item in archive.list_knowledge_objects()
        if item.ai_run_id or item.ai_provider or item.prompt_version
    ]

    total_usage = UsageSummary()
    usage_by_model: dict[str, UsageSummary] = {}
    usage_by_prompt_version: dict[str, UsageSummary] = {}
    usage_by_month: dict[str, UsageSummary] = {}

    for run in runs:
        total_usage = total_usage.add_run(run)
        _add_usage(usage_by_model, run.model or "okand", run)
        _add_usage(usage_by_prompt_version, run.prompt_version or "okand", run)
        _add_usage(usage_by_month, _month_key(run.created_at), run)

    candidate_reviews = CandidateReviewSummary()
    review_by_candidate_type: dict[str, CandidateReviewSummary] = {}
    rejection_reasons: dict[str, int] = {}

    for candidate in candidates:
        candidate_reviews = candidate_reviews.add_candidate(candidate)
        candidate_type = candidate.semantic_type or candidate.capability or "unknown"
        review_by_candidate_type[candidate_type] = review_by_candidate_type.get(
            candidate_type, CandidateReviewSummary()
        ).add_candidate(candidate)
        if candidate.review_status == "rejected" and candidate.rejection_reason:
            rejection_reasons[candidate.rejection_reason] = (
                rejection_reasons.get(candidate.rejection_reason, 0) + 1
            )

    return AiStatistics(
        completed_runs=len(runs),
        total_usage=total_usage,
        candidate_reviews=candidate_reviews,
        usage_by_model=dict(sorted(usage_by_model.items())),
        usage_by_prompt_version=dict(sorted(usage_by_prompt_version.items())),
        usage_by_month=dict(sorted(usage_by_month.items())),
        review_by_candidate_type=dict(sorted(review_by_candidate_type.items())),
        rejection_reasons=dict(sorted(rejection_reasons.items())),
    )


def _add_usage(
    summaries: dict[str, UsageSummary], key: str, run: AiRunRecord
) -> None:
    summaries[key] = summaries.get(key, UsageSummary()).add_run(run)


def _is_edited_accept(candidate: KnowledgeObject) -> bool:
    if candidate.review_status != "accepted":
        return False
    original = candidate.original_content or candidate.content
    accepted = candidate.accepted_content or candidate.content
    return accepted != original


def _month_key(created_at: str) -> str:
    if len(created_at) >= 7:
        return created_at[:7]
    return "okand"
