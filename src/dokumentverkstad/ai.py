from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil
import json
from uuid import uuid4

from .knowledge import utc_now


PROMPT_VERSION = "document-analysis-v1"
DEFAULT_AI_PROVIDER = "openai"
DEFAULT_AI_MODEL = "gpt-5.6-luna"
DEFAULT_MAX_OUTPUT_TOKENS = 6000
MAX_INPUT_TOKENS = 1_000_000
LONG_CONTEXT_INPUT_TOKEN_THRESHOLD = 272_000
AI_CAPABILITIES = (
    "summary",
    "candidate_insight",
    "candidate_claim",
    "candidate_question",
    "project_suggestion",
)


@dataclass(frozen=True)
class ModelPricing:
    short_input_per_million: float
    short_output_per_million: float
    long_input_per_million: float
    long_output_per_million: float
    long_context_input_token_threshold: int = LONG_CONTEXT_INPUT_TOKEN_THRESHOLD
    currency: str = "USD"


MODEL_PRICING = {
    DEFAULT_AI_MODEL: ModelPricing(
        short_input_per_million=0.20,
        short_output_per_million=1.20,
        long_input_per_million=0.40,
        long_output_per_million=1.80,
    ),
}


class AiProviderError(Exception):
    pass


class MissingCredentialError(AiProviderError):
    pass


class DocumentTooLargeError(AiProviderError):
    pass


class InvalidAiResultError(AiProviderError):
    pass


@dataclass(frozen=True)
class AiCandidate:
    capability: str
    content: str
    confidence: str = ""
    project_id: str = ""
    project_name: str = ""


@dataclass(frozen=True)
class AiUsage:
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass(frozen=True)
class AiCost:
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    currency: str
    method: str


@dataclass(frozen=True)
class AiAnalysisResult:
    candidates: tuple[AiCandidate, ...]
    usage: AiUsage


@dataclass(frozen=True)
class AiRunRecord:
    id: str
    document_id: str
    provider: str
    model: str
    prompt_version: str
    capabilities: tuple[str, ...]
    created_at: str
    status: str
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_cost: float
    actual_input_tokens: int = 0
    actual_output_tokens: int = 0
    actual_cost: float = 0.0
    currency: str = "USD"
    error: str = ""
    candidate_ids: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def create(
        cls,
        document_id: str,
        provider: str,
        model: str,
        capabilities: tuple[str, ...],
        estimate: AiCost,
    ) -> "AiRunRecord":
        return cls(
            id=f"airun_{uuid4().hex}",
            document_id=document_id,
            provider=provider,
            model=model,
            prompt_version=PROMPT_VERSION,
            capabilities=capabilities,
            created_at=utc_now(),
            status="planned",
            estimated_input_tokens=estimate.input_tokens,
            estimated_output_tokens=estimate.output_tokens,
            estimated_cost=estimate.estimated_cost,
            currency=estimate.currency,
        )

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "AiRunRecord":
        return cls(
            id=str(data["id"]),
            document_id=str(data["document_id"]),
            provider=str(data["provider"]),
            model=str(data["model"]),
            prompt_version=str(data["prompt_version"]),
            capabilities=tuple(str(item) for item in data.get("capabilities", [])),
            created_at=str(data["created_at"]),
            status=str(data["status"]),
            estimated_input_tokens=int(data.get("estimated_input_tokens", 0)),
            estimated_output_tokens=int(data.get("estimated_output_tokens", 0)),
            estimated_cost=float(data.get("estimated_cost", 0.0)),
            actual_input_tokens=int(data.get("actual_input_tokens", 0)),
            actual_output_tokens=int(data.get("actual_output_tokens", 0)),
            actual_cost=float(data.get("actual_cost", 0.0)),
            currency=str(data.get("currency", "USD")),
            error=str(data.get("error", "")),
            candidate_ids=tuple(str(item) for item in data.get("candidate_ids", [])),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "type": "AiRun",
            "document_id": self.document_id,
            "provider": self.provider,
            "model": self.model,
            "prompt_version": self.prompt_version,
            "capabilities": list(self.capabilities),
            "created_at": self.created_at,
            "status": self.status,
            "estimated_input_tokens": self.estimated_input_tokens,
            "estimated_output_tokens": self.estimated_output_tokens,
            "estimated_cost": self.estimated_cost,
            "actual_input_tokens": self.actual_input_tokens,
            "actual_output_tokens": self.actual_output_tokens,
            "actual_cost": self.actual_cost,
            "currency": self.currency,
            "error": self.error,
            "candidate_ids": list(self.candidate_ids),
        }

    def completed(self, usage: AiUsage, candidate_ids: tuple[str, ...]) -> "AiRunRecord":
        actual_cost = estimate_cost(
            usage.input_tokens, usage.output_tokens, self.model
        ).estimated_cost
        return AiRunRecord(
            id=self.id,
            document_id=self.document_id,
            provider=self.provider,
            model=self.model,
            prompt_version=self.prompt_version,
            capabilities=self.capabilities,
            created_at=self.created_at,
            status="completed",
            estimated_input_tokens=self.estimated_input_tokens,
            estimated_output_tokens=self.estimated_output_tokens,
            estimated_cost=self.estimated_cost,
            actual_input_tokens=usage.input_tokens,
            actual_output_tokens=usage.output_tokens,
            actual_cost=actual_cost,
            currency=self.currency,
            candidate_ids=candidate_ids,
        )

    def failed(self, error: str) -> "AiRunRecord":
        return AiRunRecord(
            id=self.id,
            document_id=self.document_id,
            provider=self.provider,
            model=self.model,
            prompt_version=self.prompt_version,
            capabilities=self.capabilities,
            created_at=self.created_at,
            status="failed",
            estimated_input_tokens=self.estimated_input_tokens,
            estimated_output_tokens=self.estimated_output_tokens,
            estimated_cost=self.estimated_cost,
            currency=self.currency,
            error=error,
        )


class AiProvider:
    name = "provider"

    def estimate_input_tokens(self, text: str, model: str) -> int:
        return estimate_input_tokens(text)

    def analyze_document(
        self,
        title: str,
        text: str,
        projects: tuple[tuple[str, str], ...],
        model: str,
        max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    ) -> AiAnalysisResult:
        raise NotImplementedError


class MockAiProvider(AiProvider):
    name = "mock"

    def analyze_document(
        self,
        title: str,
        text: str,
        projects: tuple[tuple[str, str], ...],
        model: str,
        max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    ) -> AiAnalysisResult:
        first_project = projects[0] if projects else ("", "")
        candidates = [
            AiCandidate("summary", f"Kort sammanfattning av {title}.", "medel"),
            AiCandidate("candidate_insight", "Dokumentet pekar ut ett möjligt tema.", "medel"),
            AiCandidate("candidate_claim", "Dokumentet gör ett centralt påstående.", "medel"),
            AiCandidate("candidate_question", "Vilken följdfråga bör undersökas?", "låg"),
        ]
        if first_project[0]:
            candidates.append(
                AiCandidate(
                    "project_suggestion",
                    f"Kan vara relevant för projektet {first_project[1]}.",
                    "låg",
                    project_id=first_project[0],
                    project_name=first_project[1],
                )
            )
        usage = AiUsage(input_tokens=estimate_input_tokens(text), output_tokens=120)
        return AiAnalysisResult(candidates=tuple(candidates), usage=usage)


class OpenAiProvider(AiProvider):
    name = "openai"

    def __init__(self, api_key: str):
        if not api_key:
            raise MissingCredentialError(
                "AI-provider saknar API-nyckel. Lägg till OPENAI_API_KEY eller initiera krypterade secrets."
            )
        self.api_key = api_key

    def estimate_input_tokens(self, text: str, model: str) -> int:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            response = client.responses.input_tokens.count(
                model=model, input=_analysis_input("Tokenräkning", text, ())
            )
            return int(response.input_tokens)
        except Exception:
            return estimate_input_tokens(text)

    def analyze_document(
        self,
        title: str,
        text: str,
        projects: tuple[tuple[str, str], ...],
        model: str,
        max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    ) -> AiAnalysisResult:
        try:
            from openai import OpenAI
        except ImportError as error:
            raise AiProviderError(
                "OpenAI SDK är inte installerat. Installera projektets beroenden innan AI används."
            ) from error

        client = OpenAI(api_key=self.api_key)
        try:
            response = client.responses.create(
                model=model,
                input=_analysis_input(title, text, projects),
                max_output_tokens=max_output_tokens,
                store=False,
                text={"format": _response_format_schema()},
            )
        except Exception as error:
            raise AiProviderError(f"AI-anropet misslyckades: {error.__class__.__name__}") from error

        return _analysis_result_from_openai_response(response)


def estimate_input_tokens(text: str) -> int:
    return max(1, ceil(len(text) / 4))


def estimate_cost(
    input_tokens: int,
    output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    model: str = DEFAULT_AI_MODEL,
) -> AiCost:
    pricing = MODEL_PRICING.get(model)
    if pricing is None:
        return AiCost(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost=0.0,
            currency="USD",
            method="unknown_model_price",
        )
    input_price, output_price, context_tier = _prices_for_context(
        pricing, input_tokens
    )
    cost = (input_tokens / 1_000_000) * input_price + (
        output_tokens / 1_000_000
    ) * output_price
    return AiCost(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost=round(cost, 6),
        currency=pricing.currency,
        method=f"estimated_tokens_x_configured_price_{context_tier}_context",
    )


def _prices_for_context(
    pricing: ModelPricing, input_tokens: int
) -> tuple[float, float, str]:
    if input_tokens > pricing.long_context_input_token_threshold:
        return pricing.long_input_per_million, pricing.long_output_per_million, "long"
    return pricing.short_input_per_million, pricing.short_output_per_million, "short"


def validate_document_size(input_tokens: int) -> None:
    if input_tokens > MAX_INPUT_TOKENS:
        raise DocumentTooLargeError(
            "Dokumentets extraherade text är för stor för vald modell. "
            "Ingen trunkering görs automatiskt."
        )


def _analysis_input(
    title: str, text: str, projects: tuple[tuple[str, str], ...]
) -> list[dict[str, str]]:
    project_lines = "\n".join(f"- {project_id}: {name}" for project_id, name in projects)
    return [
        {
            "role": "system",
            "content": (
                "Du är en rådgivare i Dokumentverkstad. Skapa endast kandidater "
                "som användaren ska granska. Svara strikt enligt JSON-schemat."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Promptversion: {PROMPT_VERSION}\n"
                f"Dokumenttitel: {title}\n"
                f"Befintliga projekt:\n{project_lines or '- inga'}\n\n"
                "Fyll JSON-schemats fält: summary, candidate_insights, "
                "candidate_claims, candidate_questions och project_suggestions. "
                "Använd tomma listor när ett fält saknar rimliga kandidater.\n\n"
                f"Extraherad text:\n{text}"
            ),
        },
    ]


def _response_format_schema() -> dict[str, object]:
    text_candidate = {
        "type": "object",
        "properties": {
            "content": {"type": "string"},
            "confidence": {"type": "string", "enum": ["", "låg", "medel", "hög"]},
        },
        "required": ["content", "confidence"],
        "additionalProperties": False,
    }
    project_candidate = {
        "type": "object",
        "properties": {
            "content": {"type": "string"},
            "confidence": {"type": "string", "enum": ["", "låg", "medel", "hög"]},
            "project_id": {"type": "string"},
            "project_name": {"type": "string"},
        },
        "required": ["content", "confidence", "project_id", "project_name"],
        "additionalProperties": False,
    }
    return {
        "type": "json_schema",
        "name": "document_analysis",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "summary": text_candidate,
                "candidate_insights": {"type": "array", "items": text_candidate},
                "candidate_claims": {"type": "array", "items": text_candidate},
                "candidate_questions": {"type": "array", "items": text_candidate},
                "project_suggestions": {"type": "array", "items": project_candidate},
            },
            "required": [
                "summary",
                "candidate_insights",
                "candidate_claims",
                "candidate_questions",
                "project_suggestions",
            ],
            "additionalProperties": False,
        },
    }


def _analysis_result_from_openai_response(response: object) -> AiAnalysisResult:
    _raise_for_incomplete_response(response)
    _raise_for_refusal(response)
    try:
        data = json.loads(_output_text_from_response(response))
    except json.JSONDecodeError as error:
        raise InvalidAiResultError("AI-resultatet var inte giltig strukturerad JSON.") from error
    if not isinstance(data, dict):
        raise InvalidAiResultError("AI-resultatet var inte ett JSON-objekt.")

    return AiAnalysisResult(
        candidates=_candidates_from_payload(data),
        usage=_usage_from_response(response),
    )


def _raise_for_incomplete_response(response: object) -> None:
    status = str(_field(response, "status", "") or "")
    if status in ("", "completed"):
        return
    if status == "incomplete":
        details = _field(response, "incomplete_details", None)
        reason = str(_field(details, "reason", "") or "okänd orsak")
        raise AiProviderError(
            f"AI-svaret blev ofullständigt ({reason}). Inga kandidater sparades."
        )
    raise AiProviderError(
        f"AI-provider returnerade status {status}. Inga kandidater sparades."
    )


def _raise_for_refusal(response: object) -> None:
    if _refusal_from_response(response):
        raise AiProviderError(
            "AI-provider avböjde att analysera dokumentet. Inga kandidater sparades."
        )


def _refusal_from_response(response: object) -> str:
    for part in _content_parts(response):
        if str(_field(part, "type", "") or "") == "refusal":
            return str(_field(part, "refusal", "") or "refusal")
    return ""


def _output_text_from_response(response: object) -> str:
    output_text = str(_field(response, "output_text", "") or "").strip()
    if output_text:
        return output_text
    parts = [
        str(_field(part, "text", "") or "")
        for part in _content_parts(response)
        if str(_field(part, "type", "") or "") == "output_text"
    ]
    output_text = "".join(parts).strip()
    if not output_text:
        raise InvalidAiResultError("AI-svaret saknade strukturerad output-text.")
    return output_text


def _content_parts(response: object) -> tuple[object, ...]:
    parts: list[object] = []
    output = _field(response, "output", ()) or ()
    for item in output if isinstance(output, (list, tuple)) else (output,):
        content = _field(item, "content", ()) or ()
        if isinstance(content, (list, tuple)):
            parts.extend(content)
        else:
            parts.append(content)
    return tuple(parts)


def _usage_from_response(response: object) -> AiUsage:
    usage = _field(response, "usage", None)
    return AiUsage(
        input_tokens=int(_field(usage, "input_tokens", 0) or 0),
        output_tokens=int(_field(usage, "output_tokens", 0) or 0),
    )


def _field(value: object, name: str, default: object = None) -> object:
    if isinstance(value, dict):
        return value.get(name, default)
    return getattr(value, name, default)


def _candidates_from_payload(data: dict[str, object]) -> tuple[AiCandidate, ...]:
    candidates: list[AiCandidate] = [
        _candidate_from_payload("summary", _required_dict(data, "summary"))
    ]
    for section, capability in (
        ("candidate_insights", "candidate_insight"),
        ("candidate_claims", "candidate_claim"),
        ("candidate_questions", "candidate_question"),
    ):
        for item in _required_list(data, section):
            candidates.append(_candidate_from_payload(capability, item))
    for item in _required_list(data, "project_suggestions"):
        candidates.append(_candidate_from_payload("project_suggestion", item))
    return tuple(candidates)


def _candidate_from_payload(capability: str, item: dict[str, object]) -> AiCandidate:
    content = str(item.get("content", "")).strip()
    confidence = str(item.get("confidence", "")).strip()
    if capability not in AI_CAPABILITIES or not content:
        raise InvalidAiResultError("AI-resultatet innehåller en ofullständig kandidat.")
    if confidence not in ("", "låg", "medel", "hög"):
        raise InvalidAiResultError("AI-resultatet innehåller ogiltig confidence.")
    return AiCandidate(
        capability=capability,
        content=content,
        confidence=confidence,
        project_id=str(item.get("project_id", "")).strip(),
        project_name=str(item.get("project_name", "")).strip(),
    )


def _required_dict(data: dict[str, object], name: str) -> dict[str, object]:
    value = data.get(name)
    if not isinstance(value, dict):
        raise InvalidAiResultError(f"AI-resultatet saknar fältet {name}.")
    return value


def _required_list(data: dict[str, object], name: str) -> list[dict[str, object]]:
    value = data.get(name)
    if not isinstance(value, list):
        raise InvalidAiResultError(f"AI-resultatet saknar listan {name}.")
    if not all(isinstance(item, dict) for item in value):
        raise InvalidAiResultError(f"AI-resultatet innehåller ogiltiga poster i {name}.")
    return value
