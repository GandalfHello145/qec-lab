from itertools import product
import random
import unittest

from qec_lab import RepetitionCode, SimulationResult


class RepetitionCodeTest(unittest.TestCase):
    def test_syndrome_marks_boundaries_between_flipped_runs(self) -> None:
        code = RepetitionCode(distance=5)
        self.assertEqual(code.syndrome((0, 0, 1, 1, 0)), (0, 1, 0, 1))

    def test_decoder_returns_minimum_weight_correction(self) -> None:
        code = RepetitionCode(distance=5)
        self.assertEqual(code.decode((0, 1, 1, 0)), (0, 0, 1, 0, 0))
        self.assertEqual(code.decode_minimum_weight((0, 1, 1, 0)), (0, 0, 1, 0, 0))

    def test_maximum_likelihood_decoder_depends_on_physical_error_rate(self) -> None:
        code = RepetitionCode(distance=5)
        self.assertEqual(code.decode_maximum_likelihood((0, 0, 0, 0), 0.25), (0, 0, 0, 0, 0))
        self.assertEqual(code.decode_maximum_likelihood((0, 0, 0, 0), 0.75), (1, 1, 1, 1, 1))

    def test_single_error_is_corrected(self) -> None:
        code = RepetitionCode(distance=5)
        noisy_state = (0, 0, 1, 0, 0)
        correction = code.decode(code.syndrome(noisy_state))
        corrected = tuple(bit ^ fix for bit, fix in zip(noisy_state, correction))
        self.assertEqual(corrected, code.encode(0))

    def test_exhaustive_minimum_weight_decoder_failure_condition(self) -> None:
        for distance in (3, 5, 7):
            code = RepetitionCode(distance=distance)
            zero = tuple(0 for _ in range(distance))
            one = tuple(1 for _ in range(distance))
            for error in product((0, 1), repeat=distance):
                syndrome = code.syndrome(error)
                correction = code.decode_minimum_weight(syndrome)
                residual = tuple(bit ^ fix for bit, fix in zip(error, correction))
                self.assertIn(residual, (zero, one))
                self.assertEqual(residual == one, sum(error) > distance // 2)

    def test_exact_logical_error_rate_matches_closed_form(self) -> None:
        code = RepetitionCode(distance=5)
        self.assertAlmostEqual(code.exact_logical_error_rate(0.08), 0.0045252608)

    def test_exact_logical_error_rate_for_ml_decoder_above_half(self) -> None:
        code = RepetitionCode(distance=3)
        self.assertAlmostEqual(
            code.exact_logical_error_rate(0.75, decoder="maximum-likelihood"),
            0.15625,
        )

    def test_logical_failure_rate_is_reproducible(self) -> None:
        code = RepetitionCode(distance=5)
        result = code.estimate_logical_error_rate(
            physical_error_rate=0.1,
            trials=200,
            seed=123,
        )
        self.assertEqual(result.logical_failures, 2)
        self.assertAlmostEqual(result.logical_error_rate, 0.01)
        self.assertAlmostEqual(result.exact_logical_error_rate, 0.00856)

    def test_wilson_interval_contains_observed_rate(self) -> None:
        result = SimulationResult(
            distance=5,
            physical_error_rate=0.1,
            trials=200,
            logical_failures=2,
        )
        ci_low, ci_high = result.wilson_confidence_interval()
        self.assertLess(ci_low, result.logical_error_rate)
        self.assertLess(result.logical_error_rate, ci_high)
        self.assertGreaterEqual(ci_low, 0)
        self.assertLessEqual(ci_high, 1)

    def test_invalid_distance_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "odd"):
            RepetitionCode(distance=4)

    def test_noise_model_uses_supplied_rng(self) -> None:
        code = RepetitionCode(distance=3)
        rng = random.Random(1)
        self.assertEqual(code.apply_bit_flip_noise((0, 0, 0), 0.5, rng), (1, 0, 0))

    def test_noisy_syndrome_rounds_and_detection_events(self) -> None:
        code = RepetitionCode(distance=5)
        rounds = code.sample_syndrome_rounds(
            state=(0, 1, 1, 0, 0),
            measurement_error_rate=0.0,
            rounds=2,
            rng=random.Random(1),
        )
        self.assertEqual(rounds, ((1, 0, 1, 0), (1, 0, 1, 0)))
        self.assertEqual(
            code.detection_events(rounds),
            ((1, 0, 1, 0), (0, 0, 0, 0)),
        )


if __name__ == "__main__":
    unittest.main()
