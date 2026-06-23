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
from qec_lab.pymatching_adapter import PyMatchingModel, PyMatchingNotInstalledError
from qec_lab.pymatching_adapter import PyMatchingPhenomenologicalResult
from qec_lab.pymatching_adapter import build_pymatching_model
from qec_lab.pymatching_adapter import correct_final_state_with_decoded_faults
from qec_lab.pymatching_adapter import decode_phenomenological_detection_events
from qec_lab.pymatching_adapter import decode_phenomenological_sample
from qec_lab.pymatching_adapter import decode_repetition_syndrome
from qec_lab.pymatching_adapter import estimate_phenomenological_logical_error_rate_with_pymatching
from qec_lab.pymatching_adapter import run_phenomenological_trial_with_pymatching
from qec_lab.repetition import RepetitionCode, SimulationResult

__all__ = [
    "CSSCode",
    "CSSSyndrome",
    "MatchingEdge",
    "MatchingGraph",
    "PhenomenologicalRepetitionExperiment",
    "PhenomenologicalSample",
    "PyMatchingModel",
    "PyMatchingNotInstalledError",
    "PyMatchingPhenomenologicalResult",
    "RepetitionCode",
    "SimulationResult",
    "SingleQubitError",
    "bit_flip_repetition_css_code",
    "build_phenomenological_repetition_matching_graph",
    "build_pymatching_model",
    "build_repetition_matching_graph",
    "correct_final_state_with_decoded_faults",
    "decode_phenomenological_detection_events",
    "decode_phenomenological_sample",
    "decode_repetition_syndrome",
    "estimate_phenomenological_logical_error_rate_with_pymatching",
    "log_odds_weight",
    "matrix_syndrome",
    "repetition_parity_check_matrix",
    "run_phenomenological_trial_with_pymatching",
    "shor_code",
    "steane_code",
]
