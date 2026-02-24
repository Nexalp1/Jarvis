from __future__ import annotations

import logging

from brain.llm_client import OllamaReasoner
from core.skill_registry import SkillRegistry
from engineer.agent import EngineeringAgent
from memory.store import MemoryStore
from voice.listener import ContinuousListener
from voice.speaker import Speaker

logger = logging.getLogger(__name__)


class JarvisOrchestrator:
    """Coordinates the full Jarvis pipeline."""

    def __init__(
        self,
        assistant_name: str,
        wake_word: str,
        language: str,
        listener: ContinuousListener,
        speaker: Speaker,
        memory: MemoryStore,
        reasoner: OllamaReasoner,
        skills: SkillRegistry,
        engineer: EngineeringAgent,
    ) -> None:
        self.assistant_name = assistant_name
        self.wake_word = wake_word.lower()
        self.language = language
        self.listener = listener
        self.speaker = speaker
        self.memory = memory
        self.reasoner = reasoner
        self.skills = skills
        self.engineer = engineer

    def handle_text(self, text: str) -> str:
        normalized = text.strip()
        self.memory.save_interaction("user", normalized)

        skill_response = self.skills.dispatch(normalized)
        if skill_response is not None:
            self.memory.save_interaction("assistant", skill_response)
            return skill_response

        response = self.reasoner.respond(
            prompt=normalized,
            language=self.language,
            assistant_name=self.assistant_name,
            memory_context=self.memory.recent_context(limit=6),
        )
        self.memory.save_interaction("assistant", response)
        return response

    def start(self) -> None:
        logger.info("%s iniciado. Aguardando wake word '%s'.", self.assistant_name, self.wake_word)
        for transcript in self.listener.listen():
            lowered = transcript.lower()
            if self.wake_word not in lowered:
                continue

            command = lowered.replace(self.wake_word, "", 1).strip()
            if not command:
                self.speaker.say("Sim, como posso ajudar?")
                continue

            if command.startswith("engenharia "):
                summary = self.engineer.propose(command.removeprefix("engenharia ").strip())
                self.speaker.say(summary)
                continue

            response = self.handle_text(command)
            self.speaker.say(response)
