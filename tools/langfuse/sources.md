# Langfuse: sources (checked 2026-10-20)

Taken only from the repo and its own docs.

| Fact | Value | Source |
|---|---|---|
| What it is | "Open source agent evals & observability: Trace, evaluate, and improve LLM applications with one open platform." | GitHub repo description, https://github.com/langfuse/langfuse |
| Stars | 36,080 | https://api.github.com/repos/langfuse/langfuse (2026-10-20) |
| Latest release | v4.64.0, 2026-10-19 | https://api.github.com/repos/langfuse/langfuse/releases/latest |
| Licence | MIT ("MIT Expat"), except anything under `ee/`, `web/src/ee/` and `worker/src/ee/`, which falls under `ee/LICENSE` | https://github.com/langfuse/langfuse/blob/main/LICENSE |
| Owner | "since January 2026 we're part of ClickHouse"; the copyright line reads ClickHouse, Inc. | README; LICENSE |
| Tracing | "Instrument your app and start ingesting traces … tracking LLM calls and other relevant logic … Inspect and debug complex logs and user sessions." | README › Core Features; https://langfuse.com/docs/tracing |
| Cost | "tracks the usage and cost of every LLM call"; "ships with prices for popular models from OpenAI, Anthropic, and Google" | https://langfuse.com/docs/observability/features/token-and-cost-tracking |
| Evaluations | "LLM-as-a-judge, Code evaluators, user feedback collection, manual labeling, and custom evaluation pipelines" | README › Core Features; https://langfuse.com/docs/evaluation/overview |
| Self-hosting needs | Langfuse Web, Langfuse Worker, PostgreSQL, Redis/Valkey, ClickHouse, S3/blob storage. Docker Compose is a "Single VM without high availability, scaling, or backups", meant for local use and testing; Helm on Kubernetes is the "preferred production deployment". | https://langfuse.com/self-hosting; README › Self-Host |
| Enterprise features | Some add-ons "require a license key", for example Organization Creators, Instance Management API and UI Customization | https://langfuse.com/self-hosting |
| Quickstart | `git clone --depth=1 https://github.com/langfuse/langfuse.git`, then `cd langfuse`, then `docker compose up`: "Run Langfuse on your own machine in 5 minutes" | README › Self-Host Langfuse |
| Cloud | "Managed deployment by the Langfuse team, generous free-tier, no credit card required." | README › Langfuse Cloud |
| Alternative (same category) | Arize Phoenix | index.json category "AI tracing and monitoring" |

Not run locally for this video. The scenes show the documented commands and features, not a recorded session.
