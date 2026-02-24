from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class JarvisConfig:
    assistant_name: str
    wake_word: str
    language: str
    llm: dict[str, Any]
    voice: dict[str, Any]
    memory: dict[str, Any]
    engineering: dict[str, Any]
    logging: dict[str, Any]


DEFAULT_CONFIG_PATH = Path("config/config.json")


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> JarvisConfig:
    """Load Jarvis runtime configuration from JSON file."""
    cfg_path = Path(path)
    with cfg_path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)

    return JarvisConfig(
        assistant_name=data.get("assistant_name", "Jarvis"),
        wake_word=data.get("wake_word", "jarvis"),
        language=data.get("language", "pt-BR"),
        llm=data.get("llm", {}),
        voice=data.get("voice", {}),
        memory=data.get("memory", {}),
        engineering=data.get("engineering", {}),
        logging=data.get("logging", {}),
    )
