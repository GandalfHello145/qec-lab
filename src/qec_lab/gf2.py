from __future__ import annotations

from collections.abc import Iterable, Sequence
from itertools import product


BitVector = tuple[int, ...]
BitMatrix = tuple[BitVector, ...]


def as_bit_vector(vector: Iterable[int]) -> BitVector:
    bits = tuple(int(entry) for entry in vector)
    _validate_bits(bits, context="vector")
    return bits


def as_bit_matrix(matrix: Iterable[Iterable[int]]) -> BitMatrix:
    rows = tuple(as_bit_vector(row) for row in matrix)
    if not rows:
        return rows
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("all matrix rows must have the same length")
    return rows


def zeros(length: int) -> BitVector:
    if length < 0:
        raise ValueError("length must be nonnegative")
    return tuple(0 for _ in range(length))


def identity(size: int) -> BitMatrix:
    if size < 0:
        raise ValueError("size must be nonnegative")
    return tuple(
        tuple(int(row == column) for column in range(size))
        for row in range(size)
    )


def add(left: Sequence[int], right: Sequence[int]) -> BitVector:
    left_bits = as_bit_vector(left)
    right_bits = as_bit_vector(right)
    _validate_same_length(left_bits, right_bits)
    return tuple(a ^ b for a, b in zip(left_bits, right_bits))


def dot(left: Sequence[int], right: Sequence[int]) -> int:
    left_bits = as_bit_vector(left)
    right_bits = as_bit_vector(right)
    _validate_same_length(left_bits, right_bits)
    return sum(a & b for a, b in zip(left_bits, right_bits)) % 2


def hamming_weight(vector: Sequence[int]) -> int:
    return sum(as_bit_vector(vector))


def pauli_weight(x_part: Sequence[int], z_part: Sequence[int]) -> int:
    x_bits = as_bit_vector(x_part)
    z_bits = as_bit_vector(z_part)
    _validate_same_length(x_bits, z_bits)
    return sum(int(x or z) for x, z in zip(x_bits, z_bits))


def transpose(matrix: Iterable[Iterable[int]]) -> BitMatrix:
    rows = as_bit_matrix(matrix)
    if not rows:
        return ()
    return tuple(tuple(row[column] for row in rows) for column in range(len(rows[0])))


def matvec(matrix: Iterable[Iterable[int]], vector: Sequence[int]) -> BitVector:
    rows = as_bit_matrix(matrix)
    bits = as_bit_vector(vector)
    if any(len(row) != len(bits) for row in rows):
        raise ValueError("matrix width must equal vector length")
    return tuple(dot(row, bits) for row in rows)


def matmul(left: Iterable[Iterable[int]], right: Iterable[Iterable[int]]) -> BitMatrix:
    left_rows = as_bit_matrix(left)
    right_rows = as_bit_matrix(right)
    if not left_rows or not right_rows:
        return ()
    if len(left_rows[0]) != len(right_rows):
        raise ValueError("left matrix width must equal right matrix height")
    right_columns = transpose(right_rows)
    return tuple(tuple(dot(row, column) for column in right_columns) for row in left_rows)


def rref(matrix: Iterable[Iterable[int]]) -> tuple[BitMatrix, tuple[int, ...]]:
    rows = [list(row) for row in as_bit_matrix(matrix)]
    if not rows:
        return (), ()

    row_count = len(rows)
    column_count = len(rows[0])
    pivot_columns: list[int] = []
    pivot_row = 0

    for column in range(column_count):
        pivot = None
        for candidate in range(pivot_row, row_count):
            if rows[candidate][column]:
                pivot = candidate
                break
        if pivot is None:
            continue

        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        for row in range(row_count):
            if row != pivot_row and rows[row][column]:
                rows[row] = [left ^ right for left, right in zip(rows[row], rows[pivot_row])]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break

    nonzero_rows = [tuple(row) for row in rows if any(row)]
    return tuple(nonzero_rows), tuple(pivot_columns)


def rank(matrix: Iterable[Iterable[int]]) -> int:
    _, pivot_columns = rref(matrix)
    return len(pivot_columns)


def nullspace(matrix: Iterable[Iterable[int]], width: int | None = None) -> BitMatrix:
    rows = as_bit_matrix(matrix)
    if width is None:
        if not rows:
            raise ValueError("width is required for the nullspace of an empty matrix")
        width = len(rows[0])
    if width < 0:
        raise ValueError("width must be nonnegative")
    if rows and len(rows[0]) != width:
        raise ValueError("width must match the matrix width")

    reduced, pivot_columns = rref(rows)
    pivot_set = set(pivot_columns)
    free_columns = [column for column in range(width) if column not in pivot_set]
    basis = []

    for free_column in free_columns:
        vector = [0 for _ in range(width)]
        vector[free_column] = 1
        for row, pivot_column in zip(reduced, pivot_columns):
            vector[pivot_column] = sum(row[column] & vector[column] for column in free_columns) % 2
        basis.append(tuple(vector))
    return tuple(basis)


def span(basis: Iterable[Iterable[int]], width: int | None = None) -> tuple[BitVector, ...]:
    basis_rows = as_bit_matrix(basis)
    if width is None:
        if not basis_rows:
            return ((),)
        width = len(basis_rows[0])
    if basis_rows and len(basis_rows[0]) != width:
        raise ValueError("basis width must match the requested width")

    vectors = []
    for coefficients in product((0, 1), repeat=len(basis_rows)):
        vector = [0 for _ in range(width)]
        for coefficient, basis_vector in zip(coefficients, basis_rows):
            if coefficient:
                vector = [left ^ right for left, right in zip(vector, basis_vector)]
        vectors.append(tuple(vector))
    return tuple(sorted(set(vectors)))


def in_row_space(vector: Sequence[int], matrix: Iterable[Iterable[int]]) -> bool:
    bits = as_bit_vector(vector)
    rows = as_bit_matrix(matrix)
    if rows and len(rows[0]) != len(bits):
        raise ValueError("matrix width must match vector length")
    if not rows:
        return not any(bits)
    return rank(rows) == rank((*rows, bits))


def _validate_bits(bits: BitVector, context: str) -> None:
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError(f"{context} entries must be bits")


def _validate_same_length(left: Sequence[int], right: Sequence[int]) -> None:
    if len(left) != len(right):
        raise ValueError("vectors must have the same length")
