# System Design Interview Framework

## Overview

System design interviews evaluate a candidate's ability to architect scalable, reliable, and maintainable systems. They test breadth of knowledge across infrastructure, data storage, networking, and distributed systems, combined with the judgment to make appropriate tradeoffs for a given context.

## Interview Structure

A well-run system design interview follows four phases:

**Requirements Gathering (5 minutes):** The candidate should clarify functional requirements (what the system does), non-functional requirements (scale, latency, availability, consistency), and constraints (budget, team size, timeline). Strong candidates ask about expected scale: daily active users, requests per second, data volume, and read/write ratio.

**High-Level Design (10 minutes):** Sketch the major components and their interactions. This typically includes clients, load balancers, application servers, databases, caches, and message queues. The goal is a coherent architecture that satisfies the requirements, not a detailed implementation.

**Deep Dive (15 minutes):** The interviewer selects 1-2 components for detailed discussion. This is where candidates demonstrate depth: database schema design, caching strategies, API design, data partitioning, or consistency models. Strong candidates drive this section proactively based on what they identify as the hardest problems.

**Tradeoffs and Extensions (5 minutes):** Discuss what would change at 10x or 100x scale. Address failure modes, monitoring, and operational concerns. This tests whether the candidate thinks about systems in production, not just on a whiteboard.

## Key Evaluation Dimensions

**Scalability reasoning:** Does the candidate understand horizontal vs. vertical scaling, sharding strategies, and when to introduce caching? Can they estimate capacity requirements from user numbers?

**Data modeling:** Can the candidate choose appropriate storage systems (relational vs. NoSQL vs. blob store) based on access patterns? Do they consider indexing, denormalization, and query performance?

**Tradeoff articulation:** Does the candidate explicitly name tradeoffs (consistency vs. availability, latency vs. throughput, simplicity vs. flexibility) and justify their choices for the specific use case?

**Operational awareness:** Does the candidate consider monitoring, alerting, deployment, and failure recovery? Production systems need observability — candidates who ignore this are designing for demos, not reality.

## Common Pitfalls

- Jumping into component details without establishing requirements
- Over-engineering for scale that isn't needed (premature optimization)
- Ignoring failure modes and assuming everything works
- Not quantifying: "a lot of data" vs. "approximately 500 GB/day"
- Treating the interview as a monologue rather than a collaborative design session

## Difficulty Calibration

Junior engineers should demonstrate understanding of basic client-server architecture and common patterns. Mid-level engineers should handle sharding, caching, and async processing. Senior engineers should discuss consistency models, distributed consensus, and multi-region architecture with nuance.
