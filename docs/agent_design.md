# Agent Design

## Base Agent

All agents inherit from `BaseAgent`, which defines the `analyze(data)` contract.

## Agent Descriptions

| Agent | Responsibility | Key Output |
|---|---|---|
| `VersionAgent` | Detects outdated KB content | `AuditSignal(OUTDATED)` |
| `DuplicateAgent` | Finds duplicate/conflicting docs | `AuditSignal(DUPLICATE)` |
| `CoverageAgent` | Identifies missing topics | `AuditSignal(GAP)` |
| `RetrievalAgent` | Fetches verified external info | Verified content string |
| `ScoringAgent` | Evaluates overall KB health | Health score dict |
| `LearningAgent` | Proposes KB updates | Updated content |
| `SupervisorAgent` | Aggregates signals from all agents | Combined signal list |

## Design Principles

- **Single Responsibility**: Each agent does exactly one task.
- **Composable**: Agents can be added/removed without changing others.
- **Pluggable**: New agents simply inherit from `BaseAgent`.

## Separation of Concerns: Code vs. Prompt

The architecture relies on a strict boundary between deterministic Python operations and semantic LLM evaluations:

| Agent                  | Done by Code                                   | Done by Prompt                                  |
| ---------------------- | ---------------------------------------------- | ----------------------------------------------- |
| **SupervisorAgent**    | Selects agents, runs them, combines results    | May summarize final report                      |
| **VersionAgent**       | Gets chunk version, checks DB timestamps       | Decides if content is outdated                  |
| **RetrievalAgent**     | Runs FAISS search, query expansion             | Judges whether retrieved chunk is relevant      |
| **CoverageAgent**      | Compares query with retrieved chunks           | Explains what information is missing            |
| **DuplicateAgent**     | Computes similarity / compares chunk pairs     | Determines contradiction meaning                |
| **TrustedSourceAgent** | Scrapes trusted sites, checks source health DB | Compares RAG answer with trusted source content |
| **LearningAgent**      | Stores learned rules in semantic DB            | Converts correction into reusable rule          |
| **PlannerAgent**       | Creates remediation task structure             | Generates step-by-step fix plan                 |
| **ScoringAgent**       | Calculates scores, logs confidence             | Explains why score is high/low                  |
