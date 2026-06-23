from itertools import product
from importlib.util import find_spec
import unittest

from qec_lab import RepetitionCode
from qec_lab import build_phenomenological_repetition_matching_graph
from qec_lab import build_pymatching_model
from qec_lab import decode_phenomenological_detection_events
from qec_lab import decode_repetition_syndrome


HAS_PYMATCHING = find_spec("pymatching") is not None


@unittest.skipUnless(HAS_PYMATCHING, "PyMatching is an optional dependency")
class PyMatchingAdapterTest(unittest.TestCase):
    def test_repetition_decoder_agrees_with_minimum_weight_decoder(self) -> None:
        distance = 5
        code = RepetitionCode(distance)
        for error in product((0, 1), repeat=distance):
            syndrome = code.syndrome(error)
            fault_ids = decode_repetition_syndrome(
                syndrome=syndrome,
                physical_error_rate=0.1,
            )
            correction = tuple(int(f"x{qubit}" in fault_ids) for qubit in range(distance))
            self.assertEqual(correction, code.decode_minimum_weight(syndrome))

    def test_phenomenological_measurement_fault_is_decoded(self) -> None:
        fault_ids = decode_phenomenological_detection_events(
            detection_events=((1, 0), (1, 0)),
            physical_error_rate=0.001,
            measurement_error_rate=0.2,
        )
        self.assertEqual(fault_ids, ("measurement:t0:c0",))

    def test_model_bookkeeping_round_trips_nodes_and_faults(self) -> None:
        graph = build_phenomenological_repetition_matching_graph(
            distance=3,
            rounds=2,
            physical_error_rate=0.05,
            measurement_error_rate=0.05,
        )
        model = build_pymatching_model(graph)
        self.assertEqual(model.syndrome_vector(("d:t0:c0", "d:t1:c1")), (1, 0, 0, 1))
        self.assertIn("data:t0:q0", model.fault_id_to_index)
        self.assertIn("measurement:t1:c1", model.fault_id_to_index)


if __name__ == "__main__":
    unittest.main()
