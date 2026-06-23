"""Quantum error correction simulation tools."""

from qec_lab.css import CSSCode, CSSSyndrome, SingleQubitError
from qec_lab.css import bit_flip_repetition_css_code, shor_code, steane_code
from qec_lab.matching import MatchingEdge, MatchingGraph
from qec_lab.matching import build_phenomenological_repetition_matching_graph
from qec_lab.matching import build_repetition_matching_graph
from qec_lab.matching import log_odds_weight, matrix_syndrome
from qec_lab.matching import repetition_parity_check_matrix
from qec_lab.phenomenological import PhenomenologicalRepetitionExperiment
from qec_lab.phenomenological import PhenomenologicalSample
from qec_lab.repetition import RepetitionCode, SimulationResult

__all__ = [
    "CSSCode",
    "CSSSyndrome",
    "MatchingEdge",
    "MatchingGraph",
    "PhenomenologicalRepetitionExperiment",
    "PhenomenologicalSample",
    "RepetitionCode",
    "SimulationResult",
    "SingleQubitError",
    "bit_flip_repetition_css_code",
    "build_phenomenological_repetition_matching_graph",
    "build_repetition_matching_graph",
    "log_odds_weight",
    "matrix_syndrome",
    "repetition_parity_check_matrix",
    "shor_code",
    "steane_code",
]
