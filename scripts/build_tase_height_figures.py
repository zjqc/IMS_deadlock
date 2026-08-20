"""Build T-ASE height +1 figures from write-once evidence JSON.

Read-only on scientific evidence. Does not rerun CTMC or DES.
Outputs 300 DPI PNG (VS Code preview) and vector PDF.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "paper" / "figures"
EVIDENCE = REPO_ROOT / "evidence" / "tase_hardening"

COLORS = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
    "sky": "#56B4E9",
    "gray": "#6B7280",
    "light": "#F3F4F6",
    "dark": "#111827",
    "yes": "#009E73",
    "no": "#D55E00",
}


def _read(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(path)
    return payload


def _style() -> None:
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


def _save(fig: Figure, stem: str) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT / f"{stem}.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUTPUT / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote", OUTPUT / f"{stem}.png")


def _exact_by_id(report: dict) -> dict[str, dict]:
    return {str(row["id"]): row for row in report["h7_exact"]}


def build_h7_kpis(h7: dict) -> None:
    rows = _exact_by_id(h7)
    base = rows["H7_v4_base"]
    intervention = rows["H7_v4_intervention"]
    labels = [
        r"$\theta^{\mathrm{G}}$",
        r"$\theta^{\mathrm{L}}$",
        r"$\theta^{\mathrm{B}}$",
    ]
    keys = ["theta_g", "theta_l", "theta_b"]
    base_p = [float(base["probabilities"][k]) for k in keys]
    int_p = [abs(float(intervention["probabilities"][k])) for k in keys]
    base_m = float(base["mean_stopped_time"])
    int_m = float(intervention["mean_stopped_time"])

    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.15), constrained_layout=True)
    x = range(3)
    w = 0.36
    axes[0].bar(
        [i - w / 2 for i in x],
        base_p,
        width=w,
        color=COLORS["vermillion"],
        label="Base (cap V = 1)",
    )
    axes[0].bar(
        [i + w / 2 for i in x],
        int_p,
        width=w,
        color=COLORS["green"],
        label="Extra AGV slot",
    )
    axes[0].set_xticks(list(x), labels)
    axes[0].set_ylim(0, 1.05)
    axes[0].set_ylabel("First-hit probability")
    axes[0].set_title("Stopped first-hit probabilities")
    axes[0].legend(frameon=False, loc="upper left")
    axes[0].axhline(7 / 12, color=COLORS["gray"], lw=0.7, ls="--")
    axes[0].text(2.15, 7 / 12 + 0.03, r"$7/12$", color=COLORS["gray"], fontsize=8)

    axes[1].bar(
        [0, 1],
        [base_m, int_m],
        color=[COLORS["vermillion"], COLORS["green"]],
        width=0.55,
    )
    axes[1].set_xticks([0, 1], ["Base", "Extra AGV slot"])
    axes[1].set_ylabel(r"Mean stopped time $m$")
    axes[1].set_title("Mean time to $A^{\\dagger}$")
    axes[1].set_ylim(0, max(base_m, int_m) * 1.25)
    for i, value in enumerate([base_m, int_m]):
        axes[1].text(i, value + 0.12, f"{value:.3f}", ha="center", fontsize=9)
    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    _save(fig, "fig_h7_island_kpis")


def _round_box(ax, x, y, w, h, text, facecolor, title=None) -> None:
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.0,
        edgecolor=COLORS["dark"],
        facecolor=facecolor,
    )
    ax.add_patch(box)
    if title:
        ax.text(
            x + w / 2,
            y + h - 0.08,
            title,
            ha="center",
            va="top",
            fontsize=8,
            color=COLORS["gray"],
        )
        ax.text(
            x + w / 2,
            y + h / 2 - 0.02,
            text,
            ha="center",
            va="center",
            fontsize=8.5,
        )
    else:
        ax.text(
            x + w / 2,
            y + h / 2,
            text,
            ha="center",
            va="center",
            fontsize=8.5,
        )


def build_h7_story() -> None:
    fig, ax = plt.subplots(figsize=(7.6, 3.35))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.2)
    ax.axis("off")
    ax.set_title("Positive-time local hit on the machine–AGV island")

    _round_box(
        ax,
        0.25,
        2.35,
        2.9,
        1.55,
        "A idle\nB idle\nC holds M2, in service",
        COLORS["sky"],
        title=r"$t=0$: transient $x_0$",
    )
    _round_box(
        ax,
        3.55,
        2.35,
        3.1,
        1.55,
        "A holds M1, requests V\nB holds V, requests M1\nC still has a plant arc",
        "#F4C7B0",
        title=r"first hit $D^{\mathrm{L}}$",
    )
    _round_box(
        ax,
        7.0,
        2.35,
        2.75,
        1.55,
        r"V capacity 2" + "\nkernel not closed\n" + r"$\theta^{\mathrm{B}}=0$",
        "#C8E6C9",
        title="extra AGV slot",
    )
    ax.annotate(
        "",
        xy=(3.5, 3.1),
        xytext=(3.2, 3.1),
        arrowprops={"arrowstyle": "->", "color": COLORS["dark"], "lw": 1.2},
    )
    ax.annotate(
        "",
        xy=(6.95, 3.1),
        xytext=(6.7, 3.1),
        arrowprops={"arrowstyle": "->", "color": COLORS["dark"], "lw": 1.2},
    )
    ax.text(
        3.35,
        2.12,
        r"$A$-start, $A$-svc, $B$-start",
        ha="center",
        fontsize=7.5,
        color=COLORS["gray"],
    )
    ax.text(
        5.0,
        1.55,
        "Plant graph is not a terminal SCC: C can still move.\n"
        r"$\theta^{\mathrm{L}}=0.537$, $\theta^{\mathrm{B}}=7/12$, "
        r"$m=3.596$ (64 states).",
        ha="center",
        va="center",
        fontsize=9,
    )
    ax.text(
        5.0,
        0.55,
        "Time-zero clothing (retained, not overwritten): already in "
        r"$D^{\mathrm{L}}$ at $t=0$ ($\theta^{\mathrm{L}}=1$, $m=0$).",
        ha="center",
        fontsize=8,
        color=COLORS["gray"],
    )
    _save(fig, "fig_h7_island_story")


def build_h6_fields(h5: dict, h6: dict) -> None:
    labels = {
        "H5_unit_pair_fields123": "H5 unit pair",
        "H5_unit_triple_fields123": "H5 unit triple",
        "H5_reachable_pair_fields123": "H5 reachable pair",
        "H5_wrong_r_crp_zero_match": "H5 wrong $R^\\star$",
        "H5_outside_agv_and": r"H5 AGV $\wedge$ buf",
        "H5_residual_no_local_family": "H5 residual cycle",
        "H6_A_ezpeleta_unit_s3pr": "H6-A S3PR core",
        "H6_B_agv_distortion": "H6-B AGV distort.",
    }
    rows: list[tuple[str, dict, bool]] = []
    for row in h5["rows"]:
        key = str(row["id"])
        rows.append((labels.get(key, key), row["fields"], False))
    for row in h6["rows"]:
        key = str(row["id"])
        rows.append((labels.get(key, key), row["fields"], True))

    names = [item[0] for item in rows]
    field_keys = [
        ("reachable", "Reachable"),
        ("local_family_available", "Local family"),
        ("matching_kernel_count", r"Match $|K|$"),
        ("s4pr_overlap", "Embedding"),
    ]
    data = []
    for _name, fields, _embed in rows:
        data.append(
            [
                1.0 if fields["reachable"] else 0.0,
                1.0 if fields["local_family_available"] else 0.0,
                1.0 if int(fields["matching_kernel_count"]) >= 1 else 0.0,
                1.0 if fields["s4pr_overlap"] else 0.0,
            ]
        )

    fig, ax = plt.subplots(figsize=(7.4, 4.2), constrained_layout=True)
    image = ax.imshow(data, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    image.set_clim(0, 1)
    ax.set_xticks(range(4), [label for _key, label in field_keys])
    ax.set_yticks(range(len(names)), names)
    ax.set_title("Proposition 4 four-field diagnostic")
    ax.axhline(5.5, color=COLORS["dark"], lw=1.0)
    ax.text(
        3.55,
        2.5,
        "no embedding",
        rotation=90,
        va="center",
        fontsize=8,
        color=COLORS["gray"],
    )
    ax.text(
        3.55,
        6.5,
        "H6",
        rotation=90,
        va="center",
        fontsize=8,
        color=COLORS["dark"],
    )
    for i, row in enumerate(data):
        for j, value in enumerate(row):
            ax.text(
                j,
                i,
                "yes" if value >= 0.5 else "no",
                ha="center",
                va="center",
                fontsize=8,
                color="white" if value < 0.5 else COLORS["dark"],
            )
    ax.set_xlabel("Field (agreement only if all four are yes)")
    _save(fig, "fig_h6_four_field")


def build_h8(h7: dict, h8: dict) -> None:
    base = _exact_by_id(h7)["H7_v4_base"]
    plant_b = float(base["probabilities"]["theta_b"])
    plant_m = float(base["mean_stopped_time"])
    row = h8["row"]
    n_states = int(row["n_states"])
    n_safe = int(row["n_safe"])
    n_cut = int(row["n_disabled_state_events"])
    sup = row["supervised_exact"]
    sup_b = abs(float(sup["probabilities"]["theta_b"]))
    sup_m = float(sup["mean_stopped_time"])

    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.15), constrained_layout=True)
    axes[0].bar(
        [0, 1],
        [n_states, n_safe],
        color=[COLORS["blue"], COLORS["green"]],
        width=0.55,
    )
    axes[0].set_xticks([0, 1], [r"Plant $|X|$", r"Safe $|X_{\mathrm{safe}}|$"])
    axes[0].set_ylabel("Stable states")
    axes[0].set_title(f"Explicit-graph supervisor ({n_cut} cuts)")
    for i, value in enumerate([n_states, n_safe]):
        axes[0].text(i, value + 1.2, str(value), ha="center", fontsize=9)

    axes[1].bar(
        [0, 1],
        [plant_b, sup_b],
        color=[COLORS["vermillion"], COLORS["green"]],
        width=0.55,
    )
    axes[1].set_xticks([0, 1], ["Unsupervised", "Supervised"])
    axes[1].set_ylabel(r"$\theta^{\mathrm{B}}$")
    axes[1].set_title("Selected-bad first-hit probability")
    axes[1].set_ylim(0, 1.05)
    axes[1].text(
        0,
        plant_b + 0.04,
        f"{plant_b:.3f}\n$m$={plant_m:.2f}",
        ha="center",
        fontsize=8,
    )
    axes[1].text(1, 0.06, f"{sup_b:.3f}\n$m$={sup_m:.2f}", ha="center", fontsize=8)
    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    _save(fig, "fig_h8_supervisor")


def main() -> None:
    _style()
    h7 = _read(EVIDENCE / "h7_island_v4" / "tase_hardening_h7_report.json")
    h6 = _read(EVIDENCE / "h6_embed" / "tase_hardening_h6_report.json")
    h5 = _read(EVIDENCE / "h5" / "tase_hardening_h5_report.json")
    h8 = _read(EVIDENCE / "h8_supervisor" / "tase_hardening_h8_report.json")
    build_h7_kpis(h7)
    build_h7_story()
    build_h6_fields(h5, h6)
    build_h8(h7, h8)


if __name__ == "__main__":
    main()
