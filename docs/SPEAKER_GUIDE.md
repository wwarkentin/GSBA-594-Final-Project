# Speaker guide

Ten main slides for approximately 12 minutes including discussion.

## Slide 1: Connected fitness analytics

This project evaluates whether workout histories can support useful performance feedback. The data are a protected longitudinal case study. The presentation does not identify the data owner. The central decision is whether predictive feedback provides enough value beyond understandable historical summaries.

## Slide 2: The product decision

Industry evidence motivates the business problem. The announcement does not establish that this prototype improves outcomes. The study evaluates prediction accuracy, not retention or clinical benefit. Source: https://investor.onepeloton.com/news-releases/news-release-details/peloton-launches-foldable-peloton-tread-flex-its-most-affordable

## Slide 3: A protected longitudinal dataset

Different inclusion rules produce different sample sizes. Main rides exclude short warm-up and cool-down rides. Scheduled-class metadata permits nominal duration known before the ride. Only the protected prepared feature table is distributed.

## Slide 4: The variables and preprocessing

There are seven numeric and three categorical predictors. Row ID and relative day are not extra predictors. Current-ride outcome fields are excluded. The numeric predictors were already standardized within folds before this revision. The release adds measurement masking.

## Slide 5: Activity varies across observation blocks

The descriptive series preserves broad shape and gaps. Standardized values can be negative. These descriptive indices never enter model fitting, so their series-wide scaling is not predictive preprocessing.

## Slide 6: Indexed output varies across periods

Each block contains a quarter of the modeling records, not equal calendar duration. These means are descriptive and do not isolate a training effect. Target values appear only in output-index units.

## Slide 7: Chronological development and evaluation

Historical features can update after completed earlier evaluation days, while coefficients and trees stay fixed inside each window. Folds cover unequal calendar spans. A prospective test requires genuinely new records.

## Slide 8: Regression leads the later comparison

Regression has about 13.8 percent lower later MAE than the training mean and about 27.3 percent lower than the forest. This supports the finding that a simpler model can be useful. However, the recent mean wins the actual development rule, so the presentation preserves that distinction.

## Slide 9: Final key findings

A recent development-window sensitivity narrows regression error and illustrates time-window dependence. No universal algorithm ranking is established. Fixed affine changes re-express output units, but numerical ties can slightly change a refitted forest. The verification is in docs/MASKING_CHECK.md.

## Slide 10: Prospective validation and next steps

Use the revised release rather than the earlier raw-data package. The repository should include its README variable table and bulleted findings. Updating files does not remove old GitHub history. Product, health and retention effects need additional evidence.