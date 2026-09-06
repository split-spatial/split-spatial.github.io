# Static assets: sources and build commands

Every file under `static/` comes from the paper repository at
`/home/jjyeung/agent-project-paper`. This file records the exact source and the command that
produced each one, so any asset can be rebuilt from scratch.

Two helpers appear throughout:

- `FFMPEG` is `python -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())"`.
- The LibreOffice renderer is `/data2/jjyeung/tools/libreoffice/soffice.sh`, run with
  `LO_PROFILE=/data2/jjyeung/tools/libreoffice/profiles/poster_w2`.

Rendered figures share one recipe: PyMuPDF rasterizes page 1 at 300 dpi, then PIL trims the
white margins to the content bounding box and adds 12 px of padding back. The trim first insets
the raster by 3 px so the page-edge antialiasing does not defeat the bounding box.

## Documents

| File | Source | Command |
| --- | --- | --- |
| `static/paper.pdf` | `/home/jjyeung/agent-project-paper/eccv_main.pdf` | `cp` (verified that page 1 carries no release sentence) |
| `static/poster.pdf` | `/home/jjyeung/agent-project-paper/figure_kit/poster_eccv/poster_eccv_v18.pdf` | `cp` |

## Video and poster frame

| File | Source | Command |
| --- | --- | --- |
| `static/videos/teaser.mp4` | `/home/jjyeung/agent-project-paper/figure_kit/vid2_fig3_teaser/fig3_teaser_full_16x9.mp4` | `$FFMPEG -y -i <src> -an -c:v libx264 -preset slow -crf 26 -pix_fmt yuv420p -movflags +faststart static/videos/teaser.mp4` |
| `static/images/teaser_still.jpg` | `/home/jjyeung/agent-project-paper/figure_kit/vid2_fig3_teaser/poster_full.png` | PIL: `Image.open(src).convert("RGB").save(out, "JPEG", quality=88, optimize=True, progressive=True)` |

The re-encode keeps the source geometry and timing: 1920x1080, 30 fps, 73.80 s.

## Figures

| File | Source | Command |
| --- | --- | --- |
| `static/images/sample_question.png` | `/home/jjyeung/agent-project-paper/figure_kit/fig1_teaser/req83_776/variant_d_onerow/fig1_teaser_variant_d_editable_avg_v15.pptx` | python-pptx deletes shape ids 2, 3, 17 and every shape whose left edge is at or beyond 185 mm, and clears the outline on the `white_background` rectangle; then `LO_PROFILE=... soffice.sh --convert-to pdf`, then the 300 dpi render-and-trim recipe |
| `static/images/pipeline.png` | `/home/jjyeung/agent-project-paper/figures/fig_pipeline.pdf` | 300 dpi render-and-trim recipe |
| `static/images/walkthrough.png` | `/home/jjyeung/agent-project-paper/figure_kit/fig1_hero_trace/variant_b_q1851/hero_figure_filled_v16_user_5frames.pdf` | 300 dpi render-and-trim recipe |
| `static/images/benchmark_bars.png` | `/home/jjyeung/agent-project-paper/figure_kit/poster_eccv/assets/benchmark_bars.png` | `cp` (placeholder: a newer render replaces it under the same name) |
| `static/images/vsti_category_bars.png` | `/home/jjyeung/agent-project-paper/figure_kit/poster_eccv/assets/vsti_category_bars.png` | `cp` (placeholder: a newer render replaces it under the same name) |

`sample_question.png` shows panel (a) of the paper teaser figure. Deleting the shapes listed
above removes the panel (b) column and the two panel captions.

## Template files

`index.html`, `static/css/*`, and `static/js/*` start from the Nerfies template at
<https://github.com/nerfies/nerfies.github.io>. The page drops the Nerfies analytics snippet,
navbar, carousel, interpolation viewer, and related-work section. `static/css/index.css` keeps
the Nerfies rules and appends a SPLIT block at the end for the colored section bands, the
results table, and the link color.

## Render-and-trim reference

```python
import fitz
from PIL import Image
import numpy as np

def render_trim(pdf, out, pad=12, dpi=300, inset=3):
    page = fitz.open(pdf)[0]
    pix = page.get_pixmap(dpi=dpi, alpha=False)
    pix.save("raw.png")
    im = Image.open("raw.png").convert("RGB")
    W, H = im.size
    a = np.asarray(im.crop((inset, inset, W - inset, H - inset))).astype(int)
    nz = a.sum(2) < 255 * 3 - 12
    cols, rows = np.where(nz.any(0))[0], np.where(nz.any(1))[0]
    l, t = cols.min() + inset, rows.min() + inset
    r, b = cols.max() + 1 + inset, rows.max() + 1 + inset
    im.crop((max(0, l - pad), max(0, t - pad),
             min(W, r + pad), min(H, b + pad))).save(out, optimize=True)
```
