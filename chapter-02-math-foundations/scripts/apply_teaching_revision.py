"""Upgrade the D2L-based FSI chapter 2 notebooks with step-by-step conceptual bridges.

Re-run after build_chapter2_jupyter.py to regenerate this enhanced edition.
This script is idempotent for the same edition. It does not modify source D2L notebooks.
"""
from pathlib import Path
import re
import nbformat
import cairosvg
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]
NB_FILES=[
 '01-data-manipulation-and-tensors.ipynb',
 '02-data-preprocessing.ipynb',
 '03-linear-algebra.ipynb',
 '04-calculus-and-autograd.ipynb',
 '05-probability-and-statistics.ipynb',
 '06-pytorch-documentation-reference.ipynb',
]

def cmark(body):
    c=nbformat.v4.new_markdown_cell(body.strip()+"\n")
    c.metadata['tags']=['concept-bridge']
    return c

def ccode(body):
    c=nbformat.v4.new_code_cell(body.strip()+"\n")
    c.metadata['tags']=['concept-bridge','practice']
    return c

def insert_before(nb,needle,cells):
    idx=next(i for i,c in enumerate(nb.cells) if needle in c.source)
    nb.cells[idx:idx]=cells

def insert_after(nb,needle,cells):
    idx=next(i for i,c in enumerate(nb.cells) if needle in c.source)
    nb.cells[idx+1:idx+1]=cells

def replace_markdown(nb,needle,text):
    idx=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and needle in c.source)
    nb.cells[idx].source=text.strip()+"\n"

# A. Broadcasting: the original graphic shows inputs/result; this companion shows conceptual expansion.
W,H=1160,370
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="title desc">',
 '<title id="title">Logical expansion used by tensor broadcasting</title>',
 '<desc id="desc">Three 3 row 2 column tables show A logically expanded as rows 1 1, 2 2, 3 3, B as rows 10 20 repeated, and the sum as rows 11 21, 12 22, 13 23. All cells and row and column labels are visible.</desc>',
 '<rect width="1160" height="370" rx="16" fill="#f8fafc"/>',
 '<text x="34" y="40" font-family="DejaVu Sans,Arial,sans-serif" font-size="25" font-weight="700" fill="#142941">Broadcasting: what PyTorch treats the inputs as</text>',
 '<text x="34" y="68" font-family="DejaVu Sans,Arial,sans-serif" font-size="17" fill="#475569">The repeated entries are logical; PyTorch need not make new copies in memory.</text>']

def label(x,y,content,size=18,color='#19334b',weight=400,anchor='start'):
    parts.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans,Arial,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(str(content))}</text>')
def grid(x,y,rows,kind):
    cols=len(rows[0]);cw=69;ch=49
    label(x+cols*cw/2,y-34,{'a':'A (3, 1) → (3, 2)','b':'B (1, 2) → (3, 2)','r':'Result (3, 2)'}[kind],21,'#142941',700,'middle')
    for j in range(cols):label(x+j*cw+cw/2,y-13,f'col {j}',13,'#475569',400,'middle')
    for i,row in enumerate(rows):
        label(x-11,y+i*ch+ch*.6,f'row {i}',13,'#475569',400,'end')
        for j,val in enumerate(row):
            palette={'a':('#e2f5ef','#bde6d9','#0e6651'),'b':('#e6effd','#cce0fc','#214b89'),'r':('#cdf6e9','#b8f0dd','#075c43')}[kind]
            fill=palette[1] if (kind=='a' and j==1) or (kind=='b' and i>0) else palette[0]
            parts.append(f'<rect x="{x+j*cw}" y="{y+i*ch}" width="{cw}" height="{ch}" fill="{fill}" stroke="{palette[2]}" stroke-width="1.5"/>')
            label(x+j*cw+cw/2,y+i*ch+ch*.62,val,20,palette[2],700,'middle')
    label(x+cols*cw/2,y+len(rows)*ch+30,'Shaded cells = logically reused values' if kind!='r' else 'Each cell adds values at the same position',13,'#475569',400,'middle')

grid(100,150,[[1,1],[2,2],[3,3]],'a')
label(358,242,'+',40,'#0f766e',700,'middle')
grid(457,150,[[10,20],[10,20],[10,20]],'b')
label(716,242,'=',40,'#0f766e',700,'middle')
grid(814,150,[[11,21],[12,22],[13,23]],'r')
parts.append('</svg>')
svg='\n'.join(parts)
img=ROOT/'images'/'04b-broadcasting-expanded.svg';img.write_text(svg,encoding='utf8')
cairosvg.svg2png(bytestring=svg.encode('utf8'),write_to=str(img.with_suffix('.png')),output_width=1740,output_height=555)

nbs={name:nbformat.read(ROOT/name,as_version=4) for name in NB_FILES}

# 2.1
nb=nbs[NB_FILES[0]]
if not any('concept-bridge' in c.metadata.get('tags',[]) for c in nb.cells):
    insert_after(nb,'## 2. What is a tensor?',[
        cmark('''### Why do we use tensors instead of separate numbers?\n\nA model usually receives *many examples and many measurements at once*. A tensor stores those values in one organized object so an operation can be applied to an entire group. **Shape describes the arrangement, not the meaning of the values.**\n\nFor our dataset, `(4, 3)` means four learners × three numerical measurements. `shape[0] = 4` counts learners, while `shape[1] = 3` counts measurements per learner. A scalar has zero axes, a vector one, and a matrix two. Larger tensors follow the same idea: a batch of images might have shape `(batch, channels, height, width)`.\n\n**Machine-learning connection:** if your model expects three features per example, providing a tensor with four columns will cause a shape mismatch—even if every number looks reasonable.''')
    ])
    replace_markdown(nb,'## 4. Operations: elementwise vs. broadcasting','''## 4. Operations: elementwise vs. broadcasting\n\n### First: what does *elementwise* mean?\n\nWith equally shaped tensors, `+` combines **corresponding positions**: `[1, 2] + [10, 20]` becomes `[11, 22]`. Similarly, `*` multiplies positions: `[1, 2] * [10, 20]` becomes `[10, 40]`. No rows or columns are matched by meaning or by name: PyTorch matches their **positions**.\n\n### Broadcasting — precise definition\n\n**Broadcasting is a set of rules that lets PyTorch perform elementwise operations on tensors of different but compatible shapes by treating dimensions of size 1 as expanded to the required size.**\n\n**Why does it exist?** Suppose you have a column containing three students' values and a row containing two adjustments. You want every student to receive both adjustments. You could build two larger tables by hand, but that is tedious and may waste memory. Broadcasting lets you express the same calculation directly.\n\n**Important:** 'expand' means *behave as if values repeat*, not necessarily that PyTorch physically copied the tensor's data. Now follow the original calculation below, and then the expanded view after it.''')
    insert_after(nb,'*Figure: A complete 3 × 1 plus 1 × 2 broadcasting calculation with a full 3 × 2 result table.*',[
        cmark('''### How the `(3, 1) + (1, 2)` addition works\n\n**Step 1 — read the shapes.** `A = [[1], [2], [3]]` has **3 rows and 1 column**. `B = [[10, 20]]` has **1 row and 2 columns**.\n\n**Step 2 — imagine expanding only the size-1 dimensions.** A's single column is logically repeated into two columns. B's single row is logically repeated into three rows. Their conceptual views are:\n\n| Row | A column 0 | A column 1 | B column 0 | B column 1 |\n|:--|--:|--:|--:|--:|\n| 0 | 1 | 1 | 10 | 20 |\n| 1 | 2 | 2 | 10 | 20 |\n| 2 | 3 | 3 | 10 | 20 |\n\n**Step 3 — add corresponding positions:** top-right `1+20=21`, middle-left `2+10=12`, bottom-right `3+20=23`. The complete output is `[[11,21],[12,22],[13,23]]`, shape `(3,2)`.\n\nHere is the same expansion as fully labeled 3-row × 2-column grids:'''),
        cmark('''<picture>\n  <source type="image/svg+xml" srcset="images/04b-broadcasting-expanded.svg">\n  <img src="images/04b-broadcasting-expanded.png" alt="Three complete three-row two-column grids: A expands horizontally, B expands vertically, and their elementwise sum is shown cell by cell." loading="lazy">\n</picture>\n\n*Figure: Conceptual broadcasting expansion. Colored cells show reused values; no physical copies are required.*''')
    ])
    replace_markdown(nb,'**Important distinction:** Broadcasting', '''### When are shapes compatible? Check dimensions from right to left\n\nPyTorch lines up the **last axes first**. Each aligned pair must have the **same size**, or **one size must be 1**, or a leading axis must be absent (treated as 1 for comparison). The result takes the larger size along each axis. If a pair has two different sizes, neither of which is 1, broadcasting fails.\n\n| A shape | B shape | Does it work? | Result and reasoning |\n|:--|:--|:--|:--|\n| `(3, 1)` | `(1, 2)` | Yes | `(3, 2)` — each axis has a 1 |\n| `(3, 2)` | `(3, 2)` | Yes | `(3, 2)` — both axes match |\n| `(3, 2)` | `(2,)` | Yes | `(3, 2)` — the vector acts like `(1, 2)` |\n| `(3, 2)` | `(3, 3)` | **No** | Last axis: 2 versus 3; neither is 1 |\n| `(3, 1, 4)` | `(1, 5, 1)` | Yes | `(3, 5, 4)` — check axes from the right |\n\n**Do not confuse operations:** `A * B` is elementwise multiplication, optionally with broadcasting. `A @ B` is *matrix multiplication*, which uses row–column dot products and its own shape rules (Lesson 2.3).\n\n### Where broadcasting appears in machine learning\n\nSuppose `scores` contains 1,000 learners × 3 subject scores, so it has shape `(1000, 3)`. Suppose `subject_means` contains the three averages, shape `(3,)`. `scores - subject_means` subtracts the relevant subject average from **each learner's row**, without manually creating 1,000 copies of the averages. This pattern is common in feature centering and neural-network bias addition.\n\n**Check the intuition:** Broadcasting changes *how the computation pairs values*. It does **not** invent new observations or determine what the data means.''')
    insert_after(nb,'result = A + B',[
       cmark('''### Try a compatible shape, then see a shape error\n\nIn the cell below we use tiny stand-in values rather than 1,000 learners. Predict the output shape before running. A failed example is caught and reported so it does not stop the notebook.'''),
       ccode('''subject_scores = torch.tensor([[60., 70., 80.], [75., 85., 95.]])  # 2 learners × 3 subjects\nsubject_means = torch.tensor([67.5, 77.5, 87.5])           # 3 subject averages\ncentered = subject_scores - subject_means\nprint('Scores shape:', tuple(subject_scores.shape))\nprint('Means shape:', tuple(subject_means.shape))\nprint('Centered result:\\n', centered)\nassert centered.shape == (2, 3)\n\ntry:\n    _ = torch.zeros(3, 2) + torch.zeros(3, 3)\nexcept RuntimeError:\n    print('Expected: shapes (3,2) and (3,3) cannot broadcast.')''')
    ])
    insert_before(nb,'### Check your understanding (answer before revealing by running)',[
        cmark('''### Explain broadcasting in your own words\n\nTry this four-part explanation aloud: **What** does broadcasting allow? **Why** is it useful? **How** are dimensions compared? **Where** does it appear in machine learning? If you can explain all four using `(3,1) + (1,2)`, you understand the rule rather than memorizing the diagram.''')
    ])

# 2.2
nb=nbs[NB_FILES[1]]
if not any('concept-bridge' in c.metadata.get('tags',[]) for c in nb.cells):
    insert_after(nb,'## 1. Why cleaning comes before modeling',[
        cmark('''### What are we trying to achieve?\n\n**Data preprocessing** means turning raw observations into a trustworthy, consistent form the model can use. We do it because raw data may contain unknown values, inconsistent units, text labels, or columns that should *not* be used to predict the answer.\n\n**How it works:** (1) inspect the table, (2) decide how missing values will be handled, (3) separate inputs from the answer, (4) encode categories, and (5) optionally scale numeric features. **ML connection:** a model can learn misleading patterns if preprocessing accidentally uses information from the future or test set.''')
    ])
    insert_before(nb,'<picture>\n  <source type="image/svg+xml" srcset="images/06-missing-values.svg">',[
        cmark('''### Why choose the mean here, and what could go wrong?\n\nFor known counts `2, 6, 8`, the mean is `(2 + 6 + 8) / 3 = 5.33`. Replacing a missing cell with this value is called **mean imputation**. It lets a numerical algorithm accept a complete column, but it introduces an estimated value and may hide differences among learners.\n\n- **Unknown ≠ zero:** zero asserts no practice occurred; missing means the count was unreported.\n- **Imputation ≠ recovery:** we have *not* discovered Ben's actual count.\n- **Mean ≠ always best:** a median may be more robust to extreme values, and sometimes keeping a separate "was missing" flag is useful.\n\nIn real evaluation, compute the fill value on the training portion only. If a test example helps determine the fill value, information from evaluation has leaked into training.''')
    ])
    insert_before(nb,'## 4. Turning categories into numbers',[
        cmark('''### Features versus targets: what can the model see?\n\nA **feature** is a measurement available to the model as an input. A **target** is the answer we ask it to predict. In our toy task, study hours, practice count, and study method are input features; Score is the target.\n\nWhy keep the target out of the inputs? If we hand a model the correct score while asking it to predict that same score, its excellent apparent performance would be meaningless. This is an obvious case of **target leakage**. Other leakage can be subtler, such as using information collected *after* the outcome.''')
    ])
    insert_after(nb,'**One-hot encoding** makes a separate column for each category.',[
        cmark('''### Read each encoded row, not just the column names\n\nWith category columns `Method_Text` and `Method_Video`, a learner marked "Text" has `(1, 0)` and a learner marked "Video" has `(0, 1)` (the order depends on the actual column names). A **1 means the category applies** and **0 means it does not**. We do not interpret the two columns as quantities that should be added or ordered.\n\n**Why this matters:** many models work with numbers but should not be told that Video is "greater than" Text just because we assigned arbitrary numeric labels. Other encoding schemes exist; one-hot is a clear starting point.''')
    ])
    insert_before(nb,'## 7. Practice: explain every column',[
        cmark('''### Scaling worked example\n\n**What:** Scaling changes the numerical range of a feature while preserving which rows the values belong to. **Why:** wildly different magnitudes can complicate some optimization procedures. **How:** for min–max scaling, use `(value − minimum) / (maximum − minimum)` when the range is nonzero. For Hours `[1,2,3,4]`, the value 3 becomes `(3−1)/(4−1) = 2/3 ≈ 0.667`.\n\n**A key boundary:** if maximum equals minimum, the denominator is zero, so we must handle that case separately. Also, fitted minimum and maximum must come from **training data**, not from held-out evaluation examples. Scaling is a representation choice, not a guarantee of better predictions.''')
    ])

# 2.3
nb=nbs[NB_FILES[2]]
if not any('concept-bridge' in c.metadata.get('tags',[]) for c in nb.cells):
    insert_after(nb,'## 2. The dot product: one weighted sum',[
        cmark('''### Why multiplication *and* addition?\n\nA model may consider several pieces of information, each with a different importance or **weight**. The dot product gives one combined value: multiply each feature by its corresponding weight, then add those contributions.\n\nFor `[2,4] · [3,1]`: feature 1 contributes `2×3=6`, feature 2 contributes `4×1=4`, and the sum is **10**. The answer is a single scalar, not `[6,4]`.\n\n**ML connection:** a single neuron begins with a weighted sum like this (often plus a bias), before applying its activation function. The weights are learned, not measures of a feature's inherent worth.''')
    ])
    insert_after(nb,'**Shape rule:** `(4, 2) @ (2, 1) → (4, 1)`',[
        cmark('''### Read matrix multiplication one row at a time\n\nThe first row of `X` is `[1,1]`. Dot it with weights `[2,1]` to obtain `1×2 + 1×1 = 3`. The second row `[2,1]` gives `2×2+1×1=5`, then rows 3 and 4 produce 7 and 9.\n\n**Why is this useful?** One matrix operation makes *four predictions* without writing four separate formulas. A matrix shaped `(number_of_examples, number_of_features)` multiplied by a weight column shaped `(number_of_features, 1)` gives one prediction per example. If the numbers of features do not agree, the multiplication is undefined.''')
    ])
    insert_after(nb,'To find **one output cell**',[
        cmark('''### Check every output cell by hand\n\nFor `A = [[1,2,3],[4,5,6]]` and `B = [[1,0],[0,1],[1,1]]`, the result is:\n\n| | B column 0 | B column 1 |\n|:--|--:|--:|\n| A row 0 | `1×1 + 2×0 + 3×1 = 4` | `1×0 + 2×1 + 3×1 = 5` |\n| A row 1 | `4×1 + 5×0 + 6×1 = 10` | `4×0 + 5×1 + 6×1 = 11` |\n\nThus `A @ B = [[4,5],[10,11]]`, with shape `(2,2)`. **Matrix multiplication is not matching-cell multiplication:** it combines a row with a column and sums across the shared inner dimension.''')
    ])
    insert_after(nb,'## 5. Reductions: turning many values into fewer values',[
        cmark('''### Which axis disappears?\n\nTake `[[1,2],[3,4]]`, shape `(2,2)`. `sum(dim=0)` adds **down** each column and returns `[4,6]`. `sum(dim=1)` adds **across** each row and returns `[3,7]`. A *reduction* decreases the number of axes or their sizes by summarizing values.\n\n**ML connection:** averaging a batch of losses turns one loss per example into one batch-level training objective. Choosing the wrong axis can silently produce the wrong result even if the program runs.''')
    ])
    insert_after(nb,'This matters because we often want to measure the size of a parameter vector',[
        cmark('''### Norm versus distance\n\nFor `v = [3,4]`, the **L2 norm** is `√(3²+4²)=5`: distance from the origin. To measure the distance *between* two vectors `a` and `b`, first take the difference `a−b`, then its norm `||a−b||₂`.\n\n**Why we care:** gradient clipping and weight regularization can use norms to control the magnitude of parameter vectors or updates; a norm measures size, not whether a prediction is correct.''')
    ])

# 2.4
nb=nbs[NB_FILES[3]]
if not any('concept-bridge' in c.metadata.get('tags',[]) for c in nb.cells):
    insert_after(nb,'## 1. Derivatives: how sensitive is an output?',[
        cmark('''### What does a derivative answer?\n\nThe function answers **"What is the output right now?"** The derivative answers **"If I nudge the input slightly, how quickly does the output change?"** For `f(x)=x²`, at `x=2` the output is 4 and the derivative is 4. Near this point, increasing x by `0.01` raises f by approximately `4×0.01=0.04`.\n\n**Why ML needs this:** a model adjusts weights rather than guessing endlessly. Derivatives describe how changing those weights will influence its error. The slope may be positive, negative, or zero, and is local: it need not stay the same for large changes.''')
    ])
    insert_before(nb,'## 3. First do the forward calculation',[
        cmark('''### A gradient is several slopes collected together\n\nWhen a loss depends on both `w` and `b`, we can ask two questions: how would the loss change if **only w** changed, and how would it change if **only b** changed? Those are partial derivatives. Combining them gives the **gradient** `∇L = [∂L/∂w, ∂L/∂b]`.\n\nWe calculate these values *at the current parameter settings*. A gradient says which small changes would initially raise or lower the loss; it is **not** a prediction or a parameter update.''')
    ])
    insert_after(nb,'A *negative* derivative with respect to w means',[
        cmark('''### Follow the complete chain backward\n\n| Stage | Forward value | Local derivative needed for `dL/dw` |\n|:--|:--|:--|\n| Weight/input | `w=1`, `x=2`, `b=1` | `dŷ/dw=x=2` |\n| Prediction | `ŷ=wx+b=3` | next: `dL/dŷ=2(ŷ−5)` |\n| Difference | `ŷ−5=−2` | `2×(−2)=−4` |\n| Squared loss | `L=(−2)²=4` | multiply `−4×2=−8` |\n\nThe loss gradient with respect to `w` is `−8`: increasing `w` slightly initially decreases loss. **The chain rule multiplies local derivatives along a path**, rather than multiplying outputs from successive forward passes. For the bias, `dŷ/db=1`, so `dL/db=−4`.''')
    ])
    insert_after(nb,'### What did `backward()` actually do?',[
        cmark('''### Distinguish three separate actions\n\n1. **Forward propagation:** evaluate `ŷ = wx+b` and the loss, producing ordinary numerical values.\n2. **Backward propagation (backpropagation):** traverse the recorded computation graph using the chain rule and accumulate derivatives in `.grad`.\n3. **Optimizer step:** use those derivatives to **change** parameter values. A common update is `new_weight = old_weight − learning_rate × gradient`.\n\nAutograd is the software system that computes derivatives; it does not decide the learning rate or update weights on its own. Forward-mode automatic differentiation is another derivative-computation method and is **not** just running the model's forward pass.''')
    ])
    insert_after(nb,'## 5. Why gradients need to be cleared',[
        cmark('''### Why can `.grad` surprise you?\n\nSuppose one backward pass yields a gradient of `−8`. If we run another backward pass that contributes `−8`, PyTorch may leave `−16` in the same `.grad` buffer, because gradients **accumulate** by default. That is useful in some advanced training setups but misleading if you thought `.grad` would always be overwritten.\n\nA normal training loop therefore clears gradients, calculates a new loss, calls `backward()`, and then updates parameters. **Clear → forward → backward → update** is a helpful beginner mental model.''')
    ])

# 2.5
nb=nbs[NB_FILES[4]]
if not any('concept-bridge' in c.metadata.get('tags',[]) for c in nb.cells):
    insert_after(nb,'## 1. Probability is about uncertain outcomes',[
        cmark('''### What, why, how, and where?\n\n**What:** Probability quantifies how likely an event is under an assumed process or model. A probability of 0 means impossible under that model; 1 means certain. **Why:** predictions and real-world observations can be uncertain even when we have good data.\n\n**How:** define the experiment and event first. With two independent fair coin tosses, there are four equally likely outcomes: HH, HT, TH, TT. The event "exactly one head" is `{HT, TH}`, so its probability is `2/4 = 0.5`. **ML connection:** probability helps us interpret prediction uncertainty and model evaluation, but an assumption like "fair independent tosses" must always be stated.''')
    ])
    insert_after(nb,'This is an **estimate** from the results we observed.',[
        cmark('''### Theoretical probability is not an observed count\n\nFor a fair coin, `P(heads)=0.5` describes the generating process. An observed fraction—for example, 7 heads in 10 tosses, or `7/10=0.7`—describes one **sample**. The two can differ without any contradiction.\n\n**Why more data helps:** the running fraction tends to settle *near* 0.5 as we collect many independent fair tosses; it need not hit 0.5 exactly. A larger sample reduces the influence of any one unusual result, but the correctness of an estimate still depends on assumptions and sampling.''')
    ])
    insert_after(nb,'The vertical bar `|` reads',[
        cmark('''### Conditional probability changes which rows we count\n\nA conditional probability restricts attention to cases where some condition is true. Its core rule is `P(A | B) = P(A and B) / P(B)`, provided `P(B) > 0`. In a dataset, you can think of this as:\n\n> Among **only the rows where B is true**, what fraction also satisfy A?\n\nIn our four-learner sample, `B` = "studied at least 3 hours" includes Chika and Dara (two rows). `A` = "passed" is true for both, so `P(pass | Hours≥3)` is estimated as `2/2=1` **in this invented sample**. It does not establish that studying caused passing. If no rows meet B, the observed fraction is undefined rather than zero.''')
    ])
    insert_after(nb,'A **mean** (average) tells us the center',[
        cmark('''### Same mean, different variability\n\nTwo classes might have scores `[5,5,5]` and `[3,5,7]`. Both have mean 5, but the first has **no spread** while the second varies. Standard deviation summarizes typical variation around the mean (in the original units).\n\n**Why this matters:** reporting only average model accuracy can conceal unreliable behavior on some examples. Also check variability, subgroup differences, and sample size; a single statistic never tells the whole story.''')
    ])

# 2.6 quick reference
nb=nbs[NB_FILES[5]]
if not any('concept-bridge' in c.metadata.get('tags',[]) for c in nb.cells):
    insert_before(nb,'## Key terms from Chapter 2',[
        cmark('''## A practical habit for learning new operations\n\nWhenever you find an unfamiliar function, ask **four questions**: (1) What does it compute? (2) Why would we use it? (3) Which input shapes/types does it accept, and what shape does it return? (4) Where will it be useful in ML?\n\nFor example, documentation for `torch.matmul` helps distinguish *matrix multiplication* from `torch.mul`, and `torch.broadcast_shapes` clarifies shape compatibility. Reading expected inputs and outputs is often more useful than memorizing the function name.''')
    ])

for name,nb in nbs.items():
    # Keep notebooks small and reproducible: no stored execution results.
    for c in nb.cells:
        if c.cell_type=='code':c.execution_count=None;c.outputs=[]
    nbformat.validate(nb)
    nbformat.write(nb,ROOT/name)

# Regenerate combined notebook from the individual lessons, using original section divider style.
combined=nbformat.v4.new_notebook(metadata=nbs[NB_FILES[0]].metadata)
for i,name in enumerate(NB_FILES):
    if i:
        combined.cells.append(nbformat.v4.new_markdown_cell('---\n\n'))
    combined.cells.extend(nbs[name].cells)
nbformat.validate(combined)
nbformat.write(combined,ROOT/'00-chapter-02-complete-workbook.ipynb')

# Quiz: reinforce the four-part explanation and compatibility limits.
qp=ROOT/'quizzes'/'chapter-02-checkpoint.ipynb'
quiz=nbformat.read(qp,as_version=4)
if not any('Additional broadcasting checks' in c.source for c in quiz.cells):
    quiz.cells.append(cmark('''## Additional broadcasting checks\n\n**Q16.** State the **shape compatibility rule**, including which direction dimensions are compared. Explain why `(3,2) + (3,3)` is invalid.\n\n**Q17.** Starting from `A=[[1],[2],[3]]` and `B=[[10,20]]`, write the **conceptual expanded** 3×2 views of A and B before writing their sum.\n\n**Q18.** A table of learner scores has shape `(1000,3)` and subject means have shape `(3,)`. Why is `scores - means` valid? How is the subtraction applied? Does broadcasting require 1,000 new copies of the mean vector?\n\n**Q19.** Give one example of how a correct model calculation can still teach the wrong lesson if the **target** or **held-out test data** leaks into preprocessing.\n\n**Q20.** Explain the difference between a **forward pass**, **backward pass**, and an **optimizer step** in one sentence each.'''))
    nbformat.write(quiz,qp)
key=ROOT/'quizzes'/'instructor-answer-key.md'
keytxt=key.read_text()
if 'Q16' not in keytxt:
    key.write_text(keytxt+'\n\n## Extended understanding checks (Q16–Q20)\n\n'
    '**Q16.** Compare aligned axes from right to left. Each must match, or one size is 1, or a missing leading axis is treated as 1. The last axes 2 and 3 conflict.\n\n'
    '**Q17.** A→`[[1,1],[2,2],[3,3]]`; B→`[[10,20],[10,20],[10,20]]`; sum→`[[11,21],[12,22],[13,23]]`. These are conceptual views, not necessarily physical copies.\n\n'
    '**Q18.** `(3,)` aligns with the last axis of `(1000,3)`; each row has the corresponding subject mean subtracted. Broadcasting does not inherently require 1,000 new copies of the mean vector.\n\n'
    '**Q19.** The target should not be included in its own predictors; using held-out test set statistics to fit imputation or scaling would contaminate evaluation.\n\n'
    '**Q20.** Forward evaluates prediction and loss. Backward applies the chain rule and computes/accumulates gradients. Optimization uses gradients to update parameters.\n',encoding='utf8')

# Explicitly document how to reproduce the revision and dual formats.
readme=ROOT/'README.md'
read=readme.read_text()
read=read.replace('19 diagrams','20 diagrams').replace('19 SVG','20 SVG').replace('19 matching PNG','20 matching PNG')
read=read.replace('| 1 | [Data manipulation & tensors](01-data-manipulation-and-tensors.ipynb) | shapes, indexing, broadcasting | 4 |','| 1 | [Data manipulation & tensors](01-data-manipulation-and-tensors.ipynb) | shapes, indexing, broadcasting | 5 |')
if '## Teaching revision' not in read:
    read += '''\n\n## Teaching revision — explanation-first edition\n\nThe notebook lessons now explicitly answer **what a concept means, why it matters, how it works step by step, and where it is used in machine learning**. Broadcasting includes its formal compatibility rule, a fully labeled conceptual-expansion SVG, matched PNG fallback, a worked example, and an invalid-shape example. Further bridges cover missing-value imputation and leakage; matrix calculations; gradients, chain rule and parameter updates; and probability versus observed frequency.\n\nAll lesson images are **SVG-first with PNG fallback**. True datasets shown in code are presented using Pandas/Markdown tables rather than pretending screenshots are data sources.\n\nTo reproduce the exact edition from the original lesson builder, from this chapter directory run:\n\n```bash\npython scripts/build_chapter2_jupyter.py\npython scripts/apply_teaching_revision.py\n```\n\nThe second script regenerates the new SVG/PNG companion and all concept-bridge cells. It is safe to rerun once this edition is present. It does not change source D2L files.\n'''
readme.write_text(read)
print('Enhanced notebooks and chapter rebuilt; dual-format diagram generated.')
for name in NB_FILES:
    n=nbs[name]; print(name, 'cells:',len(n.cells))

# Keep the validator, manifest, and reproducible environment in sync if the base builder rewrites them.
import json
manifest_path=ROOT/'chapter.json'
manifest=json.loads(manifest_path.read_text())
manifest['images']={'preferred':'svg','fallback':'png','count':20}
manifest_path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
validator_path=ROOT/'scripts'/'validate_assets.py'
v=validator_path.read_text()
v=v.replace('== 19,','== 20,').replace('== 38,','== 40,').replace('Expected 19 diagrams in combined + 19 in lessons','Expected 20 diagrams in combined + 20 in lessons')
v=v.replace('== 19\n','== 20\n').replace("'count':19","'count':20")
v=v.replace("assert len(dom.findall(f'.//{svg_ns}path')) > 0, f'SVG lacks vectors: {svg}'","assert len(dom.findall(f'.//{svg_ns}path')) + len(dom.findall(f'.//{svg_ns}rect')) + len(dom.findall(f'.//{svg_ns}line')) > 0, f'SVG lacks vector geometry: {svg}'")
validator_path.write_text(v,encoding='utf8')
requirements_path=ROOT/'requirements.txt'
r=requirements_path.read_text().rstrip()
for requirement in ['pillow>=10,<13','CairoSVG>=2.7,<3']:
    if requirement not in r: r+='\n'+requirement
requirements_path.write_text(r+'\n',encoding='utf8')
