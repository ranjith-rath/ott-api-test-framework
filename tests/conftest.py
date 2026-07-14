"""Shared fixtures for the test suite."""

import sys
from pathlib import Path

import pytest

# Allow `from src...` / `from utils...` imports when running pytest from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.api_client import ApiClient
from src.config_loader import load_settings


@pytest.fixture(scope="session")
def settings():
    return load_settings()


@pytest.fixture(scope="session")
def api_client(settings):
    return ApiClient(
        base_url=settings.base_url,
        api_key=settings.api_key,
        timeout=settings.timeout,
        max_retries=settings.max_retries,
        backoff_factor=settings.backoff_factor,
    )
