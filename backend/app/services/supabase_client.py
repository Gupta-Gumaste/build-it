"""Shared Supabase client. All database requests route through this client."""

from functools import lru_cache

from supabase import Client, create_client

from app.core.config import settings


@lru_cache
def get_supabase() -> Client:
    """Return a cached Supabase client, built once per process."""
    return create_client(settings.supabase_url, settings.supabase_secret_key)
