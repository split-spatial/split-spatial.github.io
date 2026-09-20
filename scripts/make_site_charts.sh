#!/bin/bash
# Renders the three chart images for the website with the dagger marker on the GT legend entry.
# The benchmark and VSTIBench charts come from the poster kit's scripts (paper repo); the VSIBench
# chart is scripts/make_vsib_category_bars.py in this repo.
set -e
SITE="$(cd "$(dirname "$0")/.." && pwd)"
KIT=/home/jjyeung/agent-project-paper/figure_kit/poster_eccv
export CHART_GT_MARK="†" CHART_OUT_DIR="$SITE/static/images" POSTER_BENCH_H=6.49 POSTER_CAT_H=5.0
# The site prints the corrected ground-truth cells; the poster keeps its own printed numbers.
export CHART_SCORES_OVERRIDE='{"SPLIT + GT": {"VSIBench": 91.8, "VSTIBench": 95.7}}'
export CHART_CATS_OVERRIDE='{"SPLIT_GT": [87.8, 97.6, 98.0, 98.0, 97.3]}'
(cd "$KIT" && python make_benchmark_bars.py && python make_category_bars.py)
rm -f "$SITE/static/images/benchmark_bars.pdf" "$SITE/static/images/vsti_category_bars.pdf"
python "$SITE/scripts/make_site_category_bars.py" vsib revsi
