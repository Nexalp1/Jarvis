from __future__ import annotations

import logging
from typing import Iterable

import requests

logger = logging.getLogger(__name__)


class OllamaReasoner:
    def __init__(self, endpoint: str, model: str, timeout: int = 60) -> None:
        self.endpoint = endpoint
        self.model = model
        self.timeout = timeout

    def respond(
        self,
        prompt: str,
        language: str,
        assistant_name: str,
        memory_context: Iterable[tuple[str, str]],
    ) -> str:
        context_text = "\n".join(f"{role}: {message}" for role, message in memory_context)
        system_prompt = (
            f"Você é {assistant_name}. Responda sempre em {language}, de forma objetiva e útil. "
            "Se a solicitação envolver auto-modificação do sistema, exija aprovação explícita antes de aplicar mudanças."
        )
        final_prompt = f"{system_prompt}\n\nContexto recente:\n{context_text}\n\nUsuário: {prompt}"

        payload = {
            "model": self.model,
            "prompt": final_prompt,
            "stream": False,
        }

        try:
            response = requests.post(self.endpoint, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("response", "Desculpe, não consegui gerar resposta agora.").strip()
        except requests.RequestException as exc:
            logger.exception("Falha ao consultar Ollama: %s", exc)
            return "Não consegui acessar o modelo local no momento."
