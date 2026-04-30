# Software Engineer — Interview Guide

## System Design and Architecture

Interviewers assess whether a candidate can decompose ambiguous, large-scale problems into concrete components and reason about tradeoffs under constraints. A strong answer to "Design a URL shortener" is not a memorized diagram — it is a structured conversation where the candidate clarifies requirements (read-heavy vs. write-heavy, latency targets, consistency needs), proposes a high-level architecture, then drills into specifics like hashing strategies, database choice, and caching layers. What separates good from great is the ability to articulate *why* one approach beats another in a given context. Saying "I'd use Cassandra" is weak. Saying "We need high write throughput and can tolerate eventual consistency, so a wide-column store like Cassandra fits better than Postgres here" demonstrates real judgment.

Key competencies: capacity estimation, component decomposition, API design, data modeling, identifying bottlenecks, horizontal vs. vertical scaling reasoning, and understanding CAP theorem tradeoffs in practice rather than in theory.

Common pitfall: jumping straight into low-level details without first aligning on requirements and scope. Another pitfall is over-engineering — proposing Kafka, Redis, and a microservice mesh for a system that serves 100 users.

## Coding and Problem Solving

The coding interview is not about getting the optimal solution on the first try. Interviewers evaluate how a candidate thinks through a problem: do they ask clarifying questions, identify edge cases before coding, and communicate their approach? A candidate who talks through a brute-force solution, analyzes its complexity, then iterates toward something better will outscore someone who silently writes an optimal solution they memorized.

Evaluation criteria: correctness, time/space complexity awareness, code readability, handling of edge cases (empty inputs, overflow, duplicates), and ability to test their own code mentally or with examples. Interviewers also look for clean variable naming, modular functions, and avoidance of unnecessary complexity.

Red flags: silence while coding, inability to estimate Big-O, writing code that only works for the happy path, and defensiveness when the interviewer offers hints.

## Debugging and Technical Depth

Senior-level candidates are expected to demonstrate debugging intuition. When presented with a failing system or buggy code, strong candidates form hypotheses, isolate variables, and systematically narrow the problem space. They ask "What changed recently?" and "Can I reproduce this?" rather than guessing randomly.

Technical depth is probed through follow-up questions: "What happens if this service goes down?" or "How would you handle a race condition here?" Candidates who can reason about concurrency, memory management, network failures, and observability (logging, metrics, tracing) stand out.

## What Separates Good from Great

Good candidates solve the problem. Great candidates solve the problem *and* discuss operational concerns — monitoring, deployment strategy, failure modes, and how the system evolves when requirements change. They treat the interview as a collaborative design session rather than an exam. They acknowledge uncertainty ("I'm not sure about the exact replication lag, but here's how I'd find out") rather than bluffing. They ask the interviewer smart questions that demonstrate they have built and operated real systems.
