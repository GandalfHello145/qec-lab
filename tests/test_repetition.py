import random
import unittest

from qec_lab import RepetitionCode


class RepetitionCodeTest(unittest.TestCase):
    def test_syndrome_marks_boundaries_between_flipped_runs(self) -> None:
        code = RepetitionCode(distance=5)
        self.assertEqual(code.syndrome((0, 0, 1, 1, 0)), (0, 1, 0, 1))

    def test_decoder_returns_minimum_weight_correction(self) -> None:
        code = RepetitionCode(distance=5)
        self.assertEqual(code.decode((0, 1, 1, 0)), (0, 0, 1, 0, 0))

    def test_single_error_is_corrected(self) -> None:
        code = RepetitionCode(distance=5)
        noisy_state = (0, 0, 1, 0, 0)
        correction = code.decode(code.syndrome(noisy_state))
        corrected = tuple(bit ^ fix for bit, fix in zip(noisy_state, correction))
        self.assertEqual(corrected, code.encode(0))

    def test_logical_failure_rate_is_reproducible(self) -> None:
        code = RepetitionCode(distance=5)
        result = code.estimate_logical_error_rate(
            physical_error_rate=0.1,
            trials=200,
            seed=123,
        )
        self.assertEqual(result.logical_failures, 2)
        self.assertAlmostEqual(result.logical_error_rate, 0.01)

    def test_invalid_distance_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "odd"):
            RepetitionCode(distance=4)

    def test_noise_model_uses_supplied_rng(self) -> None:
        code = RepetitionCode(distance=3)
        rng = random.Random(1)
        self.assertEqual(code.apply_bit_flip_noise((0, 0, 0), 0.5, rng), (1, 0, 0))


if __name__ == "__main__":
    unittest.main()
