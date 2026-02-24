from __future__ import annotations

import logging
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from engineer.workflow import ImprovementProposal
from memory.store import MemoryStore

logger = logging.getLogger(__name__)


class EngineeringAgent:
    """Safe self-improvement controller with approval-gated application."""

    def __init__(self, memory: MemoryStore, backup_dir: str, proposals_dir: str) -> None:
        self.memory = memory
        self.backup_dir = Path(backup_dir)
        self.proposals_dir = Path(proposals_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.proposals_dir.mkdir(parents=True, exist_ok=True)

    def analyze_logs(self, log_path: str) -> str:
        path = Path(log_path)
        if not path.exists():
            return "Sem logs disponíveis para análise."
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        error_count = sum(1 for line in lines if "ERROR" in line or "Exception" in line)
        warn_count = sum(1 for line in lines if "WARNING" in line)
        return f"Análise de logs: {error_count} erros e {warn_count} alertas nas últimas {len(lines)} linhas."

    def propose(self, objective: str) -> str:
        now = datetime.now().strftime("%Y%m%d-%H%M%S")
        proposal = ImprovementProposal(
            proposal_id=now,
            summary=f"Proposta para: {objective}",
            analysis="Sugestão automática baseada em padrões de manutenção e estabilidade.",
            patch_diff="# Gere diff com ferramenta interna antes de aplicar",
        )
        file = self.proposals_dir / f"proposal-{proposal.proposal_id}.md"
        file.write_text(
            "\n".join(
                [
                    f"# {proposal.summary}",
                    "",
                    "## Análise",
                    proposal.analysis,
                    "",
                    "## Patch sugerido",
                    proposal.patch_diff,
                    "",
                    "## Status",
                    "Aguardando aprovação explícita do usuário.",
                ]
            ),
            encoding="utf-8",
        )
        self.memory.save_engineering_action("proposal_created", proposal.summary, approved=False)
        return (
            f"Proposta criada ({proposal.proposal_id}). "
            "Nenhuma alteração foi aplicada. Diga 'aprovar proposta <id>' para permitir aplicação segura."
        )

    def apply_patch_with_approval(self, proposal_id: str, approved: bool, repo_path: str = ".") -> str:
        if not approved:
            self.memory.save_engineering_action("proposal_rejected", proposal_id, approved=False)
            return "Aplicação cancelada. Nenhum arquivo foi alterado."

        proposal_file = self.proposals_dir / f"proposal-{proposal_id}.md"
        if not proposal_file.exists():
            return "Proposta não encontrada."

        backup_file = self.backup_dir / f"backup-{proposal_id}.zip"
        shutil.make_archive(str(backup_file.with_suffix("")), "zip", repo_path)

        self.memory.save_engineering_action(
            "proposal_approved",
            f"{proposal_id} com backup em {backup_file}",
            approved=True,
        )
        logger.info("Backup criado: %s", backup_file)

        return (
            "Aprovação registrada e backup criado. "
            "Aplicação automática de patch não executada neste scaffold sem diff validado."
        )

    def generate_patch(self, instructions: str, repo_path: str = ".") -> str:
        """Hook para geração de patch usando git diff local ou agente futuro."""
        result = subprocess.run(
            ["git", "-C", repo_path, "diff", "--", "."],
            check=False,
            capture_output=True,
            text=True,
        )
        diff = result.stdout.strip()
        return diff or f"Nenhum diff local disponível. Instruções recebidas: {instructions}"
