def register(registry):
    def handle_status(command: str) -> str:
        return "Jarvis operacional: escuta contínua ativa, memória persistente e engenharia com aprovação habilitada."

    registry.register("status", handle_status)
