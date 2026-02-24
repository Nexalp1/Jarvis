from __future__ import annotations

import pyttsx3


class Speaker:
    def __init__(self, language: str = "pt-BR") -> None:
        self.engine = pyttsx3.init()
        self.language = language

    def say(self, text: str) -> None:
        self.engine.say(text)
        self.engine.runAndWait()
