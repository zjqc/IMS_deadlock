"""Build publication-style figures from the frozen article-core evidence.

This script is deliberately read-only with respect to scientific evidence.  It
does not rerun exact solvers or simulations; it visualizes the committed JSON
artifacts under ``evidence/article_core/minimal_closure_v1``.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE = REPO_ROOT / "evidence/article_core/minimal_closure_v1"
DEFAULT_OUTPUT = REPO_ROOT / "docs/paper/figures"

COLORS = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
    "sky": "#56B4E9",
    "yellow": "#F0E442",
    "gray": "#6B7280",
    "light": "#F3F4F6",
    "dark": "#111827",
}

CASE_ORDER = [
    "g6b_cu_pc_dglobal_only_v1",
    "g6b_cu_pc_dlocal_a2b_single_kernel_v1",
    "g6b_cu_pc_dlocal_lts_multi_kernel_v1",
    "g6b_cu_nc_local_bypass_completes_v1",
    "g6b_cu_nc_dglobal_only_with_dlocal_v1",
    "g6b_article_bridge_competing_local_completion_v1",
]

CASE_LABELS = {
    "g6b_cu_pc_dglobal_only_v1": "G: global\ncontrol",
    "g6b_cu_pc_dlocal_a2b_single_kernel_v1": "L-A2b: local\nstructural",
    "g6b_cu_pc_dlocal_lts_multi_kernel_v1": "L-LTS: local\nmodel-specific",
    "g6b_cu_nc_local_bypass_completes_v1": "B: completion\nbypass",
    "g6b_cu_nc_dglobal_only_with_dlocal_v1": "P: global/local\nprecedence",
    "g6b_article_bridge_competing_local_completion_v1": "C: competing\nbridge",
}

ESTIMANDS = [
    "theta_global_before_success",
    "theta_local_before_success",
    "theta_selected_bad_before_success",
]

ESTIMAND_LABELS = {
    "theta_global_before_success": r"$\theta_G$",
    "theta_local_before_success": r"$\theta_L$",
    "theta_selected_bad_before_success": r"$\theta_B$",
}


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return value


def _configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "axes.edgecolor": COLORS["dark"],
            "axes.linewidth": 0.8,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def _save_figure(fig: Figure, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output_dir / f"{stem}.png",
        dpi=300,
        bbox_inches="tight",
        metadata={"Software": "IMS_deadlock article figure builder"},
    )
    fig.savefig(
        output_dir / f"{stem}.pdf",
        bbox_inches="tight",
        metadata={
            "Creator": "IMS_deadlock article figure builder",
            "Producer": "Matplotlib",
            "CreationDate": None,
            "ModDate": None,
        },
    )
    plt.close(fig)


def _box(
    ax: Axes,
    x: float,
    y: float,
    width: float,
    height: float,
    text: str,
    *,
    color: str,
    edge: str | None = None,
    fontsize: float = 9.0,
) -> None:
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.018,rounding_size=0.018",
        facecolor=color,
        edgecolor=edge or COLORS["dark"],
        linewidth=1.1,
    )
    ax.add_patch(patch)
    ax.text(
        x + width / 2,
        y + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=COLORS["dark"],
        linespacing=1.25,
    )


def _arrow(
    ax: Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = COLORS["gray"],
    style: str = "-|>",
    connection: str = "arc3",
) -> None:
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle=style,
        mutation_scale=12,
        linewidth=1.2,
        color=color,
        connectionstyle=connection,
    )
    ax.add_patch(arrow)


def build_research_chain(output_dir: Path) -> None:
    """Draw the model-theory-case-evidence closure used by the manuscript."""

    fig, ax = plt.subplots(figsize=(11.2, 6.4))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    rows = [
        (
            0.77,
            [
                ("IMS-RAS$^{CW}$\nsemantics", COLORS["sky"]),
                ("Finite stable LTS\n(P1)", COLORS["sky"]),
                ("Capacity-ready\nblocking core (P2)", COLORS["sky"]),
                ("Global-first\ntarget $D_G$", COLORS["sky"]),
            ],
        ),
        (
            0.47,
            [
                ("Local candidate\nkernels", "#FCE8D5"),
                ("A2b request-closed\nsufficient route", "#FCE8D5"),
                ("Complete-LTS\nnonreachability route", "#FCE8D5"),
                ("Stopped target\n$D_L$", "#FCE8D5"),
            ],
        ),
        (
            0.17,
            [
                (r"Disjoint target" "\n" r"$D_G\uplus D_L\uplus F$", "#E3F4EA"),
                ("Exact CTMC\ncommittor / time", "#E3F4EA"),
                ("Frozen DES\n4,096 replications", "#E3F4EA"),
                ("18/18 compatible\nscoped closure", "#E3F4EA"),
            ],
        ),
    ]

    x_positions = [0.035, 0.285, 0.535, 0.785]
    width = 0.18
    height = 0.135
    for y, items in rows:
        for index, (label, color) in enumerate(items):
            _box(ax, x_positions[index], y, width, height, label, color=color)
            if index < len(items) - 1:
                _arrow(
                    ax,
                    (x_positions[index] + width, y + height / 2),
                    (x_positions[index + 1], y + height / 2),
                )

    # The global and local branches converge without implying that one is a
    # prerequisite for the other.  Route the merger through the whitespace at
    # the right and between the second and third rows to avoid crossing boxes.
    ax.plot(
        [0.965, 0.985, 0.985],
        [0.77 + height / 2, 0.77 + height / 2, 0.38],
        color=COLORS["gray"],
        linewidth=1.2,
    )
    ax.plot(
        [0.965, 0.985],
        [0.47 + height / 2, 0.47 + height / 2],
        color=COLORS["gray"],
        linewidth=1.2,
    )
    ax.plot(
        [0.985, 0.125],
        [0.38, 0.38],
        color=COLORS["gray"],
        linewidth=1.2,
    )
    _arrow(ax, (0.125, 0.38), (0.125, 0.305))

    ax.text(
        0.5,
        0.965,
        "Figure 1. Scoped theory-to-case-to-evidence research chain",
        ha="center",
        va="top",
        fontsize=13,
        weight="bold",
    )
    ax.text(
        0.5,
        0.04,
        "Boundary: the local target is a verified stopped-process first-hit set; "
        "it is not asserted to be a universal plant terminal class.",
        ha="center",
        va="bottom",
        fontsize=9.5,
        color=COLORS["vermillion"],
    )
    _save_figure(fig, output_dir, "figure_1_research_chain")


def _node(
    ax: Axes,
    x: float,
    y: float,
    text: str,
    *,
    color: str,
    radius: float = 0.075,
) -> None:
    circle = plt.Circle(
        (x, y),
        radius,
        facecolor=color,
        edgecolor=COLORS["dark"],
        linewidth=1.0,
        zorder=3,
    )
    ax.add_patch(circle)
    ax.text(x, y, text, ha="center", va="center", fontsize=8.2, zorder=4)


def _panel_base(ax: Axes, title: str, subtitle: str) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color("#D1D5DB")
    ax.set_title(title, loc="left", weight="bold", pad=7)
    ax.text(0.02, 0.91, subtitle, transform=ax.transAxes, fontsize=8.4)


def build_case_panel(
    output_dir: Path,
    certificates: dict[str, dict[str, Any]],
) -> None:
    """Draw the logical role of all six frozen article cases."""

    fig, axes = plt.subplots(2, 3, figsize=(11.5, 6.9))
    panels = axes.ravel()

    _panel_base(
        panels[0],
        "A  Time-zero global witness",
        "admission: time_zero_global",
    )
    _node(panels[0], 0.5, 0.48, "$D_G$", color="#C9E8F7", radius=0.13)
    panels[0].text(0.5, 0.19, r"$\theta_G=\theta_B=1$", ha="center")

    _panel_base(
        panels[1],
        "B  A2b local structural witness",
        "request-closed kernel; plant still has outer motion",
    )
    _node(panels[1], 0.36, 0.46, "$D_L$", color="#FCE8D5", radius=0.12)
    _node(panels[1], 0.74, 0.46, "outer", color=COLORS["light"], radius=0.10)
    _arrow(panels[1], (0.48, 0.46), (0.64, 0.46), style="<->")
    panels[1].text(0.5, 0.17, r"$\theta_L=\theta_B=1$", ha="center")

    _panel_base(
        panels[2],
        "C  Complete-LTS local witness",
        "two local kernels; completion unreachable\nfrom either local kernel",
    )
    _node(panels[2], 0.17, 0.52, "$s_0$", color=COLORS["light"])
    _node(panels[2], 0.47, 0.68, "$L_1$", color="#FCE8D5")
    _node(panels[2], 0.47, 0.34, "$L_2$", color="#FCE8D5")
    _node(panels[2], 0.77, 0.51, "post", color=COLORS["light"])
    _node(panels[2], 0.92, 0.16, "$F$", color="#E3F4EA", radius=0.06)
    _arrow(panels[2], (0.24, 0.55), (0.39, 0.65))
    _arrow(panels[2], (0.24, 0.49), (0.39, 0.37))
    _arrow(panels[2], (0.55, 0.66), (0.69, 0.55))
    _arrow(panels[2], (0.55, 0.36), (0.69, 0.47))
    _arrow(panels[2], (0.70, 0.57), (0.55, 0.65))
    _arrow(panels[2], (0.70, 0.45), (0.55, 0.37))
    panels[2].text(0.86, 0.29, "unreachable", fontsize=7.6, color=COLORS["gray"])

    _panel_base(
        panels[3],
        "D  Completion-bypass boundary",
        "candidate rejected from $D_L$",
    )
    _node(panels[3], 0.18, 0.48, "cand.", color="#FCE8D5")
    _node(panels[3], 0.50, 0.48, "bypass", color=COLORS["light"], radius=0.10)
    _node(panels[3], 0.82, 0.48, "$F$", color="#E3F4EA")
    _arrow(panels[3], (0.26, 0.48), (0.39, 0.48))
    _arrow(panels[3], (0.61, 0.48), (0.73, 0.48))
    panels[3].text(0.5, 0.17, r"$\theta_B=0$", ha="center")

    _panel_base(
        panels[4],
        "E  Global-before-local precedence",
        "same state looks locally blocked but is counted once",
    )
    _node(panels[4], 0.42, 0.49, "$D_G$", color="#C9E8F7", radius=0.13)
    _node(panels[4], 0.60, 0.49, "local\ncandidate", color="#FCE8D5", radius=0.13)
    panels[4].text(
        0.5,
        0.18,
        r"assigned to $D_G$; $D_G\cap D_L=\varnothing$",
        ha="center",
    )

    _panel_base(
        panels[5],
        "F  Competing local/completion bridge",
        "rates 1 and 2 from the same initial state",
    )
    _node(panels[5], 0.19, 0.49, "$s_0$", color=COLORS["light"])
    _node(panels[5], 0.75, 0.68, "$D_L$", color="#FCE8D5", radius=0.10)
    _node(panels[5], 0.75, 0.29, "$F$", color="#E3F4EA", radius=0.10)
    _arrow(panels[5], (0.27, 0.53), (0.64, 0.65), color=COLORS["orange"])
    _arrow(panels[5], (0.27, 0.45), (0.64, 0.32), color=COLORS["green"])
    panels[5].text(0.47, 0.68, r"$\lambda_L=1$", color=COLORS["orange"])
    panels[5].text(0.47, 0.28, r"$\lambda_F=2$", color=COLORS["green"])
    panels[5].text(0.5, 0.09, r"$\theta_L=1/(1+2)=1/3$", ha="center")

    expected_routes = {
        CASE_ORDER[0]: "time_zero_global",
        CASE_ORDER[1]: "A2b_request_closed",
        CASE_ORDER[2]: "complete_LTS_nonreachability",
        CASE_ORDER[3]: "boundary_control_not_admitted",
        CASE_ORDER[4]: "global_precedence_control",
        CASE_ORDER[5]: "A2b_request_closed",
    }
    for case_id, route in expected_routes.items():
        observed = certificates[case_id]["admission_route"]
        if observed != route:
            raise ValueError(f"Unexpected route for {case_id}: {observed}")

    fig.suptitle(
        "Figure 2. Six-case constructive and boundary-control panel",
        fontsize=13,
        weight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    _save_figure(fig, output_dir, "figure_2_case_panel")


def _result_index(
    payload: dict[str, Any],
    key: str,
) -> dict[str, dict[str, Any]]:
    rows = payload[key]
    if not isinstance(rows, list):
        raise TypeError(f"Expected list at {key}")
    return {str(row["case_id"]): row for row in rows}


def build_exact_des_comparison(
    output_dir: Path,
    exact: dict[str, dict[str, Any]],
    des: dict[str, dict[str, Any]],
    report: dict[str, Any],
) -> None:
    """Compare exact and DES probabilities and display all cell errors."""

    fig, (ax_top, ax_bottom) = plt.subplots(
        2,
        1,
        figsize=(11.2, 7.2),
        gridspec_kw={"height_ratios": [1.35, 1]},
    )
    x_positions = list(range(len(CASE_ORDER)))
    exact_bad = [
        float(exact[case_id]["probabilities"]["theta_selected_bad_before_success"])
        for case_id in CASE_ORDER
    ]
    des_bad = [
        float(des[case_id]["probabilities"]["theta_selected_bad_before_success"])
        for case_id in CASE_ORDER
    ]

    for x_value, exact_value, des_value in zip(
        x_positions,
        exact_bad,
        des_bad,
        strict=True,
    ):
        ax_top.plot(
            [x_value, x_value],
            [exact_value, des_value],
            color="#9CA3AF",
            linewidth=1.2,
            zorder=1,
        )
    ax_top.scatter(
        x_positions,
        exact_bad,
        marker="o",
        s=72,
        facecolors="white",
        edgecolors=COLORS["blue"],
        linewidths=1.8,
        label="Exact CTMC",
        zorder=3,
    )
    ax_top.scatter(
        x_positions,
        des_bad,
        marker="x",
        s=70,
        color=COLORS["vermillion"],
        linewidths=2.0,
        label="DES (4,096 runs)",
        zorder=4,
    )
    ax_top.set_ylabel(r"Selected-bad first-hit probability $\theta_B$")
    ax_top.set_ylim(-0.06, 1.08)
    ax_top.set_xticks(x_positions, [CASE_LABELS[item] for item in CASE_ORDER])
    ax_top.grid(axis="y", color="#E5E7EB", linewidth=0.8)
    ax_top.legend(loc="lower left", frameon=False, ncol=2)
    ax_top.set_title(
        "A  Exact and DES agreement on the same stopped-process target",
        loc="left",
        weight="bold",
    )

    cells = report["comparison_cells"]
    tolerance = float(cells[0]["tolerance"])
    offsets = [-0.22, 0.0, 0.22]
    colors = [COLORS["blue"], COLORS["orange"], COLORS["purple"]]
    markers = ["o", "s", "^"]
    for estimand, offset, color, marker in zip(
        ESTIMANDS,
        offsets,
        colors,
        markers,
        strict=True,
    ):
        errors = []
        for case_id in CASE_ORDER:
            matching = [
                row
                for row in cells
                if row["case_id"] == case_id and row["estimand"] == estimand
            ]
            if len(matching) != 1:
                raise ValueError(f"Missing comparison cell for {case_id}/{estimand}")
            errors.append(float(matching[0]["absolute_error"]))
        ax_bottom.scatter(
            [value + offset for value in x_positions],
            errors,
            color=color,
            marker=marker,
            s=48,
            label=ESTIMAND_LABELS[estimand],
            zorder=3,
        )
    ax_bottom.axhline(
        tolerance,
        color=COLORS["vermillion"],
        linestyle="--",
        linewidth=1.3,
        label=f"compatibility tolerance = {tolerance:.5f}",
    )
    ax_bottom.set_ylabel("Absolute error")
    ax_bottom.set_xticks(x_positions, [CASE_LABELS[item] for item in CASE_ORDER])
    ax_bottom.set_ylim(-0.0015, tolerance * 1.18)
    ax_bottom.grid(axis="y", color="#E5E7EB", linewidth=0.8)
    ax_bottom.legend(loc="upper left", frameon=False, ncol=4)
    ax_bottom.set_title(
        "B  All 18 predeclared comparison cells",
        loc="left",
        weight="bold",
    )

    max_error = max(float(row["absolute_error"]) for row in cells)
    fig.suptitle(
        "Figure 3. Frozen exact-DES compatibility "
        f"(18/18 cells; maximum error {max_error:.6f})",
        fontsize=13,
        weight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    _save_figure(fig, output_dir, "figure_3_exact_des_comparison")


def build_mean_stopping_time(
    output_dir: Path,
    exact: dict[str, dict[str, Any]],
    des: dict[str, dict[str, Any]],
) -> None:
    """Compare exact and simulated mean stopping/absorption times."""

    fig, ax = plt.subplots(figsize=(11.2, 4.8))
    x_positions = list(range(len(CASE_ORDER)))
    width = 0.34
    exact_time = [float(exact[item]["mean_absorption_time"]) for item in CASE_ORDER]
    des_time = [float(des[item]["mean_absorption_time"]) for item in CASE_ORDER]
    ax.bar(
        [value - width / 2 for value in x_positions],
        exact_time,
        width,
        color=COLORS["blue"],
        label="Exact CTMC",
    )
    ax.bar(
        [value + width / 2 for value in x_positions],
        des_time,
        width,
        color=COLORS["orange"],
        hatch="//",
        edgecolor=COLORS["dark"],
        linewidth=0.6,
        label="DES mean",
    )
    ax.set_ylabel("Mean stopping time")
    ax.set_xticks(x_positions, [CASE_LABELS[item] for item in CASE_ORDER])
    ax.grid(axis="y", color="#E5E7EB", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=2)
    ax.set_title(
        "Figure 4. Exact and DES mean stopping times on the frozen cases",
        loc="left",
        fontsize=13,
        weight="bold",
    )
    fig.tight_layout()
    _save_figure(fig, output_dir, "figure_4_mean_stopping_time")


def _validate_case_sets(*collections: Iterable[str]) -> None:
    expected = set(CASE_ORDER)
    for collection in collections:
        observed = set(collection)
        if observed != expected:
            missing = sorted(expected - observed)
            extra = sorted(observed - expected)
            raise ValueError(f"Case-set mismatch; missing={missing}, extra={extra}")


def build_all(evidence_dir: Path, output_dir: Path) -> None:
    exact_payload = _read_json(evidence_dir / "exact_results.json")
    des_payload = _read_json(evidence_dir / "des_results.json")
    certificate_payload = _read_json(evidence_dir / "article_case_certificates.json")
    report = _read_json(evidence_dir / "article_closure_report.json")

    exact = _result_index(exact_payload, "exact_results")
    des = _result_index(des_payload, "des_results")
    certificates = _result_index(certificate_payload, "case_certificates")
    _validate_case_sets(exact, des, certificates)

    if report["comparison_cell_count"] != 18:
        raise ValueError("The frozen article report must contain 18 cells")
    if not report["all_cells_compatible"]:
        raise ValueError("The frozen article report is not fully compatible")
    if report["original_g6b_gate"] != "OPEN_PENDING":
        raise ValueError("Unexpected original G6-B gate status")

    _configure_style()
    build_research_chain(output_dir)
    build_case_panel(output_dir, certificates)
    build_exact_des_comparison(output_dir, exact, des, report)
    build_mean_stopping_time(output_dir, exact, des)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=DEFAULT_EVIDENCE,
        help="Frozen article evidence directory",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Directory for PNG and PDF figures",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    build_all(args.evidence_dir.resolve(), args.output_dir.resolve())


if __name__ == "__main__":
    main()
