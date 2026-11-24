# Methods
The source is a longitudinal Peloton workout export used as an individual-record case study. Ownership attribution is withheld. It contains 1,688 workout rows and 659 cycling rows. The raw export is retained outside this release.

## Source preparation
The preparation checks exact duplicate rows, date parsing, invalid durations, negative/nonfinite numeric values and resistance outside 0–100. No invalid rows were detected under those checks in the source used here. Timestamp annotations vary; preparation preserves exported wall-clock dates. Empty category values receive an Unknown label. Missing activity-specific metrics remain missing.
Exercise includes disciplines outside Meditation, Stretching and Yoga. The latter disciplines form mindfulness and mobility summaries. Exported lengths measure logged session time rather than verified active time. No-logging days are not proof of inactivity.
Main cycling rides require positive average power, recorded duration of at least 15 minutes, and no warm/cool type. This gives 434 main rides. The predictive population additionally requires scheduled-class metadata and nominal title duration of at least 15 minutes, excluding self-paced/scenic titles, giving 420 records. The additional 14 main rides can contribute only to prior-history features. No raw titles, timestamps or measurements are distributed.

## Feature construction
Before masking, daily aggregation followed by a one-day shift constructs prior 7-/28-day exercise minutes, prior 7-day exercise days and prior 28-day main-ride average power. This excludes all current-day outcomes. Scheduled duration, type and instructor are pre-ride metadata. Recorded start hour approximates intended start hour. Exact timing and availability would need validation in a live product.
The published model_features.csv contains these prepared variables after fixed affine masking, plus category codes, relative day and masked target. An investigator can reproduce every model from the released features but cannot regenerate the unmasked source export. Original cleaning operations and feature windows are documented above. Masking constants and inverse maps are not included.

## Folds and models
First 80% of unique ride days form development (331 rides), remaining days form later evaluation (89 rides). Three expanding development folds preserve temporal order and group same-day observations. Folds cover unequal calendar spans. Selection uses unweighted mean fold MAE. Imputation, standardization and one-hot encoding fit only the current training partition.
Compare a fixed training mean, training duration/type group mean, recent 28-day mean, ridge (alpha=10) and random forest (150 trees, max depth 8, min leaf 8, seed 42). Settings are fixed. Historical features can use completed earlier evaluation days, matching sequential daily use. Parameters remain fixed within an evaluation window.
Sensitivity checks repeat development folds within two predefined subsets. They change population/window and are descriptive robustness comparisons, not new late-period optimization.

## Results and limits
Ridge has the best later-period MAE, while the recent mean wins the specified development rule. This supports transparent benchmark comparison, not a universal ranking of algorithms. The later period was exposed in earlier analysis and remains exploratory. New observations and additional participants are required for prospective/general-population validation.
Original-value MAE was converted to output-index MAE, so old unit-specific errors should not be mixed with revised errors. See MASKING_CHECK.md for verification. No clinical, weight-loss, retention or revenue effect is measured.
