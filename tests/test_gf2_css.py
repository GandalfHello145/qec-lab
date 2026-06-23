import unittest

from qec_lab import bit_flip_repetition_css_code, shor_code, steane_code
from qec_lab.css import CSSCode
from qec_lab.gf2 import (
    dot,
    in_row_space,
    matvec,
    nullspace,
    pauli_weight,
    rank,
    rref,
    span,
)


class GF2LinearAlgebraTest(unittest.TestCase):
    def test_rank_and_rref_over_gf2(self) -> None:
        matrix = (
            (1, 1, 0, 1),
            (0, 1, 1, 1),
            (1, 0, 1, 0),
        )
        reduced, pivots = rref(matrix)
        self.assertEqual(rank(matrix), 2)
        self.assertEqual(pivots, (0, 1))
        self.assertEqual(reduced, ((1, 0, 1, 0), (0, 1, 1, 1)))

    def test_nullspace_basis_solves_linear_equations(self) -> None:
        check_matrix = (
            (1, 0, 0, 1, 0, 1, 1),
            (0, 1, 0, 1, 1, 0, 1),
            (0, 0, 1, 0, 1, 1, 1),
        )
        basis = nullspace(check_matrix)
        self.assertEqual(len(basis), 4)
        for vector in basis:
            self.assertEqual(matvec(check_matrix, vector), (0, 0, 0))
        self.assertEqual(len(span(basis)), 16)

    def test_row_space_membership(self) -> None:
        basis = ((1, 1, 0), (0, 1, 1))
        self.assertTrue(in_row_space((1, 0, 1), basis))
        self.assertFalse(in_row_space((1, 0, 0), basis))

    def test_dot_and_pauli_weight(self) -> None:
        self.assertEqual(dot((1, 0, 1, 1), (0, 1, 1, 1)), 0)
        self.assertEqual(pauli_weight((1, 0, 1), (0, 1, 1)), 3)


class CSSCodeTest(unittest.TestCase):
    def test_noncommuting_css_checks_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "commute"):
            CSSCode(hx=((1, 0, 0),), hz=((1, 1, 0),))

    def test_bit_flip_repetition_css_parameters(self) -> None:
        code = bit_flip_repetition_css_code(5)
        self.assertEqual(code.parameters(compute_distance=True), (5, 1, 1))
        self.assertEqual(code.rank_x, 0)
        self.assertEqual(code.rank_z, 4)

    def test_steane_code_parameters_distance_and_generators(self) -> None:
        code = steane_code()
        self.assertEqual(code.parameters(compute_distance=True), (7, 1, 3))
        self.assertTrue(code.commutation_matrix_is_zero())
        self.assertEqual(len(code.stabilizer_generators()), 6)
        self.assertIn("XIIXIXX", code.stabilizer_generators())
        self.assertIn("ZIIZIZZ", code.stabilizer_generators())

    def test_steane_single_qubit_errors_have_unique_syndromes(self) -> None:
        code = steane_code()
        errors = code.single_qubit_errors()
        self.assertEqual(len(errors), 21)
        self.assertTrue(code.corrects_all_single_qubit_errors_non_degenerately())
        self.assertEqual(len({error.syndrome for error in errors}), 21)
        self.assertTrue(all(not error.syndrome.is_trivial for error in errors))

    def test_steane_logical_basis_has_one_x_and_one_z_generator(self) -> None:
        code = steane_code()
        x_logicals = code.x_logical_basis()
        z_logicals = code.z_logical_basis()
        self.assertEqual(len(x_logicals), 1)
        self.assertEqual(len(z_logicals), 1)
        self.assertTrue(code.is_nontrivial_logical(x_logicals[0], (0,) * code.n))
        self.assertTrue(code.is_nontrivial_logical((0,) * code.n, z_logicals[0]))

    def test_shor_code_parameters_and_distance(self) -> None:
        code = shor_code()
        self.assertEqual(code.parameters(compute_distance=True), (9, 1, 3))
        self.assertTrue(code.commutation_matrix_is_zero())
        self.assertEqual(code.rank_x, 2)
        self.assertEqual(code.rank_z, 6)

    def test_shor_code_is_degenerate_for_single_qubit_phase_errors(self) -> None:
        code = shor_code()
        table = code.single_qubit_syndrome_table()
        self.assertLess(len(table), len(code.single_qubit_errors()))
        self.assertTrue(all(not error.syndrome.is_trivial for error in code.single_qubit_errors()))


if __name__ == "__main__":
    unittest.main()
