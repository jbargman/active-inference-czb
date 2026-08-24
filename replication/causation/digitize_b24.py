"""
Digitize the two input distributions of Bärgman et al. (2024, TRF 104) from the
published figures, since the underlying SHRP2 data are not shareable:

  Fig. 1 (p. 377): off-road glance duration PDF, 0.1 s bins, SHRP2 baseline series
                   (the red histogram; the Kungälv series is extracted as well).
                   The figure is vector art, so bar geometry is exact: the PDF's
                   flattened transparency draws pure red where SHRP2 exceeds the
                   Kungälv bar, orange for the overlap (from the baseline), and
                   yellow where Kungälv exceeds SHRP2.
  Fig. 3 (p. 379): maximum-deceleration histogram, 45 SHRP2 crashes, 1.5 m/s² bins.
                   Raster image; digitized from pixels and forced to integer counts,
                   which must sum to 45 (the paper's n) or the script fails.

Calibration of Fig. 1 is done by two independent routes, per the project's
two-routes discipline:
  (a) geometry: the y positions of the tick labels 0 / 0.04 / 0.08 / 0.12 (drawn
      as filled glyph paths, clustered by height);
  (b) normalization: the drawn bars must sum to 1, because the figure plots the
      distribution CONDITIONAL on an off-road glance — the on-road point mass
      (0.80, the broken-axis top tick; caption: the CDF "would start at that
      value") is excluded from the drawn bars.
The script reports both scales and fails if they disagree by more than 5%. The
output CSVs recombine the two: probability 0.80 at duration 0 (on-road) and
0.20 x the conditional bin probabilities for the off-road bins.

Outputs (replication/causation/data/):
  b24_fig1_glances_shrp2.csv    duration_s, probability  (0.1 s bins + on-road mass at 0)
  b24_fig1_glances_kungalv.csv  same, Kungälv baseline
  b24_fig3_decel.csv            decel_ms2 (bin center), probability (counts / 45)
  digitize_report.txt           diagnostics

    python replication/causation/digitize_b24.py
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

import fitz

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PDF = REPO / "external" / "OtherNonActiveInference" / "1-s2.0-S1369847824000810-main (1).pdf"
OUT = HERE / "data"

RED = (0.867, 0.22, 0.318)
ORANGE = (0.796, 0.471, 0.169)
YELLOW = (0.863, 0.859, 0.51)
ON_ROAD_SHARE = 0.80          # the broken-axis tick; caption: CDF "would start at that value"

BASELINE_Y = None             # filled in from the bar bottoms


def col(c):
    return tuple(round(x, 3) for x in c) if c else None


def fig1(doc, report):
    page = doc[3]
    # ---- collect bar segments by color -------------------------------------------------
    segs = defaultdict(list)          # color -> list of (x0, y0, x1, y1)
    glyphs = []                        # left-of-axis glyph boxes, for tick label centers
    for d in page.get_drawings():
        r = d["rect"]
        if not (80 < r.x0 < 320 and 480 < r.y0 < 670):
            continue
        f = col(d.get("fill"))
        if f in (RED, ORANGE, YELLOW):
            if r.x1 - r.x0 > 6 and r.y1 - r.y0 > 6 and len(d["items"]) == 1:
                continue                                          # legend patch
            if f == YELLOW and len(d["items"]) > 1:
                # polygon covering 1-2 bins: split by vertex x
                pts = [p for it in d["items"] for p in it[1:] if hasattr(p, "x")]
                xs = sorted({round(p.x, 1) for p in pts})
                for x_lo, x_hi in zip(xs[:-1], xs[1:]):
                    ys = [p.y for p in pts if x_lo - 0.2 <= p.x <= x_hi + 0.2]
                    if ys and x_hi - x_lo > 0.8:
                        segs[f].append((x_lo, min(ys), x_hi, max(ys)))
            else:
                for it in d["items"]:
                    if it[0] == "re":
                        rr = it[1]
                        segs[f].append((rr.x0, rr.y0, rr.x1, rr.y1))
        elif (f == (0.149, 0.149, 0.149) and 100 < r.x0 and r.x1 < 124
              and 540 < r.y0 and r.y1 < 632):
            glyphs.append((r.x0, r.y0, r.x1, r.y1))
        elif d["type"] == "s" and col(d.get("color")) == (0.0, 0.0, 0.0):
            w, h = r.x1 - r.x0, r.y1 - r.y0
            if 1.5 < w < 3 and h < 6 and r.y1 > 620:
                segs["outline"].append((r.x0, r.y0, r.x1, r.y1))   # tail bar outlines

    baseline = max(y1 for c in (RED, ORANGE, YELLOW) for (_, _, _, y1) in segs[c])
    report.append(f"baseline y = {baseline:.2f}")

    # ---- y scale, route (a): tick label glyph clusters ---------------------------------
    glyphs.sort(key=lambda g: g[1])
    clusters, cur = [], [glyphs[0]]
    for g in glyphs[1:]:
        if g[1] - cur[-1][1] < 6:
            cur.append(g)
        else:
            clusters.append(cur); cur = [g]
    clusters.append(cur)
    centers = sorted((np.mean([(g[1] + g[3]) / 2 for g in c]) for c in clusters))
    report.append("tick label center ys: " + ", ".join(f"{c:.2f}" for c in centers))
    # bottom four clusters are 0.12, 0.08, 0.04, 0 (top one is 0.80 beyond the break)
    lin = centers[-4:]                                  # ascending y = 0.12 .. 0
    spac = np.diff(lin)
    if np.ptp(spac) > 1.0:                      # glyph boxes center digits imperfectly
        raise SystemExit(f"tick spacing not uniform: {spac}")
    pts_per_unit_a = float(np.mean(spac)) / 0.04
    # sanity: label '0' center should sit near the baseline
    if abs(lin[-1] - baseline) > 4:
        raise SystemExit(f"bottom tick center {lin[-1]:.1f} far from baseline {baseline:.1f}")

    # ---- assemble bins -----------------------------------------------------------------
    all_x = sorted(x0 for c in (RED, ORANGE, YELLOW) for (x0, _, _, _) in segs[c])
    pitch = 2.1985                                     # pt per 0.1 s bin (bar outlines)
    x_first = min(all_x)
    def bin_of(x):
        return round((x - x_first) / pitch)

    s_top = {}
    k_top = {}
    for (x0, y0, x1, y1) in segs[RED]:
        b = bin_of(x0); s_top[b] = min(s_top.get(b, baseline), y0)
    for (x0, y0, x1, y1) in segs[ORANGE]:
        b = bin_of(x0)
        s_top.setdefault(b, y0); s_top[b] = min(s_top[b], y0) if b not in s_top else s_top[b]
        k_top.setdefault(b, y0)
        # orange top is the smaller series' top; the larger series' top comes from
        # its own color. If red exists in this bin, orange top belongs to Kungälv;
        # if yellow exists, orange top belongs to SHRP2.
    for (x0, y0, x1, y1) in segs[YELLOW]:
        b = bin_of(x0); k_top[b] = min(k_top.get(b, baseline), y0)
    # fix the orange attribution now that red/yellow are known
    red_bins = {bin_of(x0) for (x0, _, _, _) in segs[RED]}
    yellow_bins = {bin_of(x0) for (x0, _, _, _) in segs[YELLOW]}
    for (x0, y0, x1, y1) in segs[ORANGE]:
        b = bin_of(x0)
        if b in red_bins and b not in yellow_bins:
            k_top[b] = y0                              # red taller: orange top = Kungälv
        elif b in yellow_bins and b not in red_bins:
            s_top[b] = y0                              # yellow taller: orange top = SHRP2
        else:                                          # equal-height or lone overlap
            s_top[b] = min(s_top.get(b, y0), y0); k_top[b] = min(k_top.get(b, y0), y0)
    for (x0, y0, x1, y1) in segs["outline"]:           # tail bars drawn only as outlines
        b = bin_of(x0)
        if b not in s_top and baseline - y0 > 0.05:
            s_top[b] = y0

    def series(tops):
        n = max(tops) + 1
        h = np.zeros(n)
        for b, y in tops.items():
            h[b] = baseline - y
        return h

    h_s, h_k = series(s_top), series(k_top)

    # ---- y scale, route (b): normalization (drawn PDF is conditional on off-road) ------
    pts_per_unit_b = float(h_s.sum() / 1.0)
    report.append(f"pts per unit: geometry {pts_per_unit_a:.1f}, "
                  f"normalization {pts_per_unit_b:.1f}")
    if abs(pts_per_unit_a - pts_per_unit_b) / pts_per_unit_a > 0.05:
        dbg = ", ".join(f"{b}:{h:.1f}" for b, h in enumerate(h_s) if h)
        raise SystemExit("calibration routes disagree by more than 5%\n"
                         f"h_s sum {h_s.sum():.1f} pt over {int((h_s > 0).sum())} bins; "
                         f"geometry says mass {h_s.sum() / pts_per_unit_a:.4f}\n"
                         f"per-bin pt: {dbg}")
    scale = pts_per_unit_b                              # exact normalization by construction

    # first drawn bar: which duration bin? x tick calibration via the axis frame is
    # brittle; instead use the pitch and the outline evidence that bins start at 0.1 s
    # (there is no bar in [0, 0.1) — the point mass sits at zero).
    durations = 0.05 + 0.1 * np.arange(1, len(h_s) + 1)   # centers of [0.1,0.2), ...
    off = 1.0 - ON_ROAD_SHARE
    rows_s = [(0.0, ON_ROAD_SHARE)] + [(round(t, 2), round(off * v / scale, 6))
                                       for t, v in zip(durations, h_s)]
    scale_k = float(h_k.sum())                            # Kungälv conditional, same logic
    rows_k = [(0.0, ON_ROAD_SHARE)] + [(round(t, 2), round(off * v / scale_k, 6))
                                       for t, v in zip(durations, h_k)]
    report.append(f"SHRP2: {int((h_s > 0).sum())} nonzero bins, longest drawn bin "
                  f"{durations[np.nonzero(h_s)[0][-1]]:.2f} s, conditional mass drawn "
                  f"{h_s.sum() / scale:.4f} (geometry route: {h_s.sum() / pts_per_unit_a:.4f})")
    report.append("Kungälv: conditional distribution extracted; on-road share set to the "
                  "same 0.80 (caption: point masses 'very similar')")
    return rows_s, rows_k


def fig3(doc, report):
    page = doc[5]
    pix = page.get_pixmap(dpi=300, clip=fitz.Rect(150, 60, 420, 240))
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    blue = (a[:, :, 2] > 120) & (a[:, :, 0] < 100) & (a[:, :, 1] < 130)
    cols = blue.any(axis=0)
    # bar column groups
    idx = np.nonzero(cols)[0]
    groups, start = [], idx[0]
    for i, j in zip(idx[:-1], idx[1:]):
        if j - i > 3:
            groups.append((start, i)); start = j
    groups.append((start, idx[-1]))
    heights = []
    for (c0, c1) in groups:
        col_h = blue[:, c0:c1 + 1].sum(axis=0)
        heights.append(np.median(col_h))
    heights = np.array(heights, dtype=float)
    counts = np.round(heights / heights.max() * 12).astype(int)   # tallest bar = 12
    report.append(f"fig3 pixel heights {heights.round(1).tolist()} -> counts {counts.tolist()}")
    if counts.sum() != 45:
        raise SystemExit(f"fig3 counts sum to {counts.sum()}, expected 45")
    edges = 3.0 + 1.5 * np.arange(len(counts) + 1)
    centers = (edges[:-1] + edges[1:]) / 2
    return [(float(c), int(n), round(n / 45, 6)) for c, n in zip(centers, counts)]


def main():
    OUT.mkdir(exist_ok=True)
    report = []
    doc = fitz.open(str(PDF))
    rows_s, rows_k = fig1(doc, report)
    rows_d = fig3(doc, report)
    with open(OUT / "b24_fig1_glances_shrp2.csv", "w") as f:
        f.write("duration_s,probability\n")
        f.writelines(f"{t},{p}\n" for t, p in rows_s)
    with open(OUT / "b24_fig1_glances_kungalv.csv", "w") as f:
        f.write("duration_s,probability\n")
        f.writelines(f"{t},{p}\n" for t, p in rows_k)
    with open(OUT / "b24_fig3_decel.csv", "w") as f:
        f.write("decel_ms2,count,probability\n")
        f.writelines(f"{c},{n},{p}\n" for c, n, p in rows_d)
    (OUT / "digitize_report.txt").write_text(
        "Digitized from Bärgman et al. (2024) Figs. 1 and 3 by "
        "replication/causation/digitize_b24.py\n" + "\n".join(report) + "\n",
        encoding="utf-8")
    print("\n".join(report))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
