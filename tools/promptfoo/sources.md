# promptfoo: sources (checked 2026-10-20)

Taken only from the repo and its own docs.

| Fact | Value | Source |
|---|---|---|
| What it is | "a CLI and library for evaluating and red-teaming LLM-based apps" | README, https://github.com/promptfoo/promptfoo |
| Repo description | "Test your prompts, agents, and RAGs. Red teaming/pentesting/vulnerability scanning for AI. Compare performance of GPT, Claude, Gemini, DeepSeek, and more. Simple declarative configs with command line and CI/CD integration." (Its last sentence is a production-use claim and is not used.) | https://api.github.com/repos/promptfoo/promptfoo |
| Stars | 26,183 | https://api.github.com/repos/promptfoo/promptfoo (2026-10-20) |
| Latest release | 0.124.1, 2026-10-08. `releases/latest` returns `code-scan-action-0.2.2` (a side package), so the main version comes from the release list; npm `latest` is also 0.124.1 | https://api.github.com/repos/promptfoo/promptfoo/releases ; https://registry.npmjs.org/promptfoo/latest |
| Maturity | Repo created 2023-04-28; still 0.x; releases every week or two; 799 open issues and PRs | GitHub API (2026-10-20) |
| Licence | MIT ("Copyright (c) Promptfoo 2025"). No separate enterprise or `ee/` folder. A few bundled third-party files keep their own notices: `src/external/APACHE_LICENSE` (Apache-2.0) and `src/redteam/providers/crescendo/LICENSE` (MIT, Microsoft, based on PyRIT) | https://github.com/promptfoo/promptfoo/blob/main/LICENSE |
| Owner | "Promptfoo is now part of OpenAI. Promptfoo remains open source and MIT licensed." Announced 2026-03-09: "Promptfoo has agreed to be acquired by OpenAI … Promptfoo will remain open source" | README; https://www.promptfoo.dev/blog/promptfoo-joining-openai/ |
| How it works | A config file lists prompts, providers (models) and tests with assertions; `promptfoo eval` runs every test on every provider; `promptfoo view` opens a web viewer with a side-by-side matrix | https://www.promptfoo.dev/docs/getting-started/ ; https://www.promptfoo.dev/docs/intro/ |
| Use 1: compare models | "Compare models side-by-side (OpenAI, Anthropic, Azure, Bedrock, Ollama, and more)". The getting-started example runs two OpenAI models on two translation tests with `contains` / `icontains` checks: "Both models run each test, producing four results." | README; https://github.com/promptfoo/promptfoo/tree/main/examples/getting-started |
| Use 2: red teaming | "Automatically scans 50+ vulnerability types": jailbreaks, injections, RAG poisoning and more. `promptfoo redteam run` "will generate several hundred adversarial inputs … Then, it will run the test cases against the target"; the report shows vulnerability categories, severity, logs and suggested mitigations | https://www.promptfoo.dev/docs/red-team/quickstart/ |
| Use 3: CI/CD | "Catch regressions early: Test prompt changes before they reach production"; `npx promptfoo@latest eval --fail-on-error` fails the build on test failures; GitHub Action, GitLab CI, Jenkins and others | https://www.promptfoo.dev/docs/integrations/ci-cd/ |
| Model-graded checks | `llm-rubric` assertions let another model grade free-form answers | https://www.promptfoo.dev/docs/getting-started/ |
| Catch: cost | Every test calls the configured provider. "Cost and latency assertions check completed responses; they do not cap spending or stop slow requests." | https://www.promptfoo.dev/docs/getting-started/ |
| Catch: remote generation | "By default, promptfoo uses a remote service for generating adversarial inputs." It can be switched off with `PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION=true`, but "Disabling remote generation may result in lower quality adversarial inputs." Red-team attack generation also uses a separate provider (OpenAI by default) | https://www.promptfoo.dev/docs/red-team/configuration/ (Remote Generation); red-team quickstart |
| Catch: free vs paid | The Enterprise comparison table marks Red Teaming, Remediations, Result Sharing and API Access as "Limited" in Community; Team Management, RBAC, external integrations and SLA are Enterprise only | https://www.promptfoo.dev/docs/enterprise/ |
| Catch: telemetry | "promptfoo collects basic usage telemetry by default"; it "does not include prompts, model outputs, test cases, provider API keys"; disable with `PROMPTFOO_DISABLE_TELEMETRY=1` | https://www.promptfoo.dev/docs/configuration/telemetry/ |
| Catch: self-hosting | Evals run locally with no server. The optional self-hosted sharing server: "Self-hosting is not recommended for production use cases": local SQLite, no multi-team support or RBAC, no built-in authentication | https://www.promptfoo.dev/docs/usage/self-hosting/ |
| Requirements | Node.js `>=22.22.0`; also `brew install promptfoo` and `pip install promptfoo`, or `npx promptfoo@latest` | README; red-team quickstart |
| Quickstart | `npm install -g promptfoo`, then `promptfoo init --example getting-started`, set `OPENAI_API_KEY`, then `cd getting-started`, `promptfoo eval`, `promptfoo view` | README › Quick Start |
| Who it's not for | Watching real customer conversations after launch is tracing and monitoring (a different category); a one-off prompt that never changes doesn't need a test suite | Inferred from the docs' scope ("test-driven LLM development"), not a quote |
| Alternative (same category) | DeepEval | index.json category "Testing AI output" |

Not used (production-use claims): "Used by OpenAI and Anthropic", "Powers LLM apps serving 10M+ users in production", and the blog's user and Fortune 500 figures.

Not run locally yet. The scenes show the documented commands and features, not a recorded session.
