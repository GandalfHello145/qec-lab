from itertools import product
from math import log
import unittest

from qec_lab import (
    RepetitionCode,
    build_phenomenological_repetition_matching_graph,
    build_repetition_matching_graph,
    log_odds_weight,
    matrix_syndrome,
    repetition_parity_check_matrix,
)


class MatchingGraphTest(unittest.TestCase):
    def test_log_odds_weight(self) -> None:
        self.assertAlmostEqual(log_odds_weight(0.1), log(9.0))
        self.assertAlmostEqual(log_odds_weight(0.5), 0.0)

    def test_repetition_parity_check_matrix(self) -> None:
        self.assertEqual(
            repetition_parity_check_matrix(5),
            (
                (1, 1, 0, 0, 0),
                (0, 1, 1, 0, 0),
                (0, 0, 1, 1, 0),
                (0, 0, 0, 1, 1),
            ),
        )

    def test_matrix_syndrome_agrees_with_repetition_code(self) -> None:
        distance = 5
        code = RepetitionCode(distance=distance)
        check_matrix = repetition_parity_check_matrix(distance)
        for error in product((0, 1), repeat=distance):
            self.assertEqual(matrix_syndrome(check_matrix, error), code.syndrome(error))

    def test_matching_graph_boundary_agrees_with_syndrome(self) -> None:
        distance = 5
        code = RepetitionCode(distance=distance)
        graph = build_repetition_matching_graph(distance, physical_error_rate=0.1)
        for error in product((0, 1), repeat=distance):
            fault_ids = [f"x{index}" for index, bit in enumerate(error) if bit]
            defect_nodes = set(graph.defect_nodes(fault_ids))
            syndrome_from_graph = tuple(
                int(f"c{check}" in defect_nodes)
                for check in range(distance - 1)
            )
            self.assertEqual(syndrome_from_graph, code.syndrome(error))

    def test_phenomenological_matching_graph_shape(self) -> None:
        graph = build_phenomenological_repetition_matching_graph(
            distance=5,
            rounds=3,
            physical_error_rate=0.1,
            measurement_error_rate=0.05,
        )
        self.assertEqual(len(graph.finite_nodes), 3 * 4)
        self.assertEqual(len(graph.edges), 3 * 5 + 3 * 4)
        self.assertIn("d:t0:c0", graph.finite_nodes)
        self.assertIn("time_boundary:c0", graph.boundary_nodes)
        self.assertEqual(
            graph.edge_by_fault_id("measurement:t2:c0").endpoints,
            ("d:t2:c0", "time_boundary:c0"),
        )


if __name__ == "__main__":
    unittest.main()
