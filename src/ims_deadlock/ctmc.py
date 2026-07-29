"""Small exact absorbing-CTMC solver for IMS proof obligations."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class QuantitativeResult:
    """Deadlock probability and mean absorption time by transient state."""

    deadlock_probability: dict[str, float]
    mean_absorption_time: dict[str, float]
    generator_provenance: str = "explicit_user_supplied"
    case_derived: bool = False
    committor_residual_inf_norm: float = 0.0
    mean_time_residual_inf_norm: float = 0.0
    probability_bounds: dict[str, float] | None = None
    probability_bounds_valid: bool = True

    def to_json_dict(self) -> dict[str, object]:
        return {
            "deadlock_probability": self.deadlock_probability,
            "mean_absorption_time": self.mean_absorption_time,
            "generator_provenance": self.generator_provenance,
            "case_derived": self.case_derived,
            "committor_residual_inf_norm": self.committor_residual_inf_norm,
            "mean_time_residual_inf_norm": self.mean_time_residual_inf_norm,
            "probability_bounds": self.probability_bounds or {"min": 0.0, "max": 0.0},
            "probability_bounds_valid": self.probability_bounds_valid,
        }


@dataclass(frozen=True)
class SensitivityResult:
    """Derivative of CTMC quantities for an explicit fixed-partition generator."""

    deadlock_probability_derivative: dict[str, float]
    mean_absorption_time_derivative: dict[str, float]
    committor_derivative_residual_inf_norm: float
    mean_time_derivative_residual_inf_norm: float
    generator_provenance: str = "explicit_user_supplied_derivative"
    case_derived: bool = False


@dataclass(frozen=True)
class DoobConditionedGenerator:
    """Deadlock-conditioned generator on positive-h transient states."""

    transient_states: tuple[str, ...]
    completion_rates: dict[tuple[str, str], float]
    deadlock_rates: dict[tuple[str, str], float]
    transient_rates: dict[tuple[str, str], float]
    row_sum_residual_inf_norm: float
    domain: dict[str, object]
    excluded_transient_states: tuple[str, ...]
    generator_provenance: str = "explicit_user_supplied_doob_h_transform"
    case_derived: bool = False


@dataclass(frozen=True)
class AbsorbingCTMC:
    """Finite absorbing CTMC described by transition-rate dictionaries."""

    transient_states: tuple[str, ...]
    completion_rates: dict[tuple[str, str], float]
    deadlock_rates: dict[tuple[str, str], float]
    transient_rates: dict[tuple[str, str], float]
    generator_provenance: str = "explicit_user_supplied"
    case_derived: bool = False

    def solve(self) -> QuantitativeResult:
        self._validate()
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
        probability_bounds = {
            "min": min(probabilities, default=0.0),
            "max": max(probabilities, default=0.0),
        }
        return QuantitativeResult(
            deadlock_probability=dict(zip(states, probabilities, strict=True)),
            mean_absorption_time=dict(zip(states, mean_times, strict=True)),
            generator_provenance=self.generator_provenance,
            case_derived=self.case_derived,
            committor_residual_inf_norm=_residual_inf_norm(
                matrix,
                probabilities,
                dead_rhs,
            ),
            mean_time_residual_inf_norm=_residual_inf_norm(
                matrix,
                mean_times,
                time_rhs,
            ),
            probability_bounds=probability_bounds,
            probability_bounds_valid=(
                probability_bounds["min"] >= -1e-10
                and probability_bounds["max"] <= 1.0 + 1e-10
            ),
        )

    def sensitivity(
        self,
        *,
        derivative_completion_rates: dict[tuple[str, str], float] | None = None,
        derivative_deadlock_rates: dict[tuple[str, str], float] | None = None,
        derivative_transient_rates: dict[tuple[str, str], float] | None = None,
    ) -> SensitivityResult:
        self._validate()
        derivative_completion_rates = derivative_completion_rates or {}
        derivative_deadlock_rates = derivative_deadlock_rates or {}
        derivative_transient_rates = derivative_transient_rates or {}
        self._validate_derivative_rates(
            derivative_completion_rates,
            derivative_deadlock_rates,
            derivative_transient_rates,
        )

        states = self.transient_states
        matrix = _q_tt(
            states,
            self.transient_rates,
            self.completion_rates,
            self.deadlock_rates,
        )
        derivative_matrix = _q_tt_derivative(
            states,
            derivative_transient_rates,
            derivative_completion_rates,
            derivative_deadlock_rates,
        )
        base = self.solve()
        h = [base.deadlock_probability[state] for state in states]
        tau = [base.mean_absorption_time[state] for state in states]
        deadlock_derivative = [
            sum(
                rate
                for (source, _target), rate in derivative_deadlock_rates.items()
                if source == state
            )
            for state in states
        ]

        committor_rhs = [
            -value
            for value in _matrix_vector_plus(derivative_matrix, h, deadlock_derivative)
        ]
        mean_time_rhs = [-value for value in _matrix_vector(derivative_matrix, tau)]
        committor_derivative = _solve_linear(matrix, committor_rhs)
        mean_time_derivative = _solve_linear(matrix, mean_time_rhs)
        return SensitivityResult(
            deadlock_probability_derivative=dict(
                zip(states, committor_derivative, strict=True),
            ),
            mean_absorption_time_derivative=dict(
                zip(states, mean_time_derivative, strict=True),
            ),
            committor_derivative_residual_inf_norm=_residual_inf_norm(
                matrix,
                committor_derivative,
                committor_rhs,
            ),
            mean_time_derivative_residual_inf_norm=_residual_inf_norm(
                matrix,
                mean_time_derivative,
                mean_time_rhs,
            ),
            case_derived=self.case_derived,
        )

    def deadlock_conditioned_generator(self) -> DoobConditionedGenerator:
        self._validate()
        base = self.solve()
        h = base.deadlock_probability
        negative_noise = {
            state: value
            for state, value in h.items()
            if value < 0.0 and abs(value) <= 1e-12
        }
        conditioned_states = tuple(
            state for state in self.transient_states if h[state] > 0.0
        )
        conditioned_set = set(conditioned_states)
        excluded = tuple(
            state for state in self.transient_states if state not in conditioned_set
        )

        transient_rates: dict[tuple[str, str], float] = {}
        for (source, target), rate in self.transient_rates.items():
            if source in conditioned_set and target in conditioned_set and rate > 0.0:
                transient_rates[(source, target)] = rate * h[target] / h[source]

        deadlock_rates = {
            (source, target): rate / h[source]
            for (source, target), rate in self.deadlock_rates.items()
            if source in conditioned_set and rate > 0.0
        }
        completion_rates = {
            (source, target): 0.0
            for (source, target), _rate in self.completion_rates.items()
            if source in conditioned_set
        }
        rows = _row_sums(
            conditioned_states,
            transient_rates,
            completion_rates,
            deadlock_rates,
        )
        return DoobConditionedGenerator(
            transient_states=conditioned_states,
            completion_rates=completion_rates,
            deadlock_rates=deadlock_rates,
            transient_rates=transient_rates,
            row_sum_residual_inf_norm=max((abs(value) for value in rows), default=0.0),
            domain={
                "conditioning_event": "deadlock_absorption",
                "positive_h_transient_states": conditioned_states,
                "negative_h_numerical_noise": negative_noise,
                "deadlock_absorbers": tuple(
                    sorted({target for _source, target in self.deadlock_rates}),
                ),
                "completion_rates": "zero",
            },
            excluded_transient_states=excluded,
            case_derived=self.case_derived,
        )

    def _validate(self) -> None:
        if len(set(self.transient_states)) != len(self.transient_states):
            msg = "duplicate transient state ids are not allowed"
            raise ValueError(msg)

        transient_set = set(self.transient_states)
        for (source, target), rate in self.transient_rates.items():
            _validate_rate(rate)
            if source not in transient_set:
                msg = f"unknown transient source {source!r}"
                raise ValueError(msg)
            if target not in transient_set:
                msg = f"unknown transient target {target!r}"
                raise ValueError(msg)
            if source == target:
                msg = "transient jump rates must not contain self transitions"
                raise ValueError(msg)
        for name, rates in (
            ("completion", self.completion_rates),
            ("deadlock", self.deadlock_rates),
        ):
            for (source, target), rate in rates.items():
                _validate_rate(rate)
                if source not in transient_set:
                    msg = f"unknown {name} source {source!r}"
                    raise ValueError(msg)
                if target in transient_set:
                    msg = f"{name} target {target!r} conflicts with transient state"
                    raise ValueError(msg)

        completion_targets = {target for _source, target in self.completion_rates}
        deadlock_targets = {target for _source, target in self.deadlock_rates}
        overlap = sorted(completion_targets & deadlock_targets)
        if overlap:
            msg = (
                f"absorbing label {overlap[0]!r} appears in both completion "
                "and deadlock"
            )
            raise ValueError(msg)
        self._validate_absorption_reachability()

    def _validate_absorption_reachability(self) -> None:
        absorbing_sources = {
            source
            for source, _target in (*self.completion_rates, *self.deadlock_rates)
            if self._outgoing_absorbing_rate(source) > 0.0
        }
        adjacency = {state: set[str]() for state in self.transient_states}
        outgoing = {state: 0.0 for state in self.transient_states}
        for (source, target), rate in self.transient_rates.items():
            outgoing[source] += rate
            if rate > 0.0:
                adjacency[source].add(target)
        for rates in (self.completion_rates, self.deadlock_rates):
            for (source, _target), rate in rates.items():
                outgoing[source] += rate

        for state, total in outgoing.items():
            if total <= 0.0:
                msg = f"state {state!r} must have a positive total outgoing rate"
                raise ValueError(msg)
            seen: set[str] = set()
            stack = [state]
            reachable = False
            while stack:
                current = stack.pop()
                if current in seen:
                    continue
                seen.add(current)
                if current in absorbing_sources:
                    reachable = True
                    break
                stack.extend(sorted(adjacency[current] - seen))
            if not reachable:
                msg = f"state {state!r} must have reachable absorbing transition"
                raise ValueError(msg)

    def _outgoing_absorbing_rate(self, state: str) -> float:
        return sum(
            rate
            for rates in (self.completion_rates, self.deadlock_rates)
            for (source, _target), rate in rates.items()
            if source == state
        )

    def _validate_derivative_rates(
        self,
        derivative_completion_rates: dict[tuple[str, str], float],
        derivative_deadlock_rates: dict[tuple[str, str], float],
        derivative_transient_rates: dict[tuple[str, str], float],
    ) -> None:
        transient_set = set(self.transient_states)
        completion_targets = {target for _source, target in self.completion_rates}
        deadlock_targets = {target for _source, target in self.deadlock_rates}
        for (source, target), rate in derivative_transient_rates.items():
            _validate_derivative_rate(rate)
            if source not in transient_set:
                msg = f"unknown derivative transient source {source!r}"
                raise ValueError(msg)
            if target not in transient_set:
                msg = f"unknown derivative transient target {target!r}"
                raise ValueError(msg)
            if source == target:
                msg = "derivative transient rates must not contain self transitions"
                raise ValueError(msg)
        for name, rates, allowed_targets in (
            ("completion", derivative_completion_rates, completion_targets),
            ("deadlock", derivative_deadlock_rates, deadlock_targets),
        ):
            for (source, target), rate in rates.items():
                _validate_derivative_rate(rate)
                if source not in transient_set:
                    msg = f"unknown derivative {name} source {source!r}"
                    raise ValueError(msg)
                if target not in allowed_targets:
                    msg = f"unknown derivative {name} target {target!r}"
                    raise ValueError(msg)


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


def _q_tt_derivative(
    states: tuple[str, ...],
    transient_rates: dict[tuple[str, str], float],
    completion_rates: dict[tuple[str, str], float],
    deadlock_rates: dict[tuple[str, str], float],
) -> list[list[float]]:
    index = {state: idx for idx, state in enumerate(states)}
    matrix = [[0.0 for _ in states] for _ in states]
    outgoing = {state: 0.0 for state in states}

    for (source, target), rate in transient_rates.items():
        outgoing[source] += rate
        matrix[index[source]][index[target]] += rate
    for rates in (completion_rates, deadlock_rates):
        for (source, _target), rate in rates.items():
            outgoing[source] += rate
    for state, row in index.items():
        matrix[row][row] -= outgoing[state]
    return matrix


def _validate_rate(rate: float) -> None:
    if not isfinite(rate) or rate < 0:
        msg = f"transition rates must be finite and nonnegative, got {rate}"
        raise ValueError(msg)


def _validate_derivative_rate(rate: float) -> None:
    if not isfinite(rate):
        msg = f"derivative transition rates must be finite, got {rate}"
        raise ValueError(msg)


def _matrix_vector(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [
        sum(coef * value for coef, value in zip(row, vector, strict=True))
        for row in matrix
    ]


def _matrix_vector_plus(
    matrix: list[list[float]],
    vector: list[float],
    addition: list[float],
) -> list[float]:
    return [
        value + addend
        for value, addend in zip(_matrix_vector(matrix, vector), addition, strict=True)
    ]


def _residual_inf_norm(
    matrix: list[list[float]],
    solution: list[float],
    rhs: list[float],
) -> float:
    residuals = [
        lhs - rhs_value
        for lhs, rhs_value in zip(_matrix_vector(matrix, solution), rhs, strict=True)
    ]
    return max((abs(value) for value in residuals), default=0.0)


def _row_sums(
    states: tuple[str, ...],
    transient_rates: dict[tuple[str, str], float],
    completion_rates: dict[tuple[str, str], float],
    deadlock_rates: dict[tuple[str, str], float],
) -> list[float]:
    matrix = _q_tt(states, transient_rates, completion_rates, deadlock_rates)
    return [
        sum(row) + _absorbing_outgoing(state, completion_rates, deadlock_rates)
        for state, row in zip(states, matrix, strict=True)
    ]


def _absorbing_outgoing(
    state: str,
    completion_rates: dict[tuple[str, str], float],
    deadlock_rates: dict[tuple[str, str], float],
) -> float:
    return sum(
        rate
        for rates in (completion_rates, deadlock_rates)
        for (source, _target), rate in rates.items()
        if source == state
    )


def _solve_linear(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    size = len(rhs)
    augmented = [
        row.copy() + [rhs_value] for row, rhs_value in zip(matrix, rhs, strict=True)
    ]

    for pivot_idx in range(size):
        pivot_row = max(
            range(pivot_idx, size), key=lambda row: abs(augmented[row][pivot_idx])
        )
        column_scale = max(
            abs(augmented[row][pivot_idx]) for row in range(pivot_idx, size)
        )
        if column_scale == 0.0 or abs(augmented[pivot_row][pivot_idx]) <= (
            column_scale * 1e-12
        ):
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
