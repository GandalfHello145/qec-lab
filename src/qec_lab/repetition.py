from __future__ import annotations

from dataclasses import dataclass
import random


BitVector = tuple[int, ...]


@dataclass(frozen=True)
class SimulationResult:
    """Summary of a Monte Carlo logical-error-rate experiment."""

    distance: int
    physical_error_rate: float
    trials: int
    logical_failures: int

    @property
    def logical_error_rate(self) -> float:
        return self.logical_failures / self.trials


class RepetitionCode:
    """Odd-length bit-flip repetition code.

    The code protects one classical bit, or the computational-basis part of a
    logical qubit, by encoding it across an odd number of physical qubits. Its
    stabilizer checks are adjacent parity checks Z_i Z_{i+1}; in this simplified
    bit-flip model, a nonzero syndrome reveals boundaries between flipped and
    unflipped runs.
    """

    def __init__(self, distance: int) -> None:
        if distance < 3:
            raise ValueError("distance must be at least 3")
        if distance % 2 == 0:
            raise ValueError("distance must be odd for majority decoding")
        self.distance = distance

    def encode(self, logical_bit: int) -> BitVector:
        self._validate_bit(logical_bit)
        return tuple(logical_bit for _ in range(self.distance))

    def apply_bit_flip_noise(
        self, state: BitVector, physical_error_rate: float, rng: random.Random
    ) -> BitVector:
        self._validate_state(state)
        self._validate_probability(physical_error_rate)
        return tuple(
            bit ^ int(rng.random() < physical_error_rate)
            for bit in state
        )

    def syndrome(self, state: BitVector) -> BitVector:
        self._validate_state(state)
        return tuple(state[index] ^ state[index + 1] for index in range(self.distance - 1))

    def decode(self, syndrome: BitVector) -> BitVector:
        """Return a minimum-weight correction matching the syndrome.

        For a 1D repetition code, a syndrome uniquely fixes an error pattern up
        to multiplication by the logical operator. We compare both candidates:
        one beginning with no error and one beginning with an error. The
        lower-weight candidate is the maximum-likelihood correction under
        independent noise below p=0.5.
        """

        if len(syndrome) != self.distance - 1:
            raise ValueError("syndrome length must be distance - 1")
        if any(bit not in (0, 1) for bit in syndrome):
            raise ValueError("syndrome entries must be bits")

        candidates = []
        for first_bit in (0, 1):
            correction = [first_bit]
            for check in syndrome:
                correction.append(correction[-1] ^ check)
            candidates.append(tuple(correction))
        return min(candidates, key=sum)

    def logical_measurement(self, state: BitVector) -> int:
        self._validate_state(state)
        return int(sum(state) > self.distance // 2)

    def run_trial(
        self,
        physical_error_rate: float,
        rng: random.Random,
        logical_bit: int = 0,
    ) -> bool:
        encoded = self.encode(logical_bit)
        noisy = self.apply_bit_flip_noise(encoded, physical_error_rate, rng)
        observed_syndrome = self.syndrome(noisy)
        correction = self.decode(observed_syndrome)
        corrected = tuple(bit ^ fix for bit, fix in zip(noisy, correction))
        return self.logical_measurement(corrected) != logical_bit

    def estimate_logical_error_rate(
        self,
        physical_error_rate: float,
        trials: int,
        seed: int | None = None,
    ) -> SimulationResult:
        self._validate_probability(physical_error_rate)
        if trials <= 0:
            raise ValueError("trials must be positive")

        rng = random.Random(seed)
        failures = sum(
            self.run_trial(physical_error_rate=physical_error_rate, rng=rng)
            for _ in range(trials)
        )
        return SimulationResult(
            distance=self.distance,
            physical_error_rate=physical_error_rate,
            trials=trials,
            logical_failures=failures,
        )

    def _validate_state(self, state: BitVector) -> None:
        if len(state) != self.distance:
            raise ValueError("state length must match code distance")
        if any(bit not in (0, 1) for bit in state):
            raise ValueError("state entries must be bits")

    @staticmethod
    def _validate_bit(bit: int) -> None:
        if bit not in (0, 1):
            raise ValueError("logical bit must be 0 or 1")

    @staticmethod
    def _validate_probability(probability: float) -> None:
        if not 0 <= probability <= 1:
            raise ValueError("probability must be between 0 and 1")
