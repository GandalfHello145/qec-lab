import random
import unittest

from qec_lab import PhenomenologicalRepetitionExperiment


class PhenomenologicalExperimentTest(unittest.TestCase):
    def test_zero_noise_sample_has_no_detection_events(self) -> None:
        experiment = PhenomenologicalRepetitionExperiment(distance=5, rounds=3)
        sample = experiment.sample(
            physical_error_rate=0.0,
            measurement_error_rate=0.0,
            rng=random.Random(1),
        )
        self.assertEqual(sample.final_state, (0, 0, 0, 0, 0))
        self.assertEqual(sample.data_errors, ((0, 0, 0, 0, 0),) * 3)
        self.assertEqual(sample.true_syndromes, ((0, 0, 0, 0),) * 3)
        self.assertEqual(sample.measured_syndromes, ((0, 0, 0, 0),) * 3)
        self.assertEqual(sample.detection_events, ((0, 0, 0, 0),) * 3)
        self.assertFalse(sample.uncorrected_logical_failure)

    def test_data_errors_change_true_syndrome(self) -> None:
        experiment = PhenomenologicalRepetitionExperiment(distance=3, rounds=1)
        sample = experiment.sample(
            physical_error_rate=1.0,
            measurement_error_rate=0.0,
            rng=random.Random(1),
        )
        self.assertEqual(sample.final_state, (1, 1, 1))
        self.assertEqual(sample.true_syndromes, ((0, 0),))
        self.assertTrue(sample.uncorrected_logical_failure)

    def test_measurement_error_can_create_detection_event_without_data_error(self) -> None:
        experiment = PhenomenologicalRepetitionExperiment(distance=3, rounds=1)
        sample = experiment.sample(
            physical_error_rate=0.0,
            measurement_error_rate=1.0,
            rng=random.Random(1),
        )
        self.assertEqual(sample.final_state, (0, 0, 0))
        self.assertEqual(sample.true_syndromes, ((0, 0),))
        self.assertEqual(sample.measured_syndromes, ((1, 1),))
        self.assertEqual(sample.detection_events, ((1, 1),))


if __name__ == "__main__":
    unittest.main()
