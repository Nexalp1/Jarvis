from __future__ import annotations

import importlib.util
import logging
from pathlib import Path
from typing import Callable


logger = logging.getLogger(__name__)

SkillHandler = Callable[[str], str]


class SkillRegistry:
    """Dynamic skill registry loaded from /skills."""

    def __init__(self) -> None:
        self._skills: dict[str, SkillHandler] = {}

    def register(self, name: str, handler: SkillHandler) -> None:
        self._skills[name.lower()] = handler
        logger.info("Skill registrada: %s", name)

    def dispatch(self, command: str) -> str | None:
        lowered = command.lower()
        for name, handler in self._skills.items():
            if lowered.startswith(name):
                return handler(command)
        return None

    def load_from_directory(self, directory: Path | str = "skills") -> None:
        skill_dir = Path(directory)
        skill_dir.mkdir(parents=True, exist_ok=True)

        for file in skill_dir.glob("*.py"):
            if file.name.startswith("_"):
                continue
            module_name = f"skills.{file.stem}"
            spec = importlib.util.spec_from_file_location(module_name, file)
            if spec is None or spec.loader is None:
                logger.warning("Não foi possível carregar skill %s", file)
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            register_fn = getattr(module, "register", None)
            if callable(register_fn):
                register_fn(self)
            else:
                logger.warning("Skill %s não possui função register(registry)", file.name)
