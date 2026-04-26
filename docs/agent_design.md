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
