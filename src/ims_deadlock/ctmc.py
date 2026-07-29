"""Small exact absorbing-CTMC solver for IMS proof obligations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QuantitativeResult:
    """Deadlock probability and mean absorption time by transient state."""

    deadlock_probability: dict[str, float]
    mean_absorption_time: dict[str, float]

    def to_json_dict(self) -> dict[str, object]:
        return {
            "deadlock_probability": self.deadlock_probability,
            "mean_absorption_time": self.mean_absorption_time,
        }


@dataclass(frozen=True)
class AbsorbingCTMC:
    """Finite absorbing CTMC described by transition-rate dictionaries."""

    transient_states: tuple[str, ...]
    completion_rates: dict[tuple[str, str], float]
    deadlock_rates: dict[tuple[str, str], float]
    transient_rates: dict[tuple[str, str], float]

    def solve(self) -> QuantitativeResult:
        states = self.transient_states
        matrix = _q_tt(
            states,
            self.transient_rates,
            self.completion_rates,
            self.deadlock_rates,
        )
        dead_rhs = [
            -sum(
                rate
                for (source, _target), rate in self.deadlock_rates.items()
                if source == state
            )
            for state in states
        ]
        time_rhs = [-1.0 for _ in states]

        probabilities = _solve_linear(matrix, dead_rhs)
        mean_times = _solve_linear(matrix, time_rhs)
        return QuantitativeResult(
            deadlock_probability=dict(zip(states, probabilities, strict=True)),
            mean_absorption_time=dict(zip(states, mean_times, strict=True)),
        )


def _q_tt(
    states: tuple[str, ...],
    transient_rates: dict[tuple[str, str], float],
    completion_rates: dict[tuple[str, str], float],
    deadlock_rates: dict[tuple[str, str], float],
) -> list[list[float]]:
    index = {state: idx for idx, state in enumerate(states)}
    matrix = [[0.0 for _ in states] for _ in states]
    outgoing = {state: 0.0 for state in states}

    for (source, target), rate in transient_rates.items():
        _validate_rate(rate)
        outgoing[source] += rate
        matrix[index[source]][index[target]] += rate
    for rates in (completion_rates, deadlock_rates):
        for (source, _target), rate in rates.items():
            _validate_rate(rate)
            outgoing[source] += rate
    for state, row in index.items():
        matrix[row][row] -= outgoing[state]
    return matrix


def _validate_rate(rate: float) -> None:
    if rate < 0:
        msg = f"transition rates must be nonnegative, got {rate}"
        raise ValueError(msg)


def _solve_linear(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    size = len(rhs)
    augmented = [
        row.copy() + [rhs_value] for row, rhs_value in zip(matrix, rhs, strict=True)
    ]

    for pivot_idx in range(size):
        pivot_row = max(
            range(pivot_idx, size), key=lambda row: abs(augmented[row][pivot_idx])
        )
        if abs(augmented[pivot_row][pivot_idx]) < 1e-12:
            msg = "singular CTMC transient generator"
            raise ValueError(msg)
        augmented[pivot_idx], augmented[pivot_row] = (
            augmented[pivot_row],
            augmented[pivot_idx],
        )
        pivot = augmented[pivot_idx][pivot_idx]
        for col in range(pivot_idx, size + 1):
            augmented[pivot_idx][col] /= pivot
        for row in range(size):
            if row == pivot_idx:
                continue
            factor = augmented[row][pivot_idx]
            if factor == 0:
                continue
            for col in range(pivot_idx, size + 1):
                augmented[row][col] -= factor * augmented[pivot_idx][col]
    return [augmented[row][size] for row in range(size)]
