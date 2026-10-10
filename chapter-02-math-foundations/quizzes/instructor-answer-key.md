# Chapter 2 checkpoint — Instructor answer key

Keep this file separate from the main learner view until after the checkpoint.

1. `(4, 3)`; 12 numbers.
2. `4`. Index 1 selects the second row; index 0 the first column.
3. An axis with length one can broadcast; the result is `(3, 2)`.
4. “Missing” means unknown; 0 means the true value is zero.
5. No. That would leak the answer into the inputs.
6. Three indicator columns (`is_Video`, `is_Text`, `is_Audio`). Each row has 1 in its category column and 0 in the other two.
7. `2×4 + 3×5 = 8 + 15 = 23`.
8. `(4,3)`. The inner dimensions (2) match.
9. `*` is elementwise multiplication, whereas `@` computes row–column dot products.
10. Prediction `3`; squared error `(3−5)² = 4`.
11. `dL/dŷ = 2(3−5) = −4`, and `dŷ/dw = 2`. Multiply to get `−8`.
12. No. It calculates and stores gradients. An optimizer or manual weight-update step then changes parameters.
13. `2/4 = 1/2`, because HT and TH qualify.
14. No; 50 is an expectation, not a guaranteed observed count. Samples vary.
15. The **sample conditional proportion** is 100% among the two higher-hour learners. Only four synthetic cases exist; correlation is not evidence of a general causal rule.


## Extended understanding checks (Q16–Q20)

**Q16.** Compare aligned axes from right to left. Each must match, or one size is 1, or a missing leading axis is treated as 1. The last axes 2 and 3 conflict.

**Q17.** A→`[[1,1],[2,2],[3,3]]`; B→`[[10,20],[10,20],[10,20]]`; sum→`[[11,21],[12,22],[13,23]]`. These are conceptual views, not necessarily physical copies.

**Q18.** `(3,)` aligns with the last axis of `(1000,3)`; each row has the corresponding subject mean subtracted. Broadcasting does not inherently require 1,000 new copies of the mean vector.

**Q19.** The target should not be included in its own predictors; using held-out test set statistics to fit imputation or scaling would contaminate evaluation.

**Q20.** Forward evaluates prediction and loss. Backward applies the chain rule and computes/accumulates gradients. Optimization uses gradients to update parameters.
