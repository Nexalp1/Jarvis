from __future__ import annotations

import json
import logging
import queue
from dataclasses import dataclass
from pathlib import Path
from typing import Generator

import sounddevice as sd
from vosk import KaldiRecognizer, Model

logger = logging.getLogger(__name__)


@dataclass
class ListenerConfig:
    sample_rate: int
    channels: int
    block_size: int
    vosk_model_path: str


class ContinuousListener:
    def __init__(self, cfg: ListenerConfig) -> None:
        self.cfg = cfg
        model_dir = Path(cfg.vosk_model_path)
        if not model_dir.exists():
            raise FileNotFoundError(
                f"Modelo Vosk não encontrado em {model_dir}. Ajuste voice.vosk_model_path no config."
            )
        self.model = Model(str(model_dir))
        self.recognizer = KaldiRecognizer(self.model, cfg.sample_rate)
        self.audio_queue: queue.Queue[bytes] = queue.Queue()

    def _audio_callback(self, indata, frames, time, status) -> None:  # noqa: ANN001
        if status:
            logger.warning("Status do áudio: %s", status)
        self.audio_queue.put(bytes(indata))

    def listen(self) -> Generator[str, None, None]:
        with sd.RawInputStream(
            samplerate=self.cfg.sample_rate,
            blocksize=self.cfg.block_size,
            device=None,
            dtype="int16",
            channels=self.cfg.channels,
            callback=self._audio_callback,
        ):
            logger.info("Escuta contínua ativada")
            while True:
                data = self.audio_queue.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    transcript = result.get("text", "").strip()
                    if transcript:
                        logger.info("Transcrição: %s", transcript)
                        yield transcript
