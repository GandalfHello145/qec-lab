"""Quantum error correction simulation tools."""

from qec_lab.matching import MatchingEdge, MatchingGraph
from qec_lab.matching import build_phenomenological_repetition_matching_graph
from qec_lab.matching import build_repetition_matching_graph
from qec_lab.matching import log_odds_weight, matrix_syndrome
from qec_lab.matching import repetition_parity_check_matrix
from qec_lab.phenomenological import PhenomenologicalRepetitionExperiment
from qec_lab.phenomenological import PhenomenologicalSample
from qec_lab.repetition import RepetitionCode, SimulationResult

__all__ = [
    "MatchingEdge",
    "MatchingGraph",
    "PhenomenologicalRepetitionExperiment",
    "PhenomenologicalSample",
    "RepetitionCode",
    "SimulationResult",
    "build_phenomenological_repetition_matching_graph",
    "build_repetition_matching_graph",
    "log_odds_weight",
    "matrix_syndrome",
    "repetition_parity_check_matrix",
]
