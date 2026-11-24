# Connected Fitness Analytics: Results
## Decision
Assess whether scheduled-class metadata and prior workout history warrant a performance-feedback prototype beyond simple summaries.

## Key findings
- Ridge regression has the lowest later-period MAE, 0.543 output-index units.
- Random forest records 0.747, while the training mean records 0.630.
- The recent 28-day mean records 0.587 average development MAE and wins the predeclared development rule.
- Regression's development performance varies sharply, so the later-period advantage does not establish universal superiority.
- A recent-window sensitivity narrows regression's development error, showing that the historical window matters.
- The later-period analysis is exploratory because earlier work already exposed it.

| Candidate | Development MAE | Later MAE | Later R² |
|---|---:|---:|---:|
| Training mean | 0.973 | 0.630 | -0.171 |
| Class group mean | 0.886 | 0.547 | 0.105 |
| Recent 28-day mean | 0.587 | 0.596 | -0.071 |
| Ridge regression | 1.364 | 0.543 | 0.171 |
| Random forest | 1.067 | 0.747 | -0.530 |


## Implication
Simpler methods can outperform a nonlinear ensemble in a relevant evaluation. Preserve the distinction between the strongest later-period result and the model selected using development data. A prospective comparison should retain recent averages and regression, define useful error tolerances with users, then evaluate new records before product deployment.

## Data handling
The release reports indices and relative time. It omits the raw export and ownership narrative. Masking reduces exposure without guaranteeing anonymity. All code runs from the protected modeling table, so the original export is not required for reproducing the reported model comparison.
