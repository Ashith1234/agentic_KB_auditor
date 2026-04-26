# System Architecture

## Overview

The Agentic KB Auditor operates as a middleware layer between the chatbot and its knowledge base.

```
User → Chatbot → Knowledge Base
                     ↑
              Auditor System (Middleware)
```

## Component Diagram

```
+------------------+     +-------------------+     +------------------+
|   RAG Plugin     | --> |   Orchestrator    | --> | Remediation Eng. |
| (middleware.py)  |     |   (pipeline.py)   |     |   (engine.py)    |
+------------------+     +-------------------+     +------------------+
                                 |                          |
                    +------------+------------+             v
                    v            v            v    +------------------+
             +----------+ +----------+ +----------+|   KB System     |
             | Version  | |Duplicate | |Coverage  || (vector_store,  |
             | Agent    | | Agent    | | Agent    ||  search, sync)  |
             +----------+ +----------+ +----------++------------------+
                    |            |            |
                    +------------+------------+
                                 v
                         +---------------+
                         |  Supervisor   |
                         |    Agent      |
                         +---------------+
```

## Data Flow

1. User sends query to chatbot.
2. Plugin middleware intercepts the request.
3. Agents run analysis in parallel.
4. Supervisor aggregates signals.
5. Remediation engine decides action: auto-fix, suggest, or escalate.
6. KB is updated safely.
7. Dashboard reflects new state.
