# Q&A preparation
**Why did regression outperform the forest?**
It has the lowest later-period MAE here. A limited sample, noisy outcomes and changing historical regimes can favor simpler approaches, but no isolated cause is established.

**Which model was selected?**
The recent 28-day mean has the lowest mean development error. Regression leads the later comparison. Changing selection after seeing that comparison would be retrospective.

**Which variables are used?**
Seven numeric predictors and three categorical predictors, fully listed in README. Relative day and row ID are split/identifier fields, not extra model inputs.

**Were variables already scaled?**
Yes. Training-fitted numeric standardization was already in the pipeline. The released data now also use masked measurement scales, coded categories and relative dates.

**Does scaling change results?**
Fixed affine changes of target units re-express errors and preserve R² for equivalently transformed predictions. Standardizing inputs matters for regularized models, so the same fold-specific pipeline is retained. A numerical check found linear predictions equivalent within floating-point tolerance and small forest differences without a changed substantive ranking.

**Is the release fully anonymous?**
No guarantee is claimed. Removing direct identifiers and masking magnitudes reduces exposure, but relational and temporal patterns remain.

**Can this establish health or churn benefits?**
No. Those outcomes and causal designs are not part of the study.
