from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from math import log
from typing import Literal


BitVector = tuple[int, ...]
FaultType = Literal["data", "measurement"]


@dataclass(frozen=True)
class MatchingEdge:
    """A weighted fault edge in a QEC matching graph.

    The endpoints are syndrome or detection-event nodes. Boundary endpoints are
    included explicitly so the same structure can describe both bulk faults and
    faults that terminate at a spatial or temporal boundary.
    """

    node1: str
    node2: str
    fault_id: str
    fault_type: FaultType
    probability: float
    weight: float

    @property
    def endpoints(self) -> tuple[str, str]:
        return self.node1, self.node2


@dataclass(frozen=True)
class MatchingGraph:
    """A small dependency-free matching-graph representation.

    This is intentionally not a replacement for PyMatching. It is a mathematical
    and testing scaffold: it makes explicit which physical faults produce which
    syndrome or detection-event boundaries.
    """

    nodes: tuple[str, ...]
    boundary_nodes: tuple[str, ...]
    edges: tuple[MatchingEdge, ...]

    @property
    def finite_nodes(self) -> tuple[str, ...]:
        boundaries = set(self.boundary_nodes)
        return tuple(node for node in self.nodes if node not in boundaries)

    def edge_by_fault_id(self, fault_id: str) -> MatchingEdge:
        for edge in self.edges:
            if edge.fault_id == fault_id:
                return edge
        raise KeyError(f"unknown fault id: {fault_id}")

    def defect_nodes(self, fault_ids: Iterable[str]) -> tuple[str, ...]:
        """Return the non-boundary nodes incident to an odd number of faults."""

        boundary_nodes = set(self.boundary_nodes)
        parity: dict[str, int] = {node: 0 for node in self.finite_nodes}
        for fault_id in fault_ids:
            edge = self.edge_by_fault_id(fault_id)
            for node in edge.endpoints:
                if node not in boundary_nodes:
                    parity[node] ^= 1
        return tuple(node for node in self.finite_nodes if parity[node])

    def to_weighted_edge_list(self) -> tuple[tuple[str, str, float], ...]:
        """Return an edge list suitable for inspection or adapter code."""

        return tuple((edge.node1, edge.node2, edge.weight) for edge in self.edges)


def log_odds_weight(probability: float) -> float:
    """Return the log-likelihood edge weight log((1-p)/p)."""

    _validate_strict_probability(probability)
    return log((1 - probability) / probability)


def repetition_parity_check_matrix(distance: int) -> tuple[BitVector, ...]:
    """Return the adjacent-check parity-check matrix of the repetition code."""

    _validate_repetition_distance(distance)
    return tuple(
        tuple(int(column == row or column == row + 1) for column in range(distance))
        for row in range(distance - 1)
    )


def matrix_syndrome(check_matrix: Sequence[Sequence[int]], error: BitVector) -> BitVector:
    """Compute H error over F_2 for a binary parity-check matrix H."""

    _validate_bit_vector(error)
    syndrome = []
    for row in check_matrix:
        if len(row) != len(error):
            raise ValueError("each parity-check row must match the error length")
        if any(entry not in (0, 1) for entry in row):
            raise ValueError("parity-check entries must be bits")
        syndrome.append(sum(entry * bit for entry, bit in zip(row, error)) % 2)
    return tuple(syndrome)


def build_repetition_matching_graph(
    distance: int,
    physical_error_rate: float,
) -> MatchingGraph:
    """Build the 1D matching graph for perfect syndrome measurements.

    A bit flip on an interior qubit creates two adjacent syndrome defects. A bit
    flip on an endpoint qubit creates one defect and terminates at a spatial
    boundary. This is the 1D version of the matching-graph construction used by
    MWPM decoders.
    """

    _validate_repetition_distance(distance)
    weight = log_odds_weight(physical_error_rate)
    check_nodes = tuple(f"c{check}" for check in range(distance - 1))
    boundary_nodes = ("left_boundary", "right_boundary")
    edges = []
    for qubit in range(distance):
        if qubit == 0:
            node1, node2 = "left_boundary", "c0"
        elif qubit == distance - 1:
            node1, node2 = f"c{distance - 2}", "right_boundary"
        else:
            node1, node2 = f"c{qubit - 1}", f"c{qubit}"
        edges.append(
            MatchingEdge(
                node1=node1,
                node2=node2,
                fault_id=f"x{qubit}",
                fault_type="data",
                probability=physical_error_rate,
                weight=weight,
            )
        )
    return MatchingGraph(
        nodes=boundary_nodes + check_nodes,
        boundary_nodes=boundary_nodes,
        edges=tuple(edges),
    )


def build_phenomenological_repetition_matching_graph(
    distance: int,
    rounds: int,
    physical_error_rate: float,
    measurement_error_rate: float,
) -> MatchingGraph:
    """Build a 1+1 dimensional matching graph for noisy syndrome measurements.

    Finite nodes are detection events indexed by measurement round and check
    position. Data errors create horizontal edges in a fixed round. Measurement
    errors create vertical edges between consecutive detection-event rounds, or
    terminate at a temporal boundary in the last round.
    """

    _validate_repetition_distance(distance)
    if rounds <= 0:
        raise ValueError("rounds must be positive")
    data_weight = log_odds_weight(physical_error_rate)
    measurement_weight = log_odds_weight(measurement_error_rate)

    detection_nodes = tuple(
        _detection_node(round_index, check)
        for round_index in range(rounds)
        for check in range(distance - 1)
    )
    boundary_nodes = tuple(
        [
            *(f"left_boundary:t{round_index}" for round_index in range(rounds)),
            *(f"right_boundary:t{round_index}" for round_index in range(rounds)),
            *(f"time_boundary:c{check}" for check in range(distance - 1)),
        ]
    )

    edges: list[MatchingEdge] = []
    for round_index in range(rounds):
        for qubit in range(distance):
            if qubit == 0:
                node1 = f"left_boundary:t{round_index}"
                node2 = _detection_node(round_index, 0)
            elif qubit == distance - 1:
                node1 = _detection_node(round_index, distance - 2)
                node2 = f"right_boundary:t{round_index}"
            else:
                node1 = _detection_node(round_index, qubit - 1)
                node2 = _detection_node(round_index, qubit)
            edges.append(
                MatchingEdge(
                    node1=node1,
                    node2=node2,
                    fault_id=f"data:t{round_index}:q{qubit}",
                    fault_type="data",
                    probability=physical_error_rate,
                    weight=data_weight,
                )
            )

    for round_index in range(rounds):
        for check in range(distance - 1):
            node1 = _detection_node(round_index, check)
            node2 = (
                _detection_node(round_index + 1, check)
                if round_index + 1 < rounds
                else f"time_boundary:c{check}"
            )
            edges.append(
                MatchingEdge(
                    node1=node1,
                    node2=node2,
                    fault_id=f"measurement:t{round_index}:c{check}",
                    fault_type="measurement",
                    probability=measurement_error_rate,
                    weight=measurement_weight,
                )
            )

    return MatchingGraph(
        nodes=boundary_nodes + detection_nodes,
        boundary_nodes=boundary_nodes,
        edges=tuple(edges),
    )


def _detection_node(round_index: int, check: int) -> str:
    return f"d:t{round_index}:c{check}"


def _validate_repetition_distance(distance: int) -> None:
    if distance < 3:
        raise ValueError("distance must be at least 3")
    if distance % 2 == 0:
        raise ValueError("distance must be odd")


def _validate_bit_vector(vector: BitVector) -> None:
    if any(bit not in (0, 1) for bit in vector):
        raise ValueError("vector entries must be bits")


def _validate_strict_probability(probability: float) -> None:
    if not 0 < probability < 1:
        raise ValueError("probability must be strictly between 0 and 1 for log-odds weights")
