# Released-data dictionary
## Target and model predictors
`output_index`: positive affine transform of observed average cycling power. Inverse constants are withheld. It is not a new physiological measure.

| Model variable | Meaning | Type | Handling |
|---|---|---|---|
| planned_duration_index | Nominal scheduled class duration | Numeric | Positive affine index; available before the ride |
| start_time_index | Planned start hour, approximated by recorded start hour | Numeric | Positive affine index |
| elapsed_time_index | Calendar time since the beginning of the observation period | Numeric | Positive affine index |
| exercise_7d_index | Sum of logged exercise minutes in the preceding 7 calendar days | Numeric | Excludes the entire current day; indexed |
| exercise_28d_index | Sum of logged exercise minutes in the preceding 28 calendar days | Numeric | Excludes the entire current day; indexed |
| exercise_days_7d_index | Number of prior 7 days with logged exercise | Numeric | Excludes current day; indexed |
| recent_output_index | Mean observed main-ride output in the preceding 28 days | Numeric | Same index scale as target; missing when no recent rides |
| class_type | Scheduled class category | Categorical | One-hot encoded inside training folds |
| instructor_code | Scheduled instructor | Categorical | Stable pseudonymous code; one-hot encoded |
| weekday_code | Scheduled day of week | Categorical | Stable code without original weekday labels; one-hot encoded |

## Other release columns
| Field | Meaning | Model input? |
|---|---|---|
| ride_id | Anonymous, sequential ride identifier | No |
| day_index | Relative whole-day coordinate from observation start, exact calendar dates removed | Split key only |
| longer_class | Predefined robustness-group membership | No |
| recent_development | Predefined recent-history robustness-group membership | No |
| relative_week | Relative weekly coordinate in descriptive data | No |
| exercise_days_index | Standardized descriptive exercise-day count | No |
| exercise_minutes_index | Standardized descriptive logged exercise time | No |
| mobility_minutes_index | Standardized descriptive mobility time | No |
| mindfulness_minutes_index | Standardized descriptive mindfulness time | No |

Missing recent output means no eligible recent main-ride observations. Fitted models impute numeric missingness from their training data. The recent-average benchmark falls back to its training target mean. One-hot encoding handles categories unseen in training without learning from evaluation outcomes. Descriptive activity indexing uses its own series-wide scale and is never a predictive input.

## Result columns
MAE_index is mean absolute error. RMSE_index is root mean squared error. bias_index is prediction minus observation averaged across rides. R2 compares squared prediction error with variation around the evaluation-set mean and may be negative. The percentage improvement column compares each candidate with the fixed training mean. All index errors use a common scale.
