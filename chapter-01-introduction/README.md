# MLFAS — Chapter 01: Introduction to Machine Learning

**Audience:** absolute beginners  
**Time:** three short lessons of about 15–20 minutes each, plus an optional practical  
**Approach:** one running example (spam email detection), accessible diagrams, short checks, and a gentle bridge to technical AI safety.

## Lessons

1. [What Is Machine Learning?](./01-what-is-machine-learning.md) — examples, inputs, labels, models, training vs. inference.
2. [How Machines Learn](./02-how-machines-learn.md) — data, loss, optimization, learning methods, deep learning.
3. [When Machine Learning Goes Wrong](./03-when-ml-goes-wrong.md) — generalization, overfitting, distribution shift, safety, alignment, security.

### Optional lab

[First ML Model: Spam Detector](./notebooks/first-ml-model.ipynb) — train and test a small model using Python. The notebook needs `scikit-learn` and works in Jupyter or Google Colab. It is **not** a production spam filter.

### Reusable assets

- `images/*.svg`: original vector diagrams referenced via **relative paths** from lessons.
- `quizzes/lesson-*.json`: 4 practice questions per lesson, with explanations.
- `chapter.json`: ordered manifest for a website content importer.

## Website integration

1. Copy the entire `chapter-01-introduction/` folder into `mlfas/` in your curriculum repository.
2. Parse Markdown front matter for title, slug, chapter order, reading estimate, and prerequisites.
3. Render Markdown and SVG assets. Preserve relative asset paths when deploying.
4. Import `chapter.json` to build chapter navigation, and the quiz JSON files for **ungraded practice**.
5. Prefer a build-time or webhook-triggered content sync instead of fetching every file live from GitHub on each visit.
6. Track student completion and serious quiz results in your application's database. Do **not** treat `correct_option_index` in a public GitHub JSON file as a secure answer key for graded assessments.
7. Serve or link the `.ipynb` file from the site (for example, a link to download or open in Jupyter/Colab). You do not need to execute arbitrary notebook code on your website's server.

## Editorial notes

- Keep each lesson clear enough to read without advanced mathematics or coding.
- More detailed math (probability, calculus, vectors, gradient descent), neural network implementation, transformers, and RL theory belong in later chapters.
- Every diagram has an SVG `<title>` and `<desc>` for accessibility; every Markdown reference has meaningful alt text.
- All quiz examples, diagrams, lesson sequencing, and prose in this starter pack are newly written.

## Attribution and further reading

Conceptual reference: [*Dive into Deep Learning*, Chapter 1 (Introduction)](https://d2l.ai/chapter_introduction/index.html), by Aston Zhang, Zack C. Lipton, Mu Li, and Alex J. Smola. The D2L book is distributed under [CC BY-SA 4.0](https://github.com/d2l-ai/d2l-en). This chapter uses independent explanations and examples rather than reproducing D2L's original chapter. If you later copy or closely adapt D2L prose or illustrations, follow its attribution and ShareAlike requirements.
