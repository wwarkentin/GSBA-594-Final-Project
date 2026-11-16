# Personal Fitness Analytics — William J. Warkentin
GSBA 594 final project starter. Analyze training consistency, comparable cycling rides, and pre-ride output prediction.

## Run in Jupyter
Extract this folder, install the requirements, and open `Peloton_Analysis.ipynb` from this folder. Run cells from top to bottom. The notebook imports the accompanying script; keep them together.

## Run in a terminal
```
python -m pip install -r requirements.txt
python analyze_peloton.py --csv workouts.csv --out results
```
To use a new export, replace `workouts.csv` or pass its path with `--csv`.

## What is included
- Commented reusable Python script, and a notebook organized for classroom explanation.
- Original CSV, charts, tables, data quality audit, holdout predictions, and interpretation notes.
- All 1,688 records (March 2021–November 2026) retained for activity analysis.
- 434 main cycling rides: at least 15 minutes, positive watts, excluding warm-up/cool-down types.
- Historical features from all activities plus recent main-ride performance; every feature excludes the current day.
- Training on 343 rides; evaluation on 91 later rides starting July 5, 2026.

## Initial results
| Model | MAE (watts) | R² |
|---|---:|---:|
| Training mean baseline | 13.21 | -0.203 |
| Ridge regression | 11.82 | 0.086 |
| Random forest | 15.06 | -0.484 |

The regression modestly outperforms the baseline. The forest does not. Keep this result in the project: model complexity does not guarantee better predictions. These are single-holdout estimates, not established generalization guarantees. Do not repeatedly tune against this holdout.

Read `results/interpretation_notes.md` before drawing conclusions. No physiological fitness, weight-loss causation, or recovery prescription is established from this export. Instructor averages reflect class selection and effort as well as instruction. Features called training minutes include meditation and stretching; they measure logged activity, not physiological load.

Your personal workout history is included. Review before uploading the folder to a public GitHub repository.
