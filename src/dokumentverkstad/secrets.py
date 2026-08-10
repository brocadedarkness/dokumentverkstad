from __future__ import annotations

import os
from pathlib import Path
import tomllib


def load_openai_api_key(secrets_path: str | Path) -> str:
    env_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if env_key:
        return env_key

    path = Path(secrets_path)
    if not path.exists():
        return ""

    data = tomllib.loads(path.read_text(encoding="utf-8-sig"))
    openai_section = data.get("openai", {})
    if not isinstance(openai_section, dict):
        return ""
    return str(openai_section.get("api_key", "")).strip()
