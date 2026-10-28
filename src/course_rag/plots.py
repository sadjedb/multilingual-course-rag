"""Shared matplotlib style for the notebooks' figures."""

import matplotlib.pyplot as plt

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e4e3df"
MUTED = "#b5b3ad"  # baselines / de-emphasised series
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
LANG_LABELS = {"ar": "Arabic", "fr": "French", "en": "English"}


def setup() -> None:
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": GRID, "axes.labelcolor": TEXT_2, "text.color": TEXT,
        "xtick.color": TEXT_2, "ytick.color": TEXT_2, "axes.grid": True, "grid.color": GRID,
        "grid.linewidth": 0.8, "axes.axisbelow": True, "axes.spines.top": False, "axes.spines.right": False,
        "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "legend.frameon": False, "savefig.dpi": 160, "savefig.bbox": "tight",
    })


def label_bars(ax, bars, fmt="{:.2f}") -> None:
    """Value labels at the end of each bar, in text ink (never the bar color)."""
    for bar in bars:
        if bars.orientation == "horizontal":
            v = bar.get_width()
            ax.annotate(fmt.format(v), (v, bar.get_y() + bar.get_height() / 2), xytext=(4, 0),
                        textcoords="offset points", va="center", fontsize=8.5, color=TEXT_2)
        else:
            v = bar.get_height()
            ax.annotate(fmt.format(v), (bar.get_x() + bar.get_width() / 2, v), xytext=(0, 3),
                        textcoords="offset points", ha="center", fontsize=8.5, color=TEXT_2)
