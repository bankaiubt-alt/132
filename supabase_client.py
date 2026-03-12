from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ENV_PATH = Path(__file__).resolve().with_name(".env")


@dataclass(frozen=True)
class SupabaseConnection:
    client: object | None
    url: str | None
    key_name: str | None
    error: str | None

    @property
    def is_ready(self) -> bool:
        return self.client is not None


def build_supabase_connection() -> SupabaseConnection:
    load_dotenv(ENV_PATH)

    url = _read_env("SUPABASE_URL")
    key_name, key = _read_key()

    if not url:
        return SupabaseConnection(
            client=None,
            url=None,
            key_name=key_name,
            error="не задан SUPABASE_URL",
        )

    if not key:
        return SupabaseConnection(
            client=None,
            url=url,
            key_name=key_name,
            error=_missing_key_message(),
        )

    try:
        from supabase import create_client
    except ModuleNotFoundError:
        return SupabaseConnection(
            client=None,
            url=url,
            key_name=key_name,
            error="не установлен пакет supabase",
        )

    try:
        client = create_client(url, key)
    except Exception as exc:
        return SupabaseConnection(
            client=None,
            url=url,
            key_name=key_name,
            error=f"ошибка инициализации клиента: {exc}",
        )

    return SupabaseConnection(client=client, url=url, key_name=key_name, error=None)


def _read_env(name: str) -> str | None:
    value = os.getenv(name, "").strip()
    return value or None


def _read_key() -> tuple[str | None, str | None]:
    for name in ("SUPABASE_PUBLISHABLE_KEY", "SUPABASE_ANON_KEY", "SUPABASE_KEY"):
        value = _read_env(name)
        if value:
            return name, value
    return _unsafe_key_name(), None


def _unsafe_key_name() -> str | None:
    for name in ("SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SECRET_KEY"):
        if _read_env(name):
            return name
    return None


def _missing_key_message() -> str:
    unsafe_name = _unsafe_key_name()
    if unsafe_name:
        return f"найден {unsafe_name}, но для клиентского приложения нужен publishable/anon key"
    return "не задан SUPABASE_PUBLISHABLE_KEY или SUPABASE_ANON_KEY"
