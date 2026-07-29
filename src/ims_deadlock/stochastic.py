"""Stochastic estimators for explicit absorbing CTMCs."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import sqrt
from random import Random

from ims_deadlock.ctmc import AbsorbingCTMC


@dataclass(frozen=True)
class CompetingAbsorptionEstimate:
    """Monte Carlo estimate for competing absorbing classes."""

    sample_count: int
    deadlock_count: int
    deadlock_estimate: float
    wilson_95_ci: tuple[float, float]
    mean_absorption_time: float
    stream_manifest: dict[str, object]
    generator_provenance: str = "explicit_user_supplied"
    case_derived: bool = False


def estimate_competing_absorption(
    ctmc: AbsorbingCTMC,
    *,
    initial_state: str,
    sample_count: int,
    master_seed: int,
) -> CompetingAbsorptionEstimate:
    """Estimate deadlock absorption with reproducible Gillespie replications."""

    if sample_count <= 0:
        msg = "sample_count must be positive"
        raise ValueError(msg)
    ctmc._validate()
    if initial_state not in set(ctmc.transient_states):
        msg = f"unknown initial_state {initial_state!r}"
        raise ValueError(msg)

    deadlock_count = 0
    total_time = 0.0
    seed_hasher = sha256()
    first_seed: int | None = None
    last_seed: int | None = None
    for replication_index in range(sample_count):
        seed = _replication_seed(master_seed, replication_index)
        if first_seed is None:
            first_seed = seed
        last_seed = seed
        seed_hasher.update(seed.to_bytes(32, "big"))
        absorbed_class, absorption_time = _run_replication(ctmc, initial_state, seed)
        total_time += absorption_time
        if absorbed_class == "deadlock":
            deadlock_count += 1

    estimate = deadlock_count / sample_count
    return CompetingAbsorptionEstimate(
        sample_count=sample_count,
        deadlock_count=deadlock_count,
        deadlock_estimate=estimate,
        wilson_95_ci=_wilson_interval(deadlock_count, sample_count),
        mean_absorption_time=total_time / sample_count,
        stream_manifest={
            "master_seed": master_seed,
            "sample_count": sample_count,
            "seed_derivation": "sha256(master_seed:replication_index)",
            "first_replication_seed": first_seed,
            "last_replication_seed": last_seed,
            "replication_seed_digest": seed_hasher.hexdigest(),
        },
        generator_provenance=ctmc.generator_provenance,
        case_derived=ctmc.case_derived,
    )


def _run_replication(
    ctmc: AbsorbingCTMC,
    initial_state: str,
    seed: int,
) -> tuple[str, float]:
    rng = Random(seed)
    current = initial_state
    elapsed = 0.0
    transient_set = set(ctmc.transient_states)
    while current in transient_set:
        transitions = _outgoing_events(ctmc, current)
        total_rate = sum(rate for _target, _absorbed_class, rate in transitions)
        if total_rate <= 0.0:
            msg = f"state {current!r} has no positive outgoing rate"
            raise ValueError(msg)
        elapsed += rng.expovariate(total_rate)
        threshold = rng.random() * total_rate
        cumulative = 0.0
        for target, absorbed_class, rate in transitions:
            cumulative += rate
            if threshold <= cumulative:
                if absorbed_class is not None:
                    return absorbed_class, elapsed
                current = target
                break
    msg = f"replication reached non-absorbing unknown state {current!r}"
    raise ValueError(msg)


def _outgoing_events(
    ctmc: AbsorbingCTMC,
    state: str,
) -> list[tuple[str, str | None, float]]:
    events: list[tuple[str, str | None, float]] = []
    for (source, target), rate in sorted(ctmc.transient_rates.items()):
        if source == state and rate > 0.0:
            events.append((target, None, rate))
    for (source, target), rate in sorted(ctmc.completion_rates.items()):
        if source == state and rate > 0.0:
            events.append((target, "completion", rate))
    for (source, target), rate in sorted(ctmc.deadlock_rates.items()):
        if source == state and rate > 0.0:
            events.append((target, "deadlock", rate))
    return events


def _replication_seed(master_seed: int, replication_index: int) -> int:
    digest = sha256(f"{master_seed}:{replication_index}".encode("ascii")).digest()
    return int.from_bytes(digest, "big")


def _wilson_interval(successes: int, sample_count: int) -> tuple[float, float]:
    z = 1.959963984540054
    p_hat = successes / sample_count
    denominator = 1.0 + z**2 / sample_count
    center = (p_hat + z**2 / (2.0 * sample_count)) / denominator
    margin = (
        z
        * sqrt(
            (p_hat * (1.0 - p_hat) + z**2 / (4.0 * sample_count)) / sample_count,
        )
        / denominator
    )
    return max(0.0, center - margin), min(1.0, center + margin)
