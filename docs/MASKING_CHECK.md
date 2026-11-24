# Masking and numerical verification
The original numeric pipeline already standardized inside each training fold. This release adds fixed positive affine measurement indices, a masked target, relative chronology and stable category codes. Inverse constants remain outside the release.

Directly comparing equivalent transformed predictions verifies the fixed mean, class-group mean, recent mean and ridge predictions within floating-point tolerance. The forest can change slightly because equivalent rescaling changes numerical ties in tree construction. No exact invariance claim is made for a refitted forest. Rankings and substantive conclusions are unchanged in this check.

Maximum absolute prediction differences, in output-index units:

- Training mean: 6.85e-16
- Class group mean: 9.44e-16
- Recent 28-day mean: 8.33e-17
- Ridge regression: 3.33e-15
- Random forest: 0.00759

Original MAE/RMSE values are intentionally not republished. Target scaling changes their units. R² and percentage comparisons are appropriate for checking substantive consistency. Standardization alone does not guarantee anonymity. Exact patterns can remain identifiable using external information.
