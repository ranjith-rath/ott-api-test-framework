"""
Loads framework configuration from config.yaml, with environment variables
(.env) taking precedence for secrets and environment-specific overrides.

This keeps secrets out of version control while allowing shared,
non-sensitive settings (timeouts, retries) to live in a committed YAML file.
"""

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "config.yaml"


@dataclass(frozen=True)
class Settings:
    base_url: str
    api_key: str
    timeout: int
    max_retries: int
    backoff_factor: float


def load_settings() -> Settings:
    """Load and merge YAML config with environment overrides.

    Raises:
        FileNotFoundError: if config.yaml is missing.
        ValueError: if a required API key is not set.
    """
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        yaml_config = yaml.safe_load(f) or {}

    api_key = os.getenv("TMDB_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError(
            "TMDB_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    return Settings(
        base_url=os.getenv("TMDB_BASE_URL", yaml_config.get("base_url")),
        api_key=api_key,
        timeout=int(os.getenv("REQUEST_TIMEOUT", yaml_config.get("timeout", 10))),
        max_retries=yaml_config.get("max_retries", 3),
        backoff_factor=yaml_config.get("backoff_factor", 0.5),
    )
