from __future__ import annotations

from brain import OllamaReasoner
from config import load_config
from core import JarvisOrchestrator, SkillRegistry
from core.logging_setup import setup_logging
from engineer import EngineeringAgent
from memory import MemoryStore
from system.autostart import ensure_windows_startup, startup_command_from_main
from voice import ContinuousListener, Speaker
from voice.listener import ListenerConfig


def build_orchestrator() -> JarvisOrchestrator:
    cfg = load_config()
    setup_logging(cfg.logging["path"], cfg.logging.get("level", "INFO"))

    memory = MemoryStore(cfg.memory["sqlite_path"])
    reasoner = OllamaReasoner(
        endpoint=cfg.llm["endpoint"],
        model=cfg.llm["model"],
    )
    listener = ContinuousListener(
        ListenerConfig(
            sample_rate=cfg.voice.get("sample_rate", 16000),
            channels=cfg.voice.get("channels", 1),
            block_size=cfg.voice.get("block_size", 8000),
            vosk_model_path=cfg.voice["vosk_model_path"],
        )
    )
    speaker = Speaker(language=cfg.language)

    skills = SkillRegistry()
    skills.load_from_directory("skills")

    engineer = EngineeringAgent(
        memory=memory,
        backup_dir=cfg.engineering["backup_dir"],
        proposals_dir=cfg.engineering["proposals_dir"],
    )

    ensure_windows_startup(cfg.assistant_name, startup_command_from_main("main.py"))

    return JarvisOrchestrator(
        assistant_name=cfg.assistant_name,
        wake_word=cfg.wake_word,
        language=cfg.language,
        listener=listener,
        speaker=speaker,
        memory=memory,
        reasoner=reasoner,
        skills=skills,
        engineer=engineer,
    )


def main() -> None:
    orchestrator = build_orchestrator()
    orchestrator.start()


if __name__ == "__main__":
    main()
