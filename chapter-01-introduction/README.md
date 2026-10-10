# MLFAS — Chapter 01: Introduction to Machine Learning

**Audience:** Absolute beginners  
**Format:** Three illustrated Jupyter Notebooks (`.ipynb`), one optional coding notebook, SVG diagrams and JSON practice quizzes.  
**Suggested pace:** 15–25 minutes per lesson, plus optional hands-on experiment.  
**Teaching thread:** One spam-email example connects all three lessons.

## Lessons

1. [What Is Machine Learning?](01-what-is-machine-learning.ipynb) — traditional programming, labeled data, features, models, training versus inference and kinds of predictions.
2. [How Machines Learn](02-how-machines-learn.ipynb) — data, model, loss, optimization, supervised/self-supervised/reinforcement learning, and deep neural networks.
3. [When Machine Learning Goes Wrong](03-when-ml-goes-wrong.ipynb) — generalization, overfitting, shortcuts, distribution shift, objective mismatch, prompt injection and technical AI safety.

**Optional lab:** [Build a tiny spam detector](notebooks/first-ml-model.ipynb), using `scikit-learn`. This is a toy demonstration, not a production spam filter.

## Diagrams, quizzes and assets

- All diagrams are original/local **SVG vector graphics** in `images/`; each lesson refers to them with notebook-relative links `images/file.svg`.
- Each lesson ends with a brief *stop and check*. A separate `quizzes/lesson-XX.json` contains four practice questions and explanations.
- `chapter.json` is the course-platform manifest. It now points to the `.ipynb` lessons.
- The three main lessons contain very small, **optional** Python cells; the material can also be read without running Python.

## Publishing as Jupyter Book

This folder is **not an independent Jupyter Book project**. Keep **one** book configuration and table of contents at the overall `mlfas/` (or your repository's chosen) root, combining Chapter 1 and Chapter 2. Include these three notebook paths in that overall table of contents. Jupyter Book can present Markdown and executable notebooks together.

To build your own learning website, import notebook Markdown cells for explanations, render images with their chapter-relative paths, and handle code cells as read-only snippets unless an interactive execution environment is specifically provided. Keep assessment records in your platform database, not GitHub. The quiz JSON contains visible answer keys and is suited to practice, not sealed grading.

## Quality and safety notes

- All lessons can be read without knowing Python, calculus or linear algebra.
- Illustrative diagrams are conceptual and not results of actual ML experiments.
- The optional lab depends on `scikit-learn`, and the core lesson code cells use only the Python standard library.
- Avoid executing untrusted notebook code automatically on a public server.

## Attribution

The structure and underlying introductory subject matter are informed by [*Dive into Deep Learning*, Introduction](https://d2l.ai/chapter_introduction/index.html). The lesson prose and locally included diagrams are independently authored for FSI. Consult the D2L license if you later copy their text or images.
