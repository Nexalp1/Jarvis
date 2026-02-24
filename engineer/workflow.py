from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ImprovementProposal:
    proposal_id: str
    summary: str
    analysis: str
    patch_diff: str
    requires_approval: bool = True
