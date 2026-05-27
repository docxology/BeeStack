"""Typed connectome graph model for BeeBrain structural and functional wiring."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

ConnectomeNodeKind = Literal["neuropil", "neuron", "tract"]
ConnectomeEdgeKind = Literal["structural_tract", "functional_granger", "synaptic"]
ConnectomeTier = Literal["structural_projectome", "functional_partial", "synaptic_unavailable"]


@dataclass(frozen=True)
class ConnectomeNode:
    node_id: str
    kind: ConnectomeNodeKind
    label: str
    module_target: str
    source_asset: str
    provenance_doi: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ConnectomeEdge:
    source_id: str
    target_id: str
    edge_kind: ConnectomeEdgeKind
    weight: float | None
    evidence: str

    def as_dict(self) -> dict[str, str | float | None]:
        return asdict(self)


@dataclass(frozen=True)
class BeeBrainConnectomeReport:
    tier: ConnectomeTier
    nodes: tuple[ConnectomeNode, ...]
    edges: tuple[ConnectomeEdge, ...]
    completeness: dict[str, float]

    def as_dict(self) -> dict[str, object]:
        return {
            "tier": self.tier,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "nodes": [node.as_dict() for node in self.nodes],
            "edges": [edge.as_dict() for edge in self.edges],
            "completeness": self.completeness,
        }
