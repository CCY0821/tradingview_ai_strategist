"""
core/strategy_generator.py
=====================
Generates or refines TradingView **Pine Script** strategies via the OpenAI Chat Completions API.

Usage example:
```python
from core.strategy_generator import generate_strategy
ps_code = generate_strategy("產生一個 EMA 交叉策略，短期 10、長期 50")
print(ps_code)
```

Follows SOLID principles and includes concise Google-style docstrings with logging.
"""
from __future__ import annotations

# 在第一行非 __future__ 之后立即加载 .env
from dotenv import load_dotenv
load_dotenv()

import os
import logging
from typing import Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

# Environment variable key for OpenAI API
_API_KEY_ENV = "OPENAI_API_KEY"


def _get_openai_client() -> OpenAI:
    """Get an OpenAI client using the environment variable."""
    api_key = os.getenv(_API_KEY_ENV)
    if not api_key:
        raise EnvironmentError(f"{_API_KEY_ENV} environment variable is not set.")
    return OpenAI(api_key=api_key)


def _ask_gpt(
    prompt: str,
    system: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 512,
) -> str:
    """Call the OpenAI ChatCompletion API and return the assistant content."""
    client = _get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system or ""},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def generate_strategy(prompt: str, system: Optional[str] = None) -> str:
    """Generate a new Pine Script strategy given a user prompt."""
    logger.info("Generating new strategy via GPT → Pine Script")
    full_prompt = (
        "Please produce a TradingView Pine Script (version 5) strategy that meets the following requirements:"
        f" {prompt}\nMake sure it includes strategy() declaration and basic entry/exit logic."
    )
    return _ask_gpt(full_prompt, system)


def rewrite_strategy(
    existing_code: str,
    prompt: str,
    system: Optional[str] = None,
) -> str:
    """Rewrite or enhance an existing Pine Script strategy based on a prompt."""
    logger.info("Rewriting existing Pine Script strategy via GPT")
    # Build the prompt with fenced code block
    full_prompt = (
        "Here is an existing Pine Script strategy. Please modify it to satisfy the following requirements:"
        f" {prompt}\n"
        "Existing code is below:\n```pine script\n"
    )
    full_prompt += existing_code
    full_prompt += "\n```"
    return _ask_gpt(full_prompt, system)

__all__ = ["generate_strategy", "rewrite_strategy"]
