from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import combinations, product
from typing import Literal

from qec_lab.gf2 import (
    BitMatrix,
    BitVector,
    as_bit_matrix,
    as_bit_vector,
    dot,
    in_row_space,
    matvec,
    nullspace,
    pauli_weight,
    rank,
    zeros,
)


Pauli = Literal["I", "X", "Y", "Z"]


@dataclass(frozen=True)
class CSSSyndrome:
    """Syndrome of a Pauli error for a CSS stabilizer code.

    `x_checks` are violations of X-type stabilizer checks and are caused by the
    Z component of a Pauli error. `z_checks` are violations of Z-type stabilizer
    checks and are caused by the X component of a Pauli error.
    """

    x_checks: BitVector
    z_checks: BitVector

    @property
    def is_trivial(self) -> bool:
        return not any(self.x_checks) and not any(self.z_checks)


@dataclass(frozen=True)
class SingleQubitError:
    qubit: int
    pauli: Pauli
    x_part: BitVector
    z_part: BitVector
    syndrome: CSSSyndrome


@dataclass(frozen=True)
class CSSCode:
    """Binary Calderbank-Shor-Steane stabilizer code.

    The rows of `hx` specify X-type stabilizer generators and the rows of `hz`
    specify Z-type stabilizer generators. Commutation is the condition
    `hx * hz.T = 0` over F_2.
    """

    hx: BitMatrix
    hz: BitMatrix
    name: str = "CSS code"

    def __post_init__(self) -> None:
        hx = as_bit_matrix(self.hx)
        hz = as_bit_matrix(self.hz)
        object.__setattr__(self, "hx", hx)
        object.__setattr__(self, "hz", hz)

        if not hx and not hz:
            raise ValueError("at least one X or Z check is required")
        widths = {len(row) for row in (*hx, *hz)}
        if len(widths) != 1:
            raise ValueError("all X and Z checks must have the same block length")
        if not self.commutation_matrix_is_zero():
            raise ValueError("CSS checks must commute: hx * hz.T must vanish over F_2")

    @property
    def n(self) -> int:
        if self.hx:
            return len(self.hx[0])
        return len(self.hz[0])

    @property
    def rank_x(self) -> int:
        return rank(self.hx)

    @property
    def rank_z(self) -> int:
        return rank(self.hz)

    @property
    def k(self) -> int:
        return self.n - self.rank_x - self.rank_z

    @property
    def parameters_without_distance(self) -> tuple[int, int]:
        return self.n, self.k

    def parameters(self, compute_distance: bool = False) -> tuple[int, int] | tuple[int, int, int]:
        if compute_distance:
            return self.n, self.k, self.distance()
        return self.parameters_without_distance

    def commutation_matrix_is_zero(self) -> bool:
        return all(dot(x_check, z_check) == 0 for x_check in self.hx for z_check in self.hz)

    def syndrome(self, x_error: Iterable[int], z_error: Iterable[int]) -> CSSSyndrome:
        x_part = as_bit_vector(x_error)
        z_part = as_bit_vector(z_error)
        self._validate_error_parts(x_part, z_part)
        return CSSSyndrome(
            x_checks=matvec(self.hx, z_part),
            z_checks=matvec(self.hz, x_part),
        )

    def stabilizer_generators(self) -> tuple[str, ...]:
        x_generators = tuple(_pauli_string(row, zeros(self.n)) for row in self.hx)
        z_generators = tuple(_pauli_string(zeros(self.n), row) for row in self.hz)
        return x_generators + z_generators

    def is_stabilizer(self, x_error: Iterable[int], z_error: Iterable[int]) -> bool:
        x_part = as_bit_vector(x_error)
        z_part = as_bit_vector(z_error)
        self._validate_error_parts(x_part, z_part)
        return in_row_space(x_part, self.hx) and in_row_space(z_part, self.hz)

    def commutes_with_stabilizers(self, x_error: Iterable[int], z_error: Iterable[int]) -> bool:
        return self.syndrome(x_error, z_error).is_trivial

    def is_nontrivial_logical(self, x_error: Iterable[int], z_error: Iterable[int]) -> bool:
        x_part = as_bit_vector(x_error)
        z_part = as_bit_vector(z_error)
        self._validate_error_parts(x_part, z_part)
        return (
            pauli_weight(x_part, z_part) > 0
            and self.commutes_with_stabilizers(x_part, z_part)
            and not self.is_stabilizer(x_part, z_part)
        )

    def distance(self) -> int:
        """Return the exact quantum distance by exhaustive search.

        This is intended for small pedagogical codes such as the repetition,
        Shor, and Steane codes. It is deliberately exact rather than asymptotic.
        """

        for weight in range(1, self.n + 1):
            for x_part, z_part in _pauli_errors_of_weight(self.n, weight):
                if self.is_nontrivial_logical(x_part, z_part):
                    return weight
        raise ValueError("no nontrivial logical operator found")

    def single_qubit_errors(self) -> tuple[SingleQubitError, ...]:
        errors = []
        for qubit in range(self.n):
            for pauli in ("X", "Y", "Z"):
                x_part, z_part = _single_qubit_pauli(self.n, qubit, pauli)
                errors.append(
                    SingleQubitError(
                        qubit=qubit,
                        pauli=pauli,
                        x_part=x_part,
                        z_part=z_part,
                        syndrome=self.syndrome(x_part, z_part),
                    )
                )
        return tuple(errors)

    def single_qubit_syndrome_table(self) -> dict[CSSSyndrome, tuple[SingleQubitError, ...]]:
        table: dict[CSSSyndrome, list[SingleQubitError]] = {}
        for error in self.single_qubit_errors():
            table.setdefault(error.syndrome, []).append(error)
        return {syndrome: tuple(errors) for syndrome, errors in table.items()}

    def corrects_all_single_qubit_errors_non_degenerately(self) -> bool:
        errors = self.single_qubit_errors()
        return all(not error.syndrome.is_trivial for error in errors) and len(
            {error.syndrome for error in errors}
        ) == len(errors)

    def x_logical_basis(self) -> BitMatrix:
        """Return representatives of X-type logical operators modulo stabilizers."""

        return _quotient_basis(nullspace(self.hz, width=self.n), self.hx, self.n)

    def z_logical_basis(self) -> BitMatrix:
        """Return representatives of Z-type logical operators modulo stabilizers."""

        return _quotient_basis(nullspace(self.hx, width=self.n), self.hz, self.n)

    def _validate_error_parts(self, x_part: BitVector, z_part: BitVector) -> None:
        if len(x_part) != self.n or len(z_part) != self.n:
            raise ValueError("Pauli error parts must have length n")


def bit_flip_repetition_css_code(distance: int) -> CSSCode:
    """Return the repetition code as a CSS code with Z-type parity checks."""

    if distance < 3:
        raise ValueError("distance must be at least 3")
    if distance % 2 == 0:
        raise ValueError("distance must be odd")
    hz = tuple(
        tuple(int(column == row or column == row + 1) for column in range(distance))
        for row in range(distance - 1)
    )
    return CSSCode(hx=(), hz=hz, name=f"{distance}-qubit bit-flip repetition CSS code")


def steane_code() -> CSSCode:
    """Return the [[7,1,3]] Steane CSS code from the Hamming [7,4,3] code."""

    hamming_check = (
        (1, 0, 0, 1, 0, 1, 1),
        (0, 1, 0, 1, 1, 0, 1),
        (0, 0, 1, 0, 1, 1, 1),
    )
    return CSSCode(hx=hamming_check, hz=hamming_check, name="Steane [[7,1,3]] code")


def shor_code() -> CSSCode:
    """Return the [[9,1,3]] Shor CSS code."""

    hx = (
        (1, 1, 1, 1, 1, 1, 0, 0, 0),
        (0, 0, 0, 1, 1, 1, 1, 1, 1),
    )
    hz = (
        (1, 1, 0, 0, 0, 0, 0, 0, 0),
        (0, 1, 1, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 1, 1, 0, 0, 0, 0),
        (0, 0, 0, 0, 1, 1, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 1, 1, 0),
        (0, 0, 0, 0, 0, 0, 0, 1, 1),
    )
    return CSSCode(hx=hx, hz=hz, name="Shor [[9,1,3]] code")


def _quotient_basis(candidate_basis: BitMatrix, subspace_basis: BitMatrix, width: int) -> BitMatrix:
    representatives = []
    current = as_bit_matrix(subspace_basis)
    for vector in candidate_basis:
        if not in_row_space(vector, current):
            representatives.append(vector)
            current = (*current, vector)
    expected_dimension = width - rank(subspace_basis) - rank(tuple(row for row in candidate_basis if False))
    _ = expected_dimension
    return tuple(representatives)


def _pauli_string(x_part: BitVector, z_part: BitVector) -> str:
    symbols = []
    for x_bit, z_bit in zip(x_part, z_part):
        if x_bit and z_bit:
            symbols.append("Y")
        elif x_bit:
            symbols.append("X")
        elif z_bit:
            symbols.append("Z")
        else:
            symbols.append("I")
    return "".join(symbols)


def _single_qubit_pauli(n: int, qubit: int, pauli: Pauli) -> tuple[BitVector, BitVector]:
    if not 0 <= qubit < n:
        raise ValueError("qubit index out of range")
    x_part = [0 for _ in range(n)]
    z_part = [0 for _ in range(n)]
    if pauli in ("X", "Y"):
        x_part[qubit] = 1
    if pauli in ("Y", "Z"):
        z_part[qubit] = 1
    return tuple(x_part), tuple(z_part)


def _pauli_errors_of_weight(n: int, weight: int) -> Iterable[tuple[BitVector, BitVector]]:
    for support in combinations(range(n), weight):
        for paulis in product(("X", "Y", "Z"), repeat=weight):
            x_part = [0 for _ in range(n)]
            z_part = [0 for _ in range(n)]
            for qubit, pauli in zip(support, paulis):
                if pauli in ("X", "Y"):
                    x_part[qubit] = 1
                if pauli in ("Y", "Z"):
                    z_part[qubit] = 1
            yield tuple(x_part), tuple(z_part)
