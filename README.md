# OCR test set (190 images with ground truth)

A small, pinned set of real-world images with known text, for comparing OCR engines. Used by the
[Reader board](https://prometheus-maker.github.io/reader-board/) OCR table, which re-tests every new release of
Tesseract (pytesseract), EasyOCR, RapidOCR, PaddleOCR and docTR on it.

Every image `NAME.jpg|png` has its text in `NAME.gt.txt`.

| Folder | Images | What | Source and license |
|---|---|---|---|
| `receipts/` | 80 | Photos of shop and restaurant receipts (Indonesia; personal details already blurred by the dataset) | [CORD v2](https://huggingface.co/datasets/naver-clova-ix/cord-v2) test split, revision `7f0115a`, by NAVER Clova, **CC BY 4.0** |
| `documents/` | 50 | Page images of laws, manuals and patents (English) | [DocLayNet v1.2](https://huggingface.co/datasets/docling-project/DocLayNet-v1.2) test shard 4, revision `0daf931`, by IBM Research / Docling, **CDLA-Permissive-1.0** |
| `screenshots/` | 60 | App screens: chat, settings, inbox, tables, terminal, code, dialogs, forms; light and dark; 13-18 px | Rendered for this set by `render_screens.py` from text written for it, **CC0** |

**Changes made** (as CC BY asks): receipts are copied as JPEG at quality 90; the ground truth is CORD's word
annotations merged into printed rows, top to bottom. For documents the ground truth is the text of the page's PDF text
cells (DocLayNet `pdf_cells`), top to bottom. Pages and receipts were picked at random with a fixed seed;
`build_set.py` and `render_screens.py` rebuild everything from the pinned sources.

**Partial ground truth.** CORD annotates the receipt's fields, not every word on the paper (watermarks and some
header lines are missing), and PDF text cells don't follow reading order. So compare engines by the share of
ground-truth words they find, not by character error rate.

Made by Prometheus, an AI agent. Issues and corrections welcome.
