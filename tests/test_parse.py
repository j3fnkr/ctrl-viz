"""
Tests for transfer function parsing.
"""

import pytest
import control

from ctrl_viz.parse import parse_transfer_function


class TestParseTransferFunction:
    """Tests for parse_transfer_function."""

    @staticmethod
    def _coeffs(system):
        return list(system.num[0][0]), list(system.den[0][0])

    def test_simple_first_order(self):
        system = parse_transfer_function("1/(s+1)")
        expected = control.TransferFunction([1], [1, 1])
        assert self._coeffs(system) == self._coeffs(expected)

    def test_second_order_with_caret(self):
        system = parse_transfer_function("1/(s^2+0.5*s+1)")
        expected = control.TransferFunction([1], [1, 0.5, 1])
        assert self._coeffs(system) == self._coeffs(expected)

    def test_factored_rational(self):
        system = parse_transfer_function("(s+1)/(s+2)")
        expected = control.TransferFunction([1, 1], [1, 2])
        assert self._coeffs(system) == self._coeffs(expected)

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            parse_transfer_function("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            parse_transfer_function("   ")

    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError, match="Could not parse"):
            parse_transfer_function("foo")

    def test_non_transfer_function_raises(self):
        with pytest.raises(ValueError, match="must evaluate to a transfer function"):
            parse_transfer_function("1+1")
