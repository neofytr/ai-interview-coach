# Mock Interview Transcript: Weak Candidate — Data Analyst

**Role:** Data Analyst
**Background:** Recent bootcamp grad, completed a capstone project on customer churn prediction
**Focus Area:** technical
**Date:** 2026-04-30

---

## Interview Plan
- **Topics:** SQL & Data Manipulation, Statistical Reasoning, Data Visualization & Communication, Problem Structuring & Analysis Design
- **Difficulty Progression:** gradual
- **Turns:** 6

---

## Interview

**Interviewer:** Welcome! I see you recently finished a data analytics bootcamp and worked on a churn prediction project — that's a great hands-on experience to draw from. Let's start with something foundational. Can you tell me about a time you had to write a SQL query to answer a business question? Walk me through the question, how you structured the query, and what you found.

**Candidate:** Yeah, so in my capstone project we had a dataset of customer transactions and I needed to find out which customers were likely to churn. I used SQL to like pull the data from the database and then I did some aggregations, like counting how many transactions each customer had. Then I exported it to Python to do the actual analysis. The query was basically a SELECT with a GROUP BY on customer ID and then I counted the transactions and got the average order value.

**Interviewer:** Okay, got it — so you used SQL for the initial data pull. Let me dig into the SQL side a bit more. Suppose you had two tables — a `customers` table and an `orders` table — and you needed to find all customers who placed more than 3 orders in the last 90 days but whose average order value decreased compared to the prior 90 days. How would you approach writing that query?

**Candidate:** Hmm, so I'd probably do a JOIN on the two tables, like an INNER JOIN on customer ID. And then I'd use a WHERE clause to filter for the last 90 days. For the count I'd use... GROUP BY and HAVING count greater than 3. For the comparison with the prior 90 days, I think you'd need like a subquery or maybe a... I'm not totally sure how to do the comparison part in one query. I think maybe you could use a CASE statement to split the time periods? Or maybe two CTEs? I've used CTEs before but I'm not super confident on the syntax for comparing two different time windows in the same query.

**Interviewer:** That's okay — you're on the right track with CTEs. Let me simplify this a bit. Forget the comparison for now. If you just needed to find the top 10 customers by total revenue in the last 90 days, what would that query look like?

**Candidate:** Oh yeah, that's easier. So it would be SELECT customer_id, SUM of order_amount, FROM orders, WHERE order_date is greater than, um, like CURRENT_DATE minus 90 days, GROUP BY customer_id, ORDER BY the SUM descending, and then LIMIT 10. Yeah, that should work.

**Interviewer:** Good, that's correct. Let's shift to statistics since you mentioned your churn prediction project. What model or approach did you use for the churn prediction, and how did you evaluate whether it was working well?

**Candidate:** We used logistic regression. For evaluation we looked at accuracy, and I think we got around 85% accuracy which was pretty good. We also looked at the confusion matrix. The model was predicting most of the non-churners correctly but it was missing some of the churners, like the recall wasn't great. But the accuracy was still high because most customers don't churn so the classes were imbalanced.

**Interviewer:** You mentioned class imbalance and that recall was low — that's an important observation. So given that you recognized the imbalance, what did you actually do about it? Did you try any techniques to address it, and how did you decide if they worked?

**Candidate:** Um, I'm not sure we actually did anything specific about it. I think our instructor mentioned SMOTE and like undersampling but we didn't implement it in our project. We mostly just noted it as a limitation. I know that accuracy isn't the best metric for imbalanced datasets but we kind of ran out of time to try other approaches. I think if I were to redo it I would try, like, adjusting the class weights or using a different metric like F1 score or AUC.

**Interviewer:** That's honest — recognizing what you'd do differently is valuable. Let's try a more practical scenario. Imagine you're a data analyst at an e-commerce company and your product manager comes to you and says "our checkout conversion rate dropped 15% last week." How would you investigate this? Walk me through your approach step by step.

**Candidate:** Okay, so first I'd probably look at the data to see if the drop is real, like maybe it's a data issue or something. Then I'd look at whether it's across all users or maybe just mobile or just a specific country. And then I'd look at, like, what changed last week. Was there a new deploy or a price change or something. I'd probably make a dashboard or something showing the conversion rate over time broken down by different segments. And then I'd present my findings to the PM.

---

## Feedback Report

**Overall Rating:** Lean No Hire
**Overall Score:** 4.2 / 10

### Summary
The candidate demonstrates foundational awareness of data analysis concepts but consistently lacks the depth required for a Data Analyst role. SQL knowledge is limited to basic queries, statistical reasoning stays surface-level even on the capstone project, and investigative approaches to business problems are vague and unstructured. There is potential — the candidate recognizes their own gaps — but significant skill development is needed before they would be effective in a professional setting.

### Strengths
1. Correctly identified that accuracy is a misleading metric for imbalanced datasets and named the class imbalance in the churn project without prompting — this shows awareness of a concept many bootcamp grads miss entirely.
2. The basic SQL query (top 10 by revenue) was syntactically correct and logically sound, showing competence with fundamental SELECT-GROUP BY-ORDER BY patterns.
3. Showed intellectual honesty by acknowledging gaps directly ("I'm not sure we actually did anything about it") rather than fabricating knowledge — this self-awareness is a positive trait for a junior hire.

### Areas for Improvement
1. SQL skills do not extend beyond single-table aggregations. The candidate could not articulate how to compare two time windows in the same query, which is a routine analyst task. Practice writing queries with multiple CTEs, window functions (LAG, LEAD, ROW_NUMBER), and self-joins — work through 20-30 problems on platforms like LeetCode SQL or StrataScratch, focusing on multi-step business logic.
2. Statistical reasoning is superficial. Despite building a logistic regression model, the candidate couldn't describe any concrete steps taken to address the imbalance problem they identified. Before interviewing again, implement at least two resampling techniques (SMOTE, class weights) on the churn dataset and compare the results using precision-recall curves, not just accuracy.
3. The business investigation answer (checkout conversion drop) was a generic checklist without analytical depth. A strong answer would specify exact segmentation dimensions, name specific SQL queries or analyses to run, and propose hypotheses. Practice the "5 Whys" framework and prepare 2-3 investigation case studies where you walk through the actual queries and charts you would build at each step.

### Practice Questions
1. Write a SQL query using window functions to calculate the month-over-month revenue growth rate per product category.
2. You have a logistic regression model with 92% accuracy but only 30% recall on the positive class. Explain what this means in business terms and describe three specific things you would try to improve recall.
3. A/B test results show a 5% improvement in conversion with a p-value of 0.08. Your PM wants to ship the feature. What do you advise, and why?
4. Your dashboard shows a spike in user signups last Tuesday but no corresponding increase in activation. List the top 5 hypotheses you would investigate, in order of priority.
5. Explain the difference between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN using a concrete business example with customers and orders.

### Action Items
1. Complete 30 intermediate-to-hard SQL problems on StrataScratch or LeetCode SQL within the next two weeks, focusing on CTEs, window functions, and multi-table joins — track your completion rate and revisit problems you got wrong.
2. Revisit the churn prediction capstone: implement class weight adjustment and SMOTE, evaluate with precision, recall, F1, and AUC-ROC, and write a 1-page summary comparing the approaches. This becomes a concrete portfolio piece.
3. Practice the "conversion drop" investigation scenario out loud three times: name the specific SQL query you'd write at each step, the exact chart you'd build, and the hypothesis each analysis tests. Record yourself and review for vague language like "I'd probably look at the data."
4. Read one end-to-end data analysis case study per week (Mode Analytics blog, Towards Data Science case studies) and outline the analyst's approach: what data they pulled, what they segmented by, what they concluded, and what you would have done differently.

### Dimension Scores
| Dimension | Score |
|-----------|-------|
| Depth of Knowledge | 3.5 |
| Problem-Solving Approach | 4.0 |
| Communication Clarity | 5.0 |
| Use of Examples | 3.8 |
| Critical Thinking | 4.5 |
