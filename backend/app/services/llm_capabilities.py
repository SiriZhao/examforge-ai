from __future__ import annotations

import math
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any


@dataclass(frozen=True)
class ModelCapability:
    context_window: int
    recommended_max_input: int
    max_output_tokens: int
    reserved_output_tokens: int
    safety_margin: int

    def available_input_tokens(self, *, system_tokens: int = 0, schema_tokens: int = 0) -> int:
        return max(
            512,
            min(
                self.recommended_max_input,
                self.context_window
                - self.reserved_output_tokens
                - self.safety_margin
                - system_tokens
                - schema_tokens,
            ),
        )


DEFAULT_CAPABILITY = ModelCapability(
    context_window=32_000,
    recommended_max_input=24_000,
    max_output_tokens=4_096,
    reserved_output_tokens=3_072,
    safety_margin=2_048,
)


MODEL_CAPABILITIES: tuple[tuple[re.Pattern[str], ModelCapability], ...] = (
    (re.compile(r"deepseek", re.I), ModelCapability(64_000, 48_000, 8_192, 4_096, 4_096)),
    (re.compile(r"gpt-4o|gpt-4\.1|gpt-5", re.I), ModelCapability(128_000, 96_000, 16_384, 4_096, 8_192)),
    (re.compile(r"qwen", re.I), ModelCapability(128_000, 96_000, 8_192, 4_096, 8_192)),
)


def capability_for(provider: str | None, model: str | None) -> ModelCapability:
    label = f"{provider or ''}/{model or ''}"
    for pattern, capability in MODEL_CAPABILITIES:
        if pattern.search(label):
            return capability
    return DEFAULT_CAPABILITY


def estimate_tokens(text: str, model: str | None = None) -> int:
    """Conservative fallback when a provider tokenizer is unavailable.

    CJK, Latin words, numbers, whitespace and punctuation are counted separately;
    this deliberately does not assume one Chinese character equals one token.
    """
    if not text:
        return 0
    conservative = _conservative_token_estimate(text)
    encoder = _tiktoken_encoder(model)
    if encoder is not None:
        try:
            # The provider tokenizer is authoritative for encoding, while the
            # fallback remains a safety floor for mixed CJK-compatible models.
            return max(len(encoder.encode(text, disallowed_special=())), conservative)
        except Exception:
            pass
    return conservative


def _conservative_token_estimate(text: str) -> int:
    cjk = len(re.findall(r"[\u3400-\u9fff\uf900-\ufaff]", text))
    latin_words = len(re.findall(r"[A-Za-z]+(?:['_-][A-Za-z]+)*", text))
    numbers = len(re.findall(r"\d+(?:\.\d+)?", text))
    consumed = "".join(re.findall(r"[\u3400-\u9fff\uf900-\ufaff]|[A-Za-z]+(?:['_-][A-Za-z]+)*|\d+(?:\.\d+)?", text))
    remainder = max(0, len(text) - len(consumed))
    return max(1, math.ceil(cjk * 1.5 + latin_words * 1.25 + numbers + remainder / 3.0))


def text_fits(text: str, token_budget: int) -> bool:
    return estimate_tokens(text) <= max(1, token_budget)


@lru_cache(maxsize=32)
def _tiktoken_encoder(model: str | None) -> Any | None:
    """Use a real tokenizer when the optional dependency is available."""
    try:
        import tiktoken

        if model:
            try:
                return tiktoken.encoding_for_model(model)
            except KeyError:
                pass
        return tiktoken.get_encoding("cl100k_base")
    except (ImportError, ModuleNotFoundError):
        return None
