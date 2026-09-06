# split-spatial.github.io

The project page for SPLIT, a training-free harness that reconstructs one metric 3-D point cloud
from a video and gives a planner VLM tools to query it. The page presents the abstract, the
contributions, a sample question, the pipeline, a walkthrough of one question, the
cross-benchmark results table, two result charts, and the BibTeX entry. It also serves the paper
and the poster.

The site is plain static HTML built on the [Nerfies](https://github.com/nerfies/nerfies.github.io)
template. GitHub Pages serves `index.html` from the repository root; no build step runs on push.

## Layout

```
index.html               the whole page
static/css/              Bulma, Font Awesome, and index.css (Nerfies rules plus a SPLIT block)
static/js/               Font Awesome
static/images/           figures, result charts, and the video poster frame
static/videos/teaser.mp4 the teaser video
static/paper.pdf         the paper
static/poster.pdf        the poster
```

## Previewing locally

```
cd <repo>
python -m http.server 8765 --bind 127.0.0.1
```

Then open <http://127.0.0.1:8765/>.

## Rebuilding the assets

`ASSETS.md` lists every file under `static/` with its source path in the paper repository at
`/home/jjyeung/agent-project-paper` and the exact command that produced it. Rebuilding one asset
means rerunning that row's command. Three cases need more than a copy:

1. **The teaser video.** Re-encode the source with libx264 at crf 26 and `+faststart`. Aim for 6
   to 10 MB at 1080p and adjust crf between 24 and 30 if the output falls outside that range.
2. **The figures.** Rasterize page 1 of the source PDF at 300 dpi with PyMuPDF, then trim the
   white margins with PIL and keep 12 px of padding. `ASSETS.md` carries the function.
3. **The sample question.** Delete the panel (b) shapes from the teaser deck with python-pptx,
   render the deck to PDF through LibreOffice, then apply the same trim.

Two charts, `static/images/benchmark_bars.png` and `static/images/vsti_category_bars.png`, are
placeholders. Newer renders replace them under the same names.

## Resetting the published history

Publishing this page rewrites history to a single commit, which keeps large binary revisions out
of the repository. From a clean working tree on `main`:

```
git checkout --orphan fresh
git add -A
git commit -m "site"
git branch -D main
git branch -m main
git push -f origin main
```

The force push discards every earlier commit on the remote, so run it only when you intend to
replace the published history.
