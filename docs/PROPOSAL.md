# Connected Fitness Analytics: Project Proposal
GSBA 594–42H

## Problem and purpose
Connected fitness product teams must determine whether historical workout records can support useful performance expectations for a selected class. This project evaluates predictive feedback against simple historical benchmarks. Members need understandable feedback, coaches need context and product teams need evidence before implementing a prediction feature. Peloton's AI coaching announcement establishes industry relevance without proving this prototype's effectiveness.

## Data and approach
A de-identified longitudinal workout dataset supplies 1,688 workouts, including 659 cycling sessions. The modeling sample contains 420 scheduled-class rides with suitable pre-ride metadata. Source preparation standardizes fields, preserves activity-specific missingness and constructs prior-day historical features. Released variables use masked indices and relative chronology. Ownership attribution, original measurements and inverse keys are excluded.

Python will compare training and class-group means, a recent-performance benchmark, ridge regression and random forest. Three chronological development splits will guide selection. Later-period error comparisons, subgroup/robustness checks and visualizations will inform the decision. Earlier exposure to the later period will remain an explicit exploratory limitation.

## Contribution and deliverables
The project will assess whether evidence supports a performance-feedback prototype and explain when simple methods are sufficient. Deliverables include reproducible Python code, an executed notebook, a data dictionary, masked data, charts, a README with model variables and bulleted findings, and a presentation. One-record-history analysis cannot establish population effectiveness, health improvement or reduced subscription churn.

See SOURCES.md for supporting sources.
