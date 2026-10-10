# Chapter 2 — Math Foundations: Interactive Jupyter Workbooks

**FSI · Machine Learning Foundations for AI Safety (MLFAS)**  
**For:** absolute beginners · **Recommended time:** roughly 4–5 hours including experiments.

## Open the complete workbook

**[`00-chapter-02-complete-workbook.ipynb`](00-chapter-02-complete-workbook.ipynb)** is the complete chapter, in one notebook. It contains explanations, accurately gridded illustrations, live code cells, and exercises **on the same page**. It also includes the short documentation appendix.

### Or follow individual lessons (easier for a learning website)

| Order | Workbook | Main concepts | Illustrations |
|---:|:--|:--|---:|
| 1 | [Data manipulation & tensors](01-data-manipulation-and-tensors.ipynb) | shapes, indexing, broadcasting | 5 |
| 2 | [Data preprocessing](02-data-preprocessing.ipynb) | missing values, features, one-hot encoding, scaling | 4 |
| 3 | [Linear algebra](03-linear-algebra.ipynb) | weighted sums, matrix multiplication, reductions, norms | 4 |
| 4 | [Calculus & autograd](04-calculus-and-autograd.ipynb) | derivatives, chain rule, backpropagation, weight update | 4 |
| 5 | [Probability & statistics](05-probability-and-statistics.ipynb) | fair coin, observed frequency, conditional probability, mean & spread | 3 |
| Appendix | [PyTorch documentation reference](06-pytorch-documentation-reference.ipynb) | finding help & quick vocabulary | — |
| Quiz | [Chapter checkpoint](quizzes/chapter-02-checkpoint.ipynb) | 20 concept checks + practice cells | — |

**Every one of the 20 diagrams is exported as both native vector SVG and high-resolution PNG.** The notebooks prefer SVG using a `<picture>` element and use PNG as the compatibility fallback. Tables use real rectangular row-and-column grids, labeled headers, and one value per cell. The lesson notebooks also use actual `pandas.DataFrame` displays when the table should be manipulated in code. Image files remain editable by rebuilding from `scripts/build_chapter2_jupyter.py` (script supplied separately in the ZIP).

## GitHub folder convention

```text
mlfas/
└── chapter-02-math-foundations/
    ├── 00-chapter-02-complete-workbook.ipynb
    ├── 01-data-manipulation-and-tensors.ipynb
    ├── 02-data-preprocessing.ipynb
    ├── 03-linear-algebra.ipynb
    ├── 04-calculus-and-autograd.ipynb
    ├── 05-probability-and-statistics.ipynb
    ├── 06-pytorch-documentation-reference.ipynb
    ├── images/                      # 20 SVG diagrams + 20 matching PNG fallbacks
    ├── quizzes/
    │   ├── chapter-02-checkpoint.ipynb
    │   └── instructor-answer-key.md
    ├── chapter.json
    ├── requirements.txt
    └── README.md
```

The lessons are **not** separate `.md` files anymore. Their teaching text is in **Markdown cells inside `.ipynb`**, next to diagrams and executable code. Chapter 1 and Chapters 3–6 are not bundled here.

## How learners use it

1. Install Python (3.10+) and JupyterLab, or open the notebooks in a Jupyter-compatible environment.
2. From this chapter folder: `pip install -r requirements.txt`, then `jupyter lab`.
3. Open **the complete workbook** *or* one numbered notebook. Read text and predict outputs before using **Run**.
4. No internet connection, GPU, D2L package, or downloadable training data is needed **after dependencies are installed**.
5. When the lessons are done, complete the checkpoint notebook.

**GitHub display vs. execution:** GitHub can *render* the saved notebook content and static SVG diagrams (or PNG fallback); running code requires a Jupyter kernel (locally or via a hosted notebook runtime). A website can render the `.ipynb` Markdown/cells and link to a notebook runtime for experiments. GitHub alone is not a code-execution backend.


## Illustration strategy — SVG first, PNG fallback

- Both `images/<name>.svg` and `images/<name>.png` are generated from the **same source drawing** by `scripts/build_chapter2_jupyter.py` (and the extra expansion diagram by `scripts/apply_teaching_revision.py`). Never manually substitute a low-quality PNG inside an `.svg` wrapper.
- Every lesson notebook uses standard HTML `<picture>` with an SVG `<source>` and a PNG `<img>` fallback; it includes descriptive alternate text and a caption. The complete workbook uses the same assets.
- Browser support for `<picture>` with SVG is excellent; notebook renderers may differ. Verify in the **actual** Jupyter/GitHub/website renderer before shipping. For website runtime failures (e.g., SVG network error), the frontend should explicitly change `img.src` to the PNG URL on error; HTML `<picture>` alone does not guarantee a fallback when the SVG request fails.
- For **datasets**, the interactive Pandas or Markdown table is the source of truth. Diagrammatic tables supplement it, with complete column headers, row labels, visible cell borders and a value in every data cell.
- A reproducibility check script at `scripts/validate_assets.py` verifies pairs, true vector SVGs, notebook paths, and the presence of SVG-first references.
- To regenerate locally, install the visualization dependencies and run `python scripts/build_chapter2_jupyter.py` followed by `python scripts/apply_teaching_revision.py`. The second command reapplies the expanded lessons and 20th diagram.

## Instructional design

Each lesson proceeds **explain → fully labeled diagram → annotated computation → runnable code → experiment → check understanding**. The examples are intentionally synthetic and mathematically small. The same four learners appear through tensor creation, preprocessing, matrix prediction, and simple probability. A one-weight toy example bridges algebra and backpropagation.

**Scope adapted from the seven attached Dive into Deep Learning notebooks:** `ndarray.ipynb`, `pandas.ipynb`, `linear-algebra.ipynb`, `calculus.ipynb`, `autograd.ipynb`, `probability.ipynb`, `lookup-api.ipynb`. The source notebooks informed *what to teach*; the prose, examples, questions, and diagram assets in this rebuild were newly authored.

Original learning reference: [Dive into Deep Learning — Chapter 2 (Preliminaries)](https://d2l.ai/chapter_preliminaries/index.html).


## Teaching revision — explanation-first edition

The notebook lessons now explicitly answer **what a concept means, why it matters, how it works step by step, and where it is used in machine learning**. Broadcasting includes its formal compatibility rule, a fully labeled conceptual-expansion SVG, matched PNG fallback, a worked example, and an invalid-shape example. Further bridges cover missing-value imputation and leakage; matrix calculations; gradients, chain rule and parameter updates; and probability versus observed frequency.

All lesson images are **SVG-first with PNG fallback**. True datasets shown in code are presented using Pandas/Markdown tables rather than pretending screenshots are data sources.

To reproduce the exact edition from the original lesson builder, from this chapter directory run:

```bash
python scripts/build_chapter2_jupyter.py
python scripts/apply_teaching_revision.py
```

The second script regenerates the new SVG/PNG companion and all concept-bridge cells. It is safe to rerun once this edition is present. It does not change source D2L files.
