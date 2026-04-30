# Data Analyst — Interview Guide

## SQL and Data Manipulation

SQL proficiency is non-negotiable. Interviewers start with fundamentals — JOINs, GROUP BY, window functions, subqueries — and escalate to complex scenarios: "Write a query to find users whose spending increased month-over-month for three consecutive months." They evaluate not just correctness but also efficiency and readability. Candidates who write clean, well-aliased queries with comments explaining non-obvious logic demonstrate professional maturity.

Key competencies: JOIN types and when each applies, CTEs for readability, window functions (ROW_NUMBER, RANK, LAG, LEAD), handling NULLs correctly, and awareness of query performance and indexing.

Common pitfall: writing technically correct SQL that is impossible for a colleague to maintain. Another is failing to handle edge cases — ties in rankings, users with no transactions. Interviewers watch whether candidates consider data quality issues (duplicates, missing values) before diving into analysis.

## Statistics and Analytical Reasoning

Data analysts are expected to understand descriptive statistics, distributions, correlation vs. causation, and the basics of hypothesis testing. Interview questions might include: "Revenue dropped 15% last week — walk me through how you'd investigate" or "A stakeholder says Feature X increased conversion by 20% — how would you validate that claim?"

Strong candidates approach investigation systematically: segment by dimension (geography, device, user cohort), check for external factors (seasonality, outages, marketing campaigns), validate data integrity, and form hypotheses before querying. They distinguish between correlation and causation without being prompted. They know when a result is statistically significant and when the sample size is too small to draw conclusions.

Evaluation criteria: intellectual curiosity, structured thinking under ambiguity, ability to ask the right follow-up questions, and comfort with saying "I need more data before I can answer that."

## Data Storytelling and Communication

The highest-impact skill for a data analyst is the ability to translate findings into decisions. Interviewers assess this through case studies or presentation exercises. A candidate who says "churn increased 8% quarter-over-quarter" has stated a fact. A candidate who says "churn among first-year subscribers increased 8%, driven primarily by users who never completed onboarding — here are three interventions we could test" has told a story that drives action.

Great candidates structure their communication for the audience: executives get the headline and recommendation first, with supporting detail available on request. They use visualizations purposefully — choosing the right chart type, labeling axes clearly, and highlighting the insight rather than decorating the data. They acknowledge limitations and uncertainty rather than overstating conclusions.

## Business Acumen and Impact Orientation

Technical skills alone do not distinguish top candidates. Interviewers look for analysts who understand the business context — revenue model, customer lifecycle, competitive dynamics — and connect their analysis to decisions that move metrics the company cares about. The best candidates ask "What decision will this analysis inform?" before starting any work. They proactively identify opportunities rather than waiting for requests, and they follow up on whether their recommendations were implemented and what the outcome was.
