"""Rebuild this test set from its pinned sources: python build_set.py RAWDIR OUTDIR

receipts/   80 of the 100 CORD v2 test receipts (CC-BY-4.0), long side scaled to 1600 px, JPEG q90.
            Ground truth: CORD's word annotations, one line per annotated line, lines ordered top to bottom.
documents/  50 DocLayNet v1.2 test pages (CDLA-Permissive-1.0), shard test-00004, split evenly over its document
            categories, English pages with at least 40 words. Ground truth: the text of the page's PDF text cells, top to bottom.
screenshots/ rendered by render_screens.py from text written for this set (CC0).
Random choices use random.Random(0), so the same sources give the same files."""
import io, json, random, re, sys
from pathlib import Path

import pyarrow.parquet as pq
from PIL import Image

RAW, OUT = Path(sys.argv[1]), Path(sys.argv[2])


def save_jpeg(data, dest, long_side=1600):
    im = Image.open(io.BytesIO(data)).convert("RGB")
    s = long_side / max(im.size)
    if s < 1:
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    im.save(dest, "JPEG", quality=90, optimize=True)


def cord():
    t = pq.read_table(RAW / "cord-test.parquet")
    keep = sorted(random.Random(0).sample(range(t.num_rows), 80))
    d = OUT / "receipts"; d.mkdir(parents=True, exist_ok=True)
    for i in keep:
        row = t.slice(i, 1).to_pylist()[0]
        gt = json.loads(row["ground_truth"])
        lines = []
        for ln in gt["valid_line"]:
            words = [w for w in ln["words"] if w["text"].strip()]
            if not words:
                continue
            top = min(min(w["quad"]["y1"], w["quad"]["y2"]) for w in words)
            left = min(min(w["quad"]["x1"], w["quad"]["x4"]) for w in words)
            lines.append((top, left, " ".join(w["text"] for w in sorted(words, key=lambda w: w["quad"]["x1"]))))
        name = f"cord-{i:03d}"
        save_jpeg(row["image"]["bytes"], d / f"{name}.jpg")
        (d / f"{name}.gt.txt").write_text("\n".join(rows_of(lines)) + "\n", encoding="utf-8")


def rows_of(lines, tol=12):
    """CORD annotates fields, not visual rows: '2  60.000' on one printed row are two lines. Merge lines whose tops
    are within tol px into one row, left to right, so the truth reads like the receipt."""
    rows = []
    for top, left, text in sorted(lines):
        if rows and top - rows[-1][0] <= tol:
            rows[-1][1].append((left, text))
        else:
            rows.append((top, [(left, text)]))
    return [" ".join(t for _, t in sorted(r)) for _, r in rows]


EN = {"the", "and", "of", "to", "in", "is", "for", "with", "be", "or", "a", "on", "that", "by"}
DE_FR_ES = {"der", "die", "und", "des", "den", "für", "le", "la", "les", "et", "du", "el", "los", "y", "von", "zu"}


def english(words):
    """The engines run English models: keep pages whose common words are English (some laws pages are German)."""
    en, other = sum(w in EN for w in words), sum(w in DE_FR_ES for w in words)
    return en >= 5 and en > 3 * other


def doclaynet():
    pf = pq.ParquetFile(RAW / "doclaynet-test4.parquet")
    pages = {}
    for b in pf.iter_batches(batch_size=16, columns=["image", "pdf_cells", "metadata"]):
        for row in b.to_pylist():
            cells = [c for el in row["pdf_cells"] for c in el if c["text"].strip()]
            words = re.findall(r"\w+", " ".join(c["text"] for c in cells).lower())
            if len(words) < 40 or not english(words):
                continue
            pages.setdefault(row["metadata"]["doc_category"], []).append(
                (row["metadata"]["page_hash"], row["image"]["bytes"], cells))
    d = OUT / "documents"; d.mkdir(parents=True, exist_ok=True)
    rnd, cats = random.Random(0), sorted(pages)
    for k, cat in enumerate(cats):
        n = 50 // len(cats) + (1 if k < 50 % len(cats) else 0)
        for h, img, cells in rnd.sample(sorted(pages[cat], key=lambda p: p[0]), min(n, len(pages[cat]))):
            name = f"doclaynet-{cat}-{h[:10]}"
            Image.open(io.BytesIO(img)).convert("RGB").save(d / f"{name}.png", optimize=True)
            rows = sorted(cells, key=lambda c: (round(c["bbox"][1] / 4), c["bbox"][0]))
            (d / f"{name}.gt.txt").write_text("\n".join(c["text"] for c in rows) + "\n", encoding="utf-8")


if __name__ == "__main__":
    cord()
    doclaynet()
