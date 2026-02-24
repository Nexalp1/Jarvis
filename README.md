# JARVIS

Arquitetura modular de assistente pessoal com foco em operação offline-first, interação em pt-BR e auto-melhoria segura baseada em aprovação explícita.

## Estrutura

- `core/`: orquestração central e registro dinâmico de skills.
- `voice/`: captura contínua de voz (Vosk/sounddevice) e síntese (pyttsx3).
- `brain/`: cliente LLM local via Ollama.
- `memory/`: persistência SQLite para contexto, preferências e histórico de engenharia.
- `engineer/`: agente de engenharia para proposta de melhorias com workflow seguro.
- `skills/`: plugins carregados automaticamente.
- `system/`: integração com sistema operacional (autostart Windows).
- `config/`: identidade e parâmetros de execução.
- `logs/`: logs de execução.

## Segurança de auto-melhoria

Nenhuma auto-modificação é aplicada automaticamente.
Toda mudança deve seguir:
1. proposta
2. resumo
3. aprovação explícita
4. backup
5. aplicação segura
