"""Tests for the app.services.llm provider dispatch and helpers."""

import os

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_PUBLISHABLE_KEY", "test-publishable-key")
os.environ.setdefault("SUPABASE_SECRET_KEY", "test-secret-key")
os.environ.setdefault("SUPABASE_JWKS_URL", "https://example.supabase.co/auth/v1/.well-known/jwks.json")

import pytest  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.services import llm  # noqa: E402


def test_gemini_role_maps_assistant_to_model():
    assert llm._gemini_role("assistant") == "model"


def test_gemini_role_maps_user_to_user():
    assert llm._gemini_role("user") == "user"


def test_generate_raises_on_unknown_provider(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "not-a-real-provider")
    with pytest.raises(ValueError, match="Unknown AI provider"):
        llm.generate("system", [{"role": "user", "content": "hi"}])
