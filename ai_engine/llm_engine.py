import re
import logging
from typing import Optional

from huggingface_hub import InferenceClient

from config import HF_TOKEN, MODEL_ID, LLM_MAX_TOKENS, LLM_TEMPERATURE, LLM_TIMEOUT

logger = logging.getLogger(__name__)

_client: Optional[InferenceClient] = None


def initialize_llm() -> None:
    """Initialize the HuggingFace InferenceClient. Called once at startup."""
    global _client

    if not HF_TOKEN:
        raise ValueError(
            "HF_TOKEN is not set. Add it to your .env file before starting the server."
        )

    _client = InferenceClient(
        model=MODEL_ID,
        token=HF_TOKEN,
        timeout=LLM_TIMEOUT,
    )
    logger.info("LLM engine initialized — model: %s", MODEL_ID)


def call_model(prompt: str, system_instruction: str) -> str:
    """
    Send a chat-completion request to the medical LLM and return cleaned text.

    Args:
        prompt: The user-facing content of the request.
        system_instruction: The system role instruction that constrains the model.

    Returns:
        Cleaned plain-text response from the model.

    Raises:
        RuntimeError: If the engine has not been initialized.
    """
    if _client is None:
        raise RuntimeError(
            "LLM engine is not initialized. Ensure initialize_llm() ran at startup."
        )

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user",   "content": prompt},
    ]

    response = _client.chat_completion(
        messages=messages,
        max_tokens=LLM_MAX_TOKENS,
        temperature=LLM_TEMPERATURE,
    )

    raw: str = response.choices[0].message.content or ""
    return _clean_response(raw)


def _clean_response(text: str) -> str:
    """Strip reasoning/thinking wrapper tokens some LLMs emit."""
    # Remove <think>...</think> and similar internal monologue blocks
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<\|thinking\|>.*?<\|/thinking\|>", "", text, flags=re.DOTALL | re.IGNORECASE)
    return text.strip()
