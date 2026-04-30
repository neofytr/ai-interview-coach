# Backend Engineer — Interview Guide

## API Design and Web Services

API design questions reveal how candidates think about contracts between systems. Interviewers ask "Design an API for a ride-sharing service" or "How would you version this API without breaking existing clients?" They evaluate whether the candidate considers resource modeling (RESTful noun-based endpoints vs. RPC-style), appropriate use of HTTP methods and status codes, pagination strategies (cursor-based vs. offset-based and why), authentication and authorization patterns, and rate limiting.

Key competencies: REST principles and when to deviate from them, GraphQL tradeoffs (flexibility vs. complexity, N+1 queries, schema evolution), gRPC for internal service communication, idempotency for safe retries, request validation, and meaningful error responses. Strong candidates also discuss API documentation, backward compatibility, and deprecation strategies.

Common pitfall: designing APIs around internal data models rather than consumer needs. Another is ignoring error handling — candidates who describe only the happy path and cannot articulate what happens when a downstream service is unavailable or a request contains malformed data reveal a gap in production thinking.

## Databases and Data Modeling

Database questions go beyond "SQL vs. NoSQL." Interviewers assess whether candidates can choose the right storage solution for specific access patterns and constraints. A question like "Design the data model for an e-commerce platform" tests normalization vs. denormalization decisions, indexing strategy, handling of transactions (ACID properties), and awareness of read/write patterns that influence schema design.

Evaluation criteria: understanding of B-tree and hash indexes, query planning and EXPLAIN output, replication strategies, partitioning approaches, and when to use specialized stores (Redis for caching, Elasticsearch for search, time-series databases for metrics). Strong candidates think about data access patterns before choosing a database, not after, and reason about consistency requirements per use case rather than applying a blanket approach.

## Scalability and Reliability

Scalability questions test whether candidates can reason about systems under increasing load. "Your API handles 100 requests per second today and needs to handle 10,000 — what changes?" Great candidates start by identifying the bottleneck (compute, I/O, database, network) through measurement rather than guessing, then propose targeted solutions: horizontal scaling behind a load balancer, caching at the appropriate layer (CDN, application, database), asynchronous processing via message queues for non-critical-path work, and read replicas for read-heavy workloads.

Reliability evaluation focuses on failure modes: "What happens when this service goes down?" Strong candidates discuss circuit breakers, retries with exponential backoff and jitter, graceful degradation, health checks, and bulkhead patterns. They understand that distributed systems will fail and design for resilience rather than prevention.

## Distributed Systems Concepts

Senior backend candidates face questions on consensus protocols, distributed transactions (saga pattern, two-phase commit), event-driven architectures, and observability. Interviewers assess whether candidates understand the fundamental challenges: network partitions, clock skew, exactly-once delivery being effectively impossible, and the practical implications of the CAP theorem.

What separates good from great: good candidates describe how a distributed system works. Great candidates describe how it fails, how you detect the failure, and how you recover from it.
