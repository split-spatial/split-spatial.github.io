#!/usr/bin/env python
"""Per-category bars for the project website: VSIBench (static/images/vsib_category_bars.png)
and ReVSI (static/images/revsi_category_bars.png). Run with the benchmark key as the argument.

Same family as the poster's VSTIBench category chart
(agent-project-paper/figure_kit/poster_eccv/make_category_bars.py, v21): three bars per
category, Baseline (red), SPLIT (green), SPLIT + GT (blue), legend in one row at the top,
the planner note under it, a centered panel title, value labels on every bar.

Numbers: the VSIBench analysis subset (exact-500 cohort with the 50-question answerable
appearance cohort, USER sanction 2026-08-24), the same cohort behind the paper's 88.8 cell.
  - SPLIT + GT per category: paper Table 2 ground-truth diagnostic row, score-index role
    exact500_gt_r1339_cyfix_88p32 with the appearance cell from the screen-ii cohort
    (bank req235_composite_cyfix_topup7_20260920T1208Z) -> composite 91.8.
  - Baseline / SPLIT per category: R899_BASELINE_TOPUP_RESULT.md and R914_SPLIT_TOPUP_RESULT.md
    (487-cohort tables; every non-route category has all 50 members), with route from
    R930_EXACT500_CELLS.json (24/50, 32/50) and appearance from the screen-ii cohort in
    REQ155_V3_CELLS_GT_QWEN_RESULT.md (38/50, 36/50). Relative direction is the mean of the
    easy/medium/hard difficulties, as in the official 8-task macro.
  Check: the 8-task macros reproduce the printed composites 56.8583 / 65.2917 / 88.7833.
Counting is an oracle ceiling in the GT arm; appearance order uses the 50-question cohort.

ReVSI rows are the paper's ReVSI table (tab:revsi) verbatim: Baseline and SPLIT on the full
benchmark (32 frames), SPLIT + GT on the 981-question analysis subset that excludes 18 route
questions without complete annotations; counting is an oracle ceiling. Means reproduce 63.8 / 71.5 / 91.0.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "Nimbus Sans", "Liberation Sans", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "static", "images")
GT_MARK = os.environ.get("CHART_GT_MARK", "†")   # dagger on the GT legend entry, footnoted on the page

COL_W = (35.25 - 2 * 0.5 - 2 * 0.3) / 3.0      # the poster chart's width, so every chart shares one look
FIG_H = 5.0
TICK, AXLBL, VALUE, LEGEND, ROWTITLE = 15, 16, 15, 16, 18
RED, GREEN, BLUE, INK = "#EA4335", "#34A853", "#4285F4", "#202124"

BENCH = {
    "vsib": dict(
        title="VSIBench", out="vsib_category_bars.png",
        cats=["Object\nCount", "Absolute\nDistance", "Object\nSize", "Room\nSize",
              "Relative\nDistance", "Relative\nDirection", "Route\nPlan", "Appearance\nOrder"],
        baseline=[52.0, 38.4, 63.2, 62.6, 62.0, 52.7, 48.0, 76.0],
        split=[50.0, 54.2, 62.2, 54.6, 78.0, 87.3, 64.0, 72.0],
        split_gt=[95.4, 92.4, 97.0, 92.4, 94.0, 99.3, 64.0, 100.0],
        # macro check against the printed composites (unrounded relative direction)
        check=(([52.0, 38.4, 63.2, 62.6, 62.0, (60 + 64 + 34) / 3, 48.0, 76.0], 56.8583),
               ([50.0, 54.2, 62.2, 54.6, 78.0, (94 + 88 + 80) / 3, 64.0, 72.0], 65.2917),
               ([95.4, 92.4, 97.0, 92.4, 94.0, 99.3, 64.0, 100.0], 91.8125)),
    ),
    "revsi": dict(
        title="ReVSI", out="revsi_category_bars.png",
        cats=["Object\nCount", "Absolute\nDistance", "Object\nSize", "Room\nSize",
              "Relative\nDistance", "Relative\nDirection", "Route\nPlan"],
        baseline=[64.6, 59.6, 76.8, 61.9, 67.0, 58.0, 58.5],
        split=[58.8, 66.8, 64.2, 50.3, 84.2, 93.2, 82.9],
        split_gt=[86.7, 98.2, 85.0, 79.7, 97.9, 98.3, 91.1],
        check=(([64.6, 59.6, 76.8, 61.9, 67.0, 58.0, 58.5], 63.8),
               ([58.8, 66.8, 64.2, 50.3, 84.2, 93.2, 82.9], 71.5),
               ([86.7, 98.2, 85.0, 79.7, 97.9, 98.3, 91.1], 91.0)),
    ),
}


def main(key):
    b = BENCH[key]
    CATS, BASELINE, SPLIT, SPLIT_GT = b["cats"], b["baseline"], b["split"], b["split_gt"]
    for vec, ref in b["check"]:
        assert abs(sum(vec) / len(vec) - ref) < 0.06, (key, sum(vec) / len(vec), ref)
    OUT = os.path.join(OUT_DIR, b["out"])
    x = np.arange(len(CATS))
    w = 0.28
    fig, ax = plt.subplots(figsize=(COL_W, FIG_H))
    series = [("Baseline (Gemini 3.1 Pro)", BASELINE, RED), ("SPLIT (Ours)", SPLIT, GREEN), ("SPLIT (Ours) + GT" + GT_MARK, SPLIT_GT, BLUE)]
    values = [BASELINE, SPLIT, SPLIT_GT]
    labels = {}
    for i, (label, vals, color) in enumerate(series):
        offs = (i - 1) * w
        ax.bar(x + offs, vals, width=w, color=color, label=label, zorder=3, edgecolor=color, linewidth=0)
        for j, (xi, v) in enumerate(zip(x + offs, vals)):
            labels[(i, j)] = ax.text(xi, v + 1.8, f"{v:.1f}", ha="center", va="bottom",
                                     fontsize=VALUE, fontweight="bold", color=INK, clip_on=False)
    ax.set_xlim(-0.5, len(CATS) - 0.5)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_ylabel("Accuracy", fontsize=AXLBL, labelpad=8)
    ax.set_xticks(x)
    ax.set_xticklabels(CATS, fontsize=TICK)
    ax.tick_params(axis="y", labelsize=TICK)
    ax.tick_params(axis="x", length=0, pad=6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#DADCE0", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    fig.legend(loc="upper center", bbox_to_anchor=(0.535, 1.0), ncol=3,
               fontsize=LEGEND, frameon=False, columnspacing=1.8, handlelength=1.5)
    fig.canvas.draw()
    leg_y0 = fig.legends[0].get_window_extent(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted()).y0
    note_y = leg_y0 - 0.025
    fig.text(0.535, note_y, "SPLIT (Ours) always uses Gemini 3.1 Pro as the planner VLM.", ha="center", va="top",
             fontsize=LEGEND - 1, style="italic", color=INK)
    ax.set_title(b["title"], fontsize=ROWTITLE, fontweight="bold", pad=24, color=INK)
    fig.subplots_adjust(left=0.075, right=0.995, top=note_y - 0.17, bottom=0.15)
    # lift the taller label only where two adjacent rendered labels overlap
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    pad = 2.0 * fig.dpi / 72.0
    per_px = 1.0 / (ax.transData.transform((0, 1))[1] - ax.transData.transform((0, 0))[1])
    n_lift = 0
    for j in range(len(CATS)):
        for a, b in ((0, 1), (1, 2)):
            ta, tb = labels[(a, j)], labels[(b, j)]
            ba, bb = ta.get_window_extent(rend), tb.get_window_extent(rend)
            if ba.x1 + pad > bb.x0 and bb.x1 + pad > ba.x0 and ba.y1 + pad > bb.y0 and bb.y1 + pad > ba.y0:
                hi, lo = (ta, tb) if values[a][j] >= values[b][j] else (tb, ta)
                bh, bl = hi.get_window_extent(rend), lo.get_window_extent(rend)
                hi.set_y(hi.get_position()[1] + (bl.y1 + pad - bh.y0) * per_px)
                n_lift += 1
    print("%s category chart: %d lifted labels" % (key, n_lift))
    fig.savefig(OUT, dpi=300, facecolor="white")
    plt.close(fig)
    print("wrote", os.path.abspath(OUT))


if __name__ == "__main__":
    import sys
    for key in (sys.argv[1:] or list(BENCH)):
        main(key)
