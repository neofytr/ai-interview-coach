# Data Scientist — Interview Guide

## Machine Learning Fundamentals

Interviewers expect candidates to go well beyond textbook definitions. Asking "Explain the bias-variance tradeoff" is a warm-up — the real evaluation is whether the candidate can apply it: "Your model has high accuracy on training data but poor test performance. Walk me through your diagnosis." Strong candidates describe a systematic approach: inspect learning curves, check for data leakage, evaluate feature distributions between train and test, try regularization, and consider whether the model complexity is appropriate for the dataset size.

Key competencies: supervised vs. unsupervised learning, familiarity with core algorithms (logistic regression, tree-based methods, SVMs, neural networks), awareness of when simple models outperform complex ones, and cross-validation strategies. Candidates should explain gradient descent, regularization (L1 vs. L2), and ensemble methods in intuitive terms.

Common pitfall: jumping to deep learning for every problem. If the dataset has 500 rows, proposing a transformer raises red flags. Another pitfall is treating model selection as the entire job while neglecting data quality and problem framing.

## Experimentation and Causal Inference

A/B testing is central to applied data science. Interviewers probe whether candidates can design experiments correctly: defining hypotheses, choosing metrics, calculating sample size, handling multiple comparisons, and interpreting results. A common question is "Your A/B test shows a 3% lift in click-through rate with p=0.04 — should we ship?" Great candidates discuss practical significance vs. statistical significance, check for novelty effects, examine segment-level results, and consider long-term impact vs. short-term gains.

Beyond A/B tests, strong candidates understand quasi-experimental methods — difference-in-differences, regression discontinuity, instrumental variables — and know when randomized experiments are not feasible. They reason about confounders, selection bias, and survivorship bias without being prompted.

## Feature Engineering and Data Pipelines

Feature engineering separates strong data scientists from those who only know how to call sklearn.fit(). Interviewers assess whether candidates can think creatively about transforming raw data into predictive signals: encoding categorical variables appropriately, creating interaction features, handling temporal features (cyclical encoding, lag features), dealing with missing data beyond simple imputation, and understanding when feature scaling matters.

Evaluation criteria: reasoning about feature importance and multicollinearity, awareness of target leakage, and practical experience with pipeline tools. Candidates who iterate — starting with simple features, evaluating contribution, then adding complexity — demonstrate real-world maturity.

## Model Evaluation and Deployment

Choosing the right evaluation metric is itself a test of judgment. Interviewers ask "Would you optimize for precision or recall here?" and evaluate whether the candidate connects the answer to business consequences — false positives in fraud detection have different costs than false positives in spam filtering. Strong candidates discuss confusion matrices, ROC-AUC vs. PR-AUC for imbalanced classes, calibration, and how to evaluate ranking models.

On deployment, candidates should articulate how a model moves from notebook to production: monitoring for data drift, setting up retraining pipelines, A/B testing against the current system, and defining rollback criteria. The gap between "I trained a model" and "I deployed a reliable prediction system" is where senior candidates distinguish themselves.
