"""Authorized T6 waves for the T-ASE hardening panel."""

from __future__ import annotations

import hashlib
import json
import math
import os
import time
from pathlib import Path
from random import Random
from typing import Any

from ims_deadlock.analysis import enumerate_stable_lts
from ims_deadlock.ctmc import AbsorbingCTMC
from ims_deadlock.engine import EventKind
from ims_deadlock.tase_hardening import (
    H1_IDS,
    H2_CELLS,
    H2_TYPES,
    H3_STATE_CAP,
    SCOPE_ID,
    ComputeProbe,
    WorkerProtocolError,
    build_h2_plant,
    build_h3_plant,
    build_h3_rows,
    build_h4_islands,
    build_h4_v3_islands,
    build_shard_plan,
    classify_h3_row,
    evaluate_h1,
    evaluate_h2_plant,
    pin_blas_thread_env,
    plan_workers,
    run_process_pool,
    validate_wave,
)
from ims_deadlock.terminal_classes import (
    TerminalPartitionError,
    partition_stable_lts,
)

AUTH_RELATIVE = "cases/discovery/tase_hardening_v1/quantitative_authorization.json"
APPROVED_QUANT_AUTH_SHA256 = (
    "090c75516fbbde24dcc4cde03b0d24aa633955f1ce9b97cc4c49b229f7b193c9"
)
PRIMARY_SEED = 2026081901
REPRO_SEED = 2026081902
H4_REPLICATIONS = 65536
HOEFFDING_K = 6
HOEFFDING_ALPHA = 0.01


def live_probe() -> ComputeProbe:
    """Record logical CPUs and free RAM without extra packages."""

    logical = os.cpu_count() or 4
    free_gib = 32.0
    try:
        import ctypes

        class _MemoryStatusEx(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = _MemoryStatusEx()
        status.dwLength = ctypes.sizeof(_MemoryStatusEx)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            free_gib = float(status.ullAvailPhys) / (1024.0**3)
    except Exception:
        pass
    return ComputeProbe(logical_cpus=int(logical), free_ram_gib=free_gib)


def hoeffding_tolerance(n: int = H4_REPLICATIONS) -> float:
    """Simultaneous Hoeffding bound for six probability cells at alpha=0.01."""

    return math.sqrt(math.log(2.0 * HOEFFDING_K / HOEFFDING_ALPHA) / (2.0 * n))


def require_quantitative_authorization(repo_root: Path) -> dict[str, Any]:
    """Accept only the T6 authorization bytes approved in this session."""

    path = repo_root / AUTH_RELATIVE
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != APPROVED_QUANT_AUTH_SHA256:
        raise WorkerProtocolError(f"quantitative authorization hash mismatch {digest}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("quantitative_execution_authorized") is not True:
        raise WorkerProtocolError("quantitative flag is not true")
    if payload.get("scope_id") != SCOPE_ID:
        raise WorkerProtocolError("authorization scope mismatch")
    return payload


def eval_h1_id(case_id: str) -> dict[str, Any]:
    """Picklable H1 worker."""

    result = evaluate_h1(case_id)
    result["id"] = case_id
    return result


def eval_h2_key(key: tuple[str, str]) -> dict[str, Any]:
    """Picklable H2 worker."""

    plant = build_h2_plant(key[0], key[1])
    report = evaluate_h2_plant(plant)
    report["id"] = f"{key[0]}__{key[1]}"
    return report


def eval_h3_row(row: dict[str, Any]) -> dict[str, Any]:
    """Picklable H3 worker: enumerate or refuse."""

    started = time.perf_counter()
    model, state, transitions = build_h3_plant(row)
    lts = enumerate_stable_lts(model, state, transitions, max_states=H3_STATE_CAP)
    elapsed = time.perf_counter() - started
    payload = {
        **row,
        "id": (
            f"h3-{row['n_jobs']}-{row['n_resources']}-{row['capacity']}-"
            f"{row['n_alternatives']}-{row['kernel_count']}-"
            f"{int(row['bypass'])}-{int(row['transport'])}"
        ),
        "state_count": len(lts.states),
        "elapsed_s": elapsed,
        "truncated": lts.truncated,
    }
    payload["classification"] = classify_h3_row(payload)
    return payload


def eval_h4_v3_barrier(role: str) -> dict[str, Any]:
    """Barrier A for the P1 deadlock island."""

    return _eval_h4_barrier(role, version="v3")


def eval_h4_barrier(role: str) -> dict[str, Any]:
    """Enumerate one H4 v2 island and attempt a terminal/stopping partition."""

    return _eval_h4_barrier(role, version="v2")


def _eval_h4_barrier(role: str, *, version: str) -> dict[str, Any]:
    islands = build_h4_v3_islands() if version == "v3" else build_h4_islands()
    island = next(item for item in islands if item.role == role)
    prefix = "H4_v3" if version == "v3" else "H4_v2"
    lts = enumerate_stable_lts(
        island.model,
        island.initial_state,
        island.transitions,
        max_states=H3_STATE_CAP,
    )
    payload: dict[str, Any] = {
        "id": f"{prefix}_{role}",
        "role": role,
        "label": island.label,
        "intervention": island.intervention,
        "state_count": len(lts.states),
        "truncated": lts.truncated,
        "barrier_a": "refused",
        "refusal_code": None,
        "states": [],
        "transitions": [],
        "d_global": [],
        "d_local": [],
        "completion": [],
        "initial_state": None,
    }
    if lts.truncated or not lts.states:
        payload["refusal_code"] = "truncated_or_empty_lts"
        return payload
    try:
        partition = partition_stable_lts(
            island.model,
            lts,
            island.transitions,
            verify_generated_lts=True,
        )
        unselected = (
            list(partition.r_livelock_state_ids)
            + list(partition.r_terminal_state_ids)
            + list(partition.unreachable_nonabsorbing_state_ids)
        )
        if unselected:
            payload["refusal_code"] = "unselected_closed_or_unreachable"
            payload["refusal_details"] = {"state_ids": unselected}
            return payload
    except TerminalPartitionError as error:
        payload["refusal_code"] = error.code
        payload["refusal_details"] = error.details
        return payload
    rates = _event_rates(island.transitions)
    payload.update(
        {
            "barrier_a": "certified",
            "initial_state": lts.initial_state_id,
            "states": [record.state_id for record in lts.states],
            "d_global": list(partition.d_global_state_ids),
            "d_local": list(partition.d_local_state_ids),
            "completion": list(partition.f_state_ids),
            "transitions": [
                {
                    "source": arc.source,
                    "event": arc.event,
                    "target": arc.target,
                    "rate": rates[arc.event],
                }
                for arc in lts.transitions
            ],
        }
    )
    return payload


def _event_rates(transitions: Any) -> dict[str, float]:
    rates: dict[str, float] = {}
    for transition in transitions:
        rates[transition.name] = (
            2.0 if transition.kind == EventKind.SERVICE_COMPLETE else 1.0
        )
    return rates


def solve_h4_exact(barrier: dict[str, Any]) -> dict[str, Any]:
    """Exact first-hit probabilities on a certified H4 stopped graph."""

    if barrier["barrier_a"] != "certified":
        return {
            "id": barrier["id"],
            "status": "refused",
            "reason": barrier.get("refusal_code"),
        }
    classes = _class_maps(barrier)
    initial = str(barrier["initial_state"])
    if initial in classes["A_stop"]:
        label = classes["label"][initial]
        probs = {
            "theta_g": 1.0 if label == "D_global" else 0.0,
            "theta_l": 1.0 if label == "D_local" else 0.0,
            "theta_b": 1.0 if label in {"D_global", "D_local"} else 0.0,
        }
        return {
            "id": barrier["id"],
            "status": "exact",
            "probabilities": probs,
            "mean_stopped_time": 0.0,
        }
    desired_g = set(barrier["d_global"])
    desired_l = set(barrier["d_local"])
    desired_b = desired_g | desired_l
    theta_g, time_g = _solve_binary(barrier, desired_g, initial)
    theta_l, time_l = _solve_binary(barrier, desired_l, initial)
    theta_b, time_b = _solve_binary(barrier, desired_b, initial)
    del time_g, time_l
    return {
        "id": barrier["id"],
        "status": "exact",
        "probabilities": {
            "theta_g": theta_g,
            "theta_l": theta_l,
            "theta_b": theta_b,
        },
        "mean_stopped_time": time_b,
    }


def _class_maps(barrier: dict[str, Any]) -> dict[str, Any]:
    label: dict[str, str] = {}
    for state in barrier["d_global"]:
        label[state] = "D_global"
    for state in barrier["d_local"]:
        label[state] = "D_local"
    for state in barrier["completion"]:
        label[state] = "F"
    return {"label": label, "A_stop": set(label)}


def _solve_binary(
    barrier: dict[str, Any], desired: set[str], initial: str
) -> tuple[float, float]:
    all_stop = (
        set(barrier["d_global"]) | set(barrier["d_local"]) | set(barrier["completion"])
    )
    transient = tuple(state for state in barrier["states"] if state not in all_stop)
    if initial not in transient:
        return 0.0, 0.0
    transient_rates: dict[tuple[str, str], float] = {}
    deadlock_rates: dict[tuple[str, str], float] = {}
    completion_rates: dict[tuple[str, str], float] = {}
    for arc in barrier["transitions"]:
        source = str(arc["source"])
        target = str(arc["target"])
        rate = float(arc["rate"])
        if source in all_stop:
            continue
        key = (source, target)
        if target in desired:
            deadlock_rates[key] = deadlock_rates.get(key, 0.0) + rate
        elif target in all_stop:
            completion_rates[key] = completion_rates.get(key, 0.0) + rate
        else:
            transient_rates[key] = transient_rates.get(key, 0.0) + rate
    result = AbsorbingCTMC(
        transient_states=transient,
        completion_rates=completion_rates,
        deadlock_rates=deadlock_rates,
        transient_rates=transient_rates,
        generator_provenance="tase_hardening_h4_stopped_ctmc_v1",
        case_derived=True,
    ).solve()
    return (
        float(result.deadlock_probability[initial]),
        float(result.mean_absorption_time[initial]),
    )


def eval_h4_des_shard(payload: dict[str, Any]) -> dict[str, Any]:
    """Picklable DES shard: contiguous replications of one certified plant."""

    barrier = payload["barrier"]
    start = int(payload["start"])
    count = int(payload["count"])
    master_seed = int(payload["master_seed"])
    wave = str(payload["wave"])
    counts = {"D_global": 0, "D_local": 0, "F": 0}
    total_time = 0.0
    by_source: dict[str, list[dict[str, Any]]] = {}
    for arc in barrier["transitions"]:
        by_source.setdefault(str(arc["source"]), []).append(arc)
    labels = _class_maps(barrier)["label"]
    initial = str(barrier["initial_state"])
    for index in range(start, start + count):
        seed = int.from_bytes(
            hashlib.sha256(f"{master_seed}:{index}".encode("ascii")).digest(),
            "big",
        )
        absorbed, elapsed = _gillespie(initial, by_source, labels, seed)
        counts[absorbed] += 1
        total_time += elapsed
    return {
        "id": f"{barrier['id']}__{wave}__{start}",
        "plant_id": barrier["id"],
        "wave": wave,
        "start": start,
        "count": count,
        "counts": counts,
        "total_time": total_time,
    }


def _gillespie(
    initial: str,
    by_source: dict[str, list[dict[str, Any]]],
    labels: dict[str, str],
    seed: int,
) -> tuple[str, float]:
    rng = Random(seed)
    current = initial
    elapsed = 0.0
    for _step in range(1_000_000):
        if current in labels:
            return labels[current], elapsed
        arcs = by_source.get(current, [])
        total = sum(float(arc["rate"]) for arc in arcs)
        if total <= 0.0:
            raise WorkerProtocolError(f"no positive rate at {current}")
        elapsed += rng.expovariate(total)
        threshold = rng.random() * total
        cumulative = 0.0
        selected = arcs[-1]
        for arc in arcs:
            cumulative += float(arc["rate"])
            if threshold < cumulative:
                selected = arc
                break
        current = str(selected["target"])
    raise WorkerProtocolError("DES step limit exceeded")


def _merge_des(
    shards: list[dict[str, Any]], *, plant_id: str, wave: str, n: int
) -> dict[str, Any]:
    counts = {"D_global": 0, "D_local": 0, "F": 0}
    total_time = 0.0
    total = 0
    for shard in shards:
        if shard["plant_id"] != plant_id or shard["wave"] != wave:
            continue
        for key in counts:
            counts[key] += int(shard["counts"][key])
        total_time += float(shard["total_time"])
        total += int(shard["count"])
    if total != n:
        raise WorkerProtocolError(f"{plant_id} {wave} merged {total} != {n}")
    return {
        "id": f"{plant_id}__{wave}",
        "plant_id": plant_id,
        "wave": wave,
        "sample_count": n,
        "counts": counts,
        "probabilities": {
            "theta_g": counts["D_global"] / n,
            "theta_l": counts["D_local"] / n,
            "theta_b": (counts["D_global"] + counts["D_local"]) / n,
        },
        "mean_stopped_time": total_time / n,
    }


def run_h4_v3_waves(repo_root: Path) -> dict[str, Any]:
    """P1 quantitative wave for the deadlock island. v1/v2 stay immutable."""

    return _run_h4_named_waves(
        repo_root,
        version="v3",
        evidence_name="v3",
        report_name="tase_hardening_h4_v3_report.json",
        barrier_fn=eval_h4_v3_barrier,
    )


def run_h4_v2_waves(repo_root: Path) -> dict[str, Any]:
    """Re-run only repaired H4 into a new evidence root. v1 stays immutable."""

    return _run_h4_named_waves(
        repo_root,
        version="v2",
        evidence_name="v2",
        report_name="tase_hardening_h4_v2_report.json",
        barrier_fn=eval_h4_barrier,
    )


def _run_h4_named_waves(
    repo_root: Path,
    *,
    version: str,
    evidence_name: str,
    report_name: str,
    barrier_fn: Any,
) -> dict[str, Any]:
    auth = require_quantitative_authorization(repo_root)
    probe = live_probe()
    workers = plan_workers(probe, family="H4")
    validate_wave(
        wave="P0",
        workers=workers,
        probe=probe,
        primary_repro_overlap=False,
        reducer_count=1,
    )
    pin_blas_thread_env(workers=workers)
    evidence = repo_root / "evidence" / "tase_hardening" / evidence_name
    evidence.mkdir(parents=True, exist_ok=True)
    report_path = evidence / report_name
    if report_path.exists():
        raise WorkerProtocolError(f"{report_name} already exists; will not overwrite")

    barriers = run_process_pool(("base", "intervention"), barrier_fn, workers=2)
    exact = [solve_h4_exact(barrier) for barrier in barriers]
    certified = [barrier for barrier in barriers if barrier["barrier_a"] == "certified"]
    des_primary: list[dict[str, Any]] = []
    des_repro: list[dict[str, Any]] = []
    if certified:
        des_primary = _run_des_wave(
            certified, wave="primary", master_seed=PRIMARY_SEED, workers=workers
        )
        validate_wave(
            wave="R0",
            workers=workers,
            probe=probe,
            primary_repro_overlap=False,
            reducer_count=1,
        )
        des_repro = _run_des_wave(
            certified, wave="repro", master_seed=REPRO_SEED, workers=workers
        )
    merged_primary = [
        _merge_des(des_primary, plant_id=item["id"], wave="primary", n=H4_REPLICATIONS)
        for item in certified
    ]
    merged_repro = [
        _merge_des(des_repro, plant_id=item["id"], wave="repro", n=H4_REPLICATIONS)
        for item in certified
    ]
    tolerance = hoeffding_tolerance()
    cells = []
    for exact_row in exact:
        if exact_row["status"] != "exact":
            continue
        primary = next(
            item for item in merged_primary if item["plant_id"] == exact_row["id"]
        )
        for name in ("theta_g", "theta_l", "theta_b"):
            error = abs(
                float(exact_row["probabilities"][name]) - primary["probabilities"][name]
            )
            cells.append(
                {
                    "plant_id": exact_row["id"],
                    "estimand": name,
                    "exact": exact_row["probabilities"][name],
                    "des": primary["probabilities"][name],
                    "abs_error": error,
                    "tolerance": tolerance,
                    "compatible": error <= tolerance,
                }
            )
    report = {
        "scope_id": SCOPE_ID,
        "panel": f"h4_{version}",
        "authorization_id": auth["authorization_id"],
        "authorization_sha256": APPROVED_QUANT_AUTH_SHA256,
        "prior_h4_roots_untouched": True,
        "probe": {
            "logical_cpus": probe.logical_cpus,
            "free_ram_gib": probe.free_ram_gib,
            "workers": workers,
        },
        "h4_barrier": [
            {key: barrier[key] for key in barrier if key != "transitions"}
            for barrier in barriers
        ],
        "h4_exact": exact,
        "h4_des_primary": merged_primary,
        "h4_des_repro": merged_repro,
        "compatibility": cells,
        "hoeffding_tolerance": tolerance,
        "original_g6b_gate": "OPEN_PENDING",
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def run_authorized_waves(repo_root: Path) -> dict[str, Any]:
    """Execute P1–P4 and the repro DES wave, then reduce."""

    auth = require_quantitative_authorization(repo_root)
    probe = live_probe()
    workers = plan_workers(probe, family="H3")
    validate_wave(
        wave="P0",
        workers=workers,
        probe=probe,
        primary_repro_overlap=False,
        reducer_count=1,
    )
    pin_blas_thread_env(workers=workers)
    evidence = repo_root / "evidence" / "tase_hardening" / "v1"
    evidence.mkdir(parents=True, exist_ok=True)

    h1 = run_process_pool(H1_IDS, eval_h1_id, workers=min(workers, len(H1_IDS)))
    h2_keys = [(type_id, cell) for type_id in H2_TYPES for cell in H2_CELLS]
    h2 = run_process_pool(h2_keys, eval_h2_key, workers=min(workers, 32))
    h3_rows = list(build_h3_rows())
    h3 = run_process_pool(h3_rows, eval_h3_row, workers=workers)

    barriers = run_process_pool(("base", "intervention"), eval_h4_barrier, workers=2)
    exact = [solve_h4_exact(barrier) for barrier in barriers]
    certified = [barrier for barrier in barriers if barrier["barrier_a"] == "certified"]

    des_primary: list[dict[str, Any]] = []
    des_repro: list[dict[str, Any]] = []
    if certified:
        des_primary = _run_des_wave(
            certified, wave="primary", master_seed=PRIMARY_SEED, workers=workers
        )
        validate_wave(
            wave="R0",
            workers=workers,
            probe=probe,
            primary_repro_overlap=False,
            reducer_count=1,
        )
        des_repro = _run_des_wave(
            certified, wave="repro", master_seed=REPRO_SEED, workers=workers
        )

    merged_primary = [
        _merge_des(des_primary, plant_id=item["id"], wave="primary", n=H4_REPLICATIONS)
        for item in certified
    ]
    merged_repro = [
        _merge_des(des_repro, plant_id=item["id"], wave="repro", n=H4_REPLICATIONS)
        for item in certified
    ]
    tolerance = hoeffding_tolerance()
    cells = []
    for exact_row in exact:
        if exact_row["status"] != "exact":
            continue
        primary = next(
            item for item in merged_primary if item["plant_id"] == exact_row["id"]
        )
        for name in ("theta_g", "theta_l", "theta_b"):
            error = abs(
                float(exact_row["probabilities"][name]) - primary["probabilities"][name]
            )
            cells.append(
                {
                    "plant_id": exact_row["id"],
                    "estimand": name,
                    "exact": exact_row["probabilities"][name],
                    "des": primary["probabilities"][name],
                    "abs_error": error,
                    "tolerance": tolerance,
                    "compatible": error <= tolerance,
                }
            )

    report = {
        "scope_id": SCOPE_ID,
        "authorization_id": auth["authorization_id"],
        "authorization_sha256": APPROVED_QUANT_AUTH_SHA256,
        "probe": {
            "logical_cpus": probe.logical_cpus,
            "free_ram_gib": probe.free_ram_gib,
            "workers": workers,
        },
        "h1": h1,
        "h2": h2,
        "h3_summary": _h3_summary(h3),
        "h4_barrier": [
            {key: barrier[key] for key in barrier if key != "transitions"}
            for barrier in barriers
        ],
        "h4_exact": exact,
        "h4_des_primary": merged_primary,
        "h4_des_repro": merged_repro,
        "compatibility": cells,
        "hoeffding_tolerance": tolerance,
        "original_g6b_gate": "OPEN_PENDING",
        "article_core_v1_rewritten": False,
    }
    report_path = evidence / "tase_hardening_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (evidence / "h3_rows.json").write_text(
        json.dumps(h3, indent=2) + "\n", encoding="utf-8"
    )
    return report


def _h3_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    refused = sum(1 for row in rows if row["classification"] == "refused")
    return {
        "n_rows": len(rows),
        "enumerated": len(rows) - refused,
        "refused": refused,
        "max_state_count": max((int(row["state_count"]) for row in rows), default=0),
        "max_elapsed_s": max((float(row["elapsed_s"]) for row in rows), default=0.0),
    }


def _run_des_wave(
    certified: list[dict[str, Any]],
    *,
    wave: str,
    master_seed: int,
    workers: int,
) -> list[dict[str, Any]]:
    shard_payloads: list[dict[str, Any]] = []
    for barrier in certified:
        starts = _contiguous_starts(H4_REPLICATIONS, workers)
        for start, count in starts:
            shard_payloads.append(
                {
                    "barrier": barrier,
                    "start": start,
                    "count": count,
                    "master_seed": master_seed,
                    "wave": wave,
                }
            )
    return run_process_pool(shard_payloads, eval_h4_des_shard, workers=workers)


def _contiguous_starts(n: int, workers: int) -> list[tuple[int, int]]:
    plan = build_shard_plan(tuple(str(index) for index in range(n)), workers=workers)
    starts: list[tuple[int, int]] = []
    cursor = 0
    # rebuild contiguous blocks rather than striped shards
    base = n // workers
    rem = n % workers
    for worker in range(workers):
        count = base + (1 if worker < rem else 0)
        if count:
            starts.append((cursor, count))
            cursor += count
    del plan
    return starts


def main() -> int:
    import sys

    repo = Path(__file__).resolve().parents[2]
    if "--h4-v3" in sys.argv:
        report = run_h4_v3_waves(repo)
        print(
            json.dumps(
                {
                    "workers": report["probe"],
                    "barrier": [
                        (row["id"], row.get("barrier_a"), row.get("refusal_code"))
                        for row in report["h4_barrier"]
                    ],
                    "exact": report["h4_exact"],
                    "compatibility": report["compatibility"],
                },
                indent=2,
            )
        )
        return 0
    if "--h4-v2" in sys.argv:
        report = run_h4_v2_waves(repo)
        print(
            json.dumps(
                {
                    "workers": report["probe"],
                    "barrier": [
                        (row["id"], row.get("barrier_a"), row.get("refusal_code"))
                        for row in report["h4_barrier"]
                    ],
                    "compatibility": report["compatibility"],
                },
                indent=2,
            )
        )
        return 0
    report = run_authorized_waves(repo)
    print(
        json.dumps({"workers": report["probe"], "h3": report["h3_summary"]}, indent=2)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
