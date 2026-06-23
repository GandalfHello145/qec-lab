from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from qec_lab.matching import (
    MatchingGraph,
    build_phenomenological_repetition_matching_graph,
    build_repetition_matching_graph,
)
from qec_lab.phenomenological import PhenomenologicalSample
from qec_lab.repetition import BitVector


class PyMatchingNotInstalledError(ImportError):
    """Raised when PyMatching-dependent functionality is used without PyMatching."""


@dataclass(frozen=True)
class PyMatchingModel:
    """Bookkeeping data for a PyMatching object built from a QEC-Lab graph."""

    matching: Any
    node_to_index: dict[str, int]
    index_to_node: dict[int, str]
    fault_id_to_index: dict[str, int]
    index_to_fault_id: dict[int, str]

    def syndrome_vector(self, defect_nodes: set[str] | frozenset[str] | tuple[str, ...]) -> BitVector:
        defect_set = set(defect_nodes)
        unknown = defect_set.difference(self.node_to_index)
        if unknown:
            raise ValueError(f"unknown defect nodes: {sorted(unknown)}")
        return tuple(
            int(self.index_to_node[index] in defect_set)
            for index in range(len(self.index_to_node))
        )

    def decode(self, defect_nodes: set[str] | frozenset[str] | tuple[str, ...]) -> tuple[str, ...]:
        correction = self.matching.decode(list(self.syndrome_vector(defect_nodes)))
        return tuple(
            self.index_to_fault_id[index]
            for index, bit in enumerate(correction)
            if bit and index in self.index_to_fault_id
        )


def build_pymatching_model(graph: MatchingGraph) -> PyMatchingModel:
    """Convert a QEC-Lab `MatchingGraph` into a `pymatching.Matching` object.

    The conversion uses PyMatching's virtual-boundary convention: if a QEC-Lab
    edge has one finite endpoint and one boundary endpoint, it becomes a
    PyMatching boundary edge. If both endpoints are finite, it becomes an
    ordinary graph edge.
    """

    pymatching = _import_pymatching()
    matching = pymatching.Matching()

    node_to_index = {
        node: index
        for index, node in enumerate(graph.finite_nodes)
    }
    index_to_node = {index: node for node, index in node_to_index.items()}
    fault_id_to_index = {
        edge.fault_id: index
        for index, edge in enumerate(graph.edges)
    }
    index_to_fault_id = {index: fault_id for fault_id, index in fault_id_to_index.items()}
    boundary_nodes = set(graph.boundary_nodes)

    for edge in graph.edges:
        finite_endpoints = [
            endpoint for endpoint in edge.endpoints
            if endpoint not in boundary_nodes
        ]
        fault_index = fault_id_to_index[edge.fault_id]
        if len(finite_endpoints) == 1:
            matching.add_boundary_edge(
                node_to_index[finite_endpoints[0]],
                fault_ids=fault_index,
                weight=edge.weight,
                error_probability=edge.probability,
                merge_strategy="smallest-weight",
            )
        elif len(finite_endpoints) == 2:
            matching.add_edge(
                node_to_index[finite_endpoints[0]],
                node_to_index[finite_endpoints[1]],
                fault_ids=fault_index,
                weight=edge.weight,
                error_probability=edge.probability,
                merge_strategy="smallest-weight",
            )
        else:
            raise ValueError(
                "each matching edge must have one or two finite detector endpoints"
            )

    matching.ensure_num_fault_ids(len(fault_id_to_index))
    return PyMatchingModel(
        matching=matching,
        node_to_index=node_to_index,
        index_to_node=index_to_node,
        fault_id_to_index=fault_id_to_index,
        index_to_fault_id=index_to_fault_id,
    )


def decode_repetition_syndrome(
    syndrome: BitVector,
    physical_error_rate: float,
) -> tuple[str, ...]:
    """Decode a perfect-measurement repetition-code syndrome with PyMatching."""

    graph = build_repetition_matching_graph(
        distance=len(syndrome) + 1,
        physical_error_rate=physical_error_rate,
    )
    model = build_pymatching_model(graph)
    defect_nodes = tuple(
        f"c{check}" for check, bit in enumerate(syndrome) if bit
    )
    return model.decode(defect_nodes)


def decode_phenomenological_detection_events(
    detection_events: tuple[BitVector, ...],
    physical_error_rate: float,
    measurement_error_rate: float,
) -> tuple[str, ...]:
    """Decode repeated syndrome-difference data with a 1+1D PyMatching graph."""

    if not detection_events:
        raise ValueError("at least one detection-event round is required")
    check_count = len(detection_events[0])
    if check_count == 0:
        raise ValueError("detection-event rounds must contain at least one check")
    if any(len(round_events) != check_count for round_events in detection_events):
        raise ValueError("all detection-event rounds must have the same length")

    graph = build_phenomenological_repetition_matching_graph(
        distance=check_count + 1,
        rounds=len(detection_events),
        physical_error_rate=physical_error_rate,
        measurement_error_rate=measurement_error_rate,
    )
    model = build_pymatching_model(graph)
    defect_nodes = tuple(
        f"d:t{round_index}:c{check}"
        for round_index, round_events in enumerate(detection_events)
        for check, bit in enumerate(round_events)
        if bit
    )
    return model.decode(defect_nodes)


def decode_phenomenological_sample(sample: PhenomenologicalSample) -> tuple[str, ...]:
    """Decode a `PhenomenologicalSample` using PyMatching."""

    return decode_phenomenological_detection_events(
        detection_events=sample.detection_events,
        physical_error_rate=sample.physical_error_rate,
        measurement_error_rate=sample.measurement_error_rate,
    )


def _import_pymatching() -> Any:
    try:
        import pymatching  # type: ignore[import-not-found]
    except ImportError as error:
        raise PyMatchingNotInstalledError(
            "PyMatching is required for this function. Install it with "
            "`pip install -e .[matching]` or `pip install pymatching`."
        ) from error
    return pymatching
