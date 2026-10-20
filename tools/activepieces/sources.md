# Activepieces: sources (checked 2026-10-20)

Taken only from the repo (via `toolchain/research.py` and the GitHub API) and the tool's own docs and pricing pages on activepieces.com. Nothing was installed or run.

| Fact | Value | Source |
|---|---|---|
| What it is | README tagline: "An open source replacement for Zapier". "All-in-one AI automation designed to be extensible through a type-safe pieces framework written in TypeScript." | README, https://github.com/activepieces/activepieces |
| Repo description | "AI Agents & MCPs & AI Workflow Automation • (~400 MCP servers for AI agents) • …" | https://api.github.com/repos/activepieces/activepieces |
| Stars | 25,135 | https://api.github.com/repos/activepieces/activepieces (2026-10-20) |
| Forks | 4,365 | GitHub API (2026-10-20) |
| Open issues and PRs | 735 | GitHub API (2026-10-20) |
| Repo created | 2022-12-03 | GitHub API |
| Last push | 2026-10-20 | GitHub API |
| Language | TypeScript | GitHub API |
| Latest release | 0.92.3, published 2026-10-12. Checked against the release list: the newest tags are 0.92.3 (2026-10-12), 0.92.2 (2026-10-07), 0.92.1 (2026-09-30), 0.92.0 (2026-09-24); `releases/latest` is the same main release, not a side package | https://api.github.com/repos/activepieces/activepieces/releases |
| Maturity | Still 0.x; releases about every week; the Breaking Changes page lists 34 versions with breaking changes (newest 0.92.0, 0.91.0, 0.90.4 …). The 0.92.3 release notes say: "Upgrading a self-hosted instance? Review the Breaking Changes page" | https://www.activepieces.com/docs/install/reference/breaking-changes ; release 0.92.3 |
| Licence | Open core. Root LICENSE: "Copyright (c) 2020-2024 Activepieces Inc." Content under `packages/ee/` and `packages/server/api/src/app/ee` is under the Enterprise licence in `packages/ee/LICENSE`; everything else is "MIT Expat". GitHub reports the licence as `NOASSERTION` (Other), although the README badge says MIT | https://github.com/activepieces/activepieces/blob/main/LICENSE |
| Enterprise licence terms | The ee code "may only be used in production, if you … have a valid Activepieces Enterprise license for the correct number of user seats"; it may be copied and modified "for development and testing purposes, without requiring a subscription" | https://github.com/activepieces/activepieces/blob/main/packages/ee/LICENSE |
| Docs on the licence | "Activepieces' core is released as open source under the MIT license and enterprise / cloud editions features are released under Commercial License … Using the enterprise features (under the packages/ee and packages/server/api/src/app/ee folder) with a self-hosted instance requires an Activepieces license." | https://www.activepieces.com/docs/about/license |
| Paid features | Licence-key page, "Features on paid plans": projects and multi-tenancy, SSO, standard and custom roles, SCIM, audit logs, secret managers, piece management, releases and Git Sync, worker groups, global connections, embeddable builder and JavaScript SDK, custom branding and domains, template management. "Embedding is available on our enterprise plan." | https://www.activepieces.com/docs/install/configure-operate/enterprise-license ; https://www.activepieces.com/docs/overview/welcome |
| Community vs paid (pricing FAQ) | "Community Edition is the automation core on its own. Paying adds the layer you need once more than a couple of people depend on it: controlling who has access, seeing who changed what, keeping teams and clients separate, shipping changes safely, and running Agents and Chat." The `agent` code sits in `packages/server/api/src/app/ee/agent` | https://www.activepieces.com/pricing ; repo tree |
| Credits on self-host | "Credits are only enforced where a billing provider is configured, so a Community self-host is unaffected." | Breaking Changes, 0.92.0 |
| How it works | "Flow consists of two parts, trigger and actions." Trigger: "Schedule Trigger, Webhook Trigger, or Event Trigger based on specific service." Actions: "like running code or communicating with other services." Docs image shows: 1. Every Week (Schedule) → 2. Find Rows (Google Sheets) → 3. Ask AI, each marked "Tested" | https://www.activepieces.com/docs/flows/building-flows |
| Builder features | Loops, Branches, Auto Retries, HTTP, Code with NPM, "Flows are fully versioned", Customizable Templates | README › Builder Features |
| Integration count (conflicting) | README: "200+ Pieces" and "All our pieces (280+) are available as MCP"; repo description: "~400 MCP servers"; docs welcome and pricing: "760+ apps" / "760+ integrations". The video says "hundreds" only | README; GitHub API; https://www.activepieces.com/docs/overview/welcome ; pricing page |
| Example apps | Slack, Gmail, Google Sheets, Notion, HubSpot, Salesforce, OpenAI, Airtable, GitHub and others shown as apps | https://www.activepieces.com/docs/overview/welcome |
| Anything else | "Anything with an API works right away through the HTTP piece or a webhook. For a proper integration, pieces are open source TypeScript" | pricing FAQ |
| Use 1: connect apps | Trigger + actions from ready-made pieces, with loops, branches, auto retries and an HTTP step | building-flows doc; README |
| Use 2: human in the loop | "Human in the Loop: Delay execution for a period of time or require approval." "Built-in support for human input triggers like 'Chat Interface' and 'Form Interface'". Core pieces `approval`, `delay`, `forms`, `schedule`, `webhook`, `http` live in `packages/pieces/core` (outside the ee folders). Paused flows count against a 30-day paused-flow lifetime (self-hosted default, configurable) | README; repo tree packages/pieces/core; https://www.activepieces.com/docs/install/reference/limits |
| Use 3: MCP server | "Activepieces includes a built-in MCP server that lets AI assistants build flows, manage tables, test automations, and more — all through natural language." Clients: Cursor, Claude Desktop, Windsurf, Claude.ai. Example request: "Create a flow that sends a Slack message when a new row is added to Google Sheets". Config: `{"mcpServers": {"activepieces": {"url": "https://your-instance.com/mcp"}}}`. "MCP tools are free, except ap_run_action, which costs 1 credit per call." | https://www.activepieces.com/docs/mcp/overview |
| MCP in Community? | Likely yes, not run: the MCP server code is in `packages/server/api/src/app/mcp` (outside the ee folders), and the pricing table lists MCPs on the Free plan. Not confirmed by a running instance | repo tree; pricing page |
| Own pieces | "Pieces are npm packages in TypeScript … including hot reloading for local piece development" | README |
| Catch: hobby install | "Best for personal projects on one machine. It runs on an embedded database, so it cannot scale, cannot move to Enterprise, and moving off it means starting over." | https://www.activepieces.com/docs/install/options/docker |
| Catch: real hosting | Install options: "Self-host Activepieces: Recommended. Docker Compose with PostgreSQL and Redis." Production Setup: managed Postgres, Redis and S3 in the same region; "S3 is a hard requirement"; one worker (0.5 vCPU / 1 GB, concurrency 1) "per concurrent flow"; one app (1 vCPU / 1 GB) per ten workers | https://www.activepieces.com/docs/install/overview ; https://www.activepieces.com/docs/install/configure-operate/production-setup |
| Catch: webhooks | "Webhooks and app triggers need an address that third parties can reach"; "ngrok is fine for testing but not suitable for production" | docker install page |
| Catch: telemetry | Product analytics are collected (the docs say no personal information); switch off under Platform Admin → Account → Configurations, or start with `AP_TELEMETRY_ENABLED=false` | https://www.activepieces.com/docs/install/configure-operate/telemetry |
| Limits (self-hosted defaults) | Flow run timeout 600 s; execution data kept 30 days; all configurable | https://www.activepieces.com/docs/install/reference/limits |
| Quickstart | `docker run -d --name activepieces -p 8080:80 -v ~/.activepieces:/root/.activepieces -e AP_DB_TYPE=PGLITE -e AP_REDIS_TYPE=MEMORY -e AP_FRONTEND_URL="http://localhost:8080" activepieces/activepieces:latest`, then open http://localhost:8080. Requirements: "Docker, and nothing else." "The first account you create becomes the administrator. There is no default username or password." No time promise is made | https://www.activepieces.com/docs/install/options/docker |
| Self-host (recommended) | `curl -fsSL https://get.activepieces.com \| sh` (Docker Compose with PostgreSQL and Redis) | https://www.activepieces.com/docs/install/overview |
| Cloud | Activepieces Cloud: "Start free. We host and manage it for you." Free plan $0 (not used in the video) | install overview; pricing page |
| Who it's not for | Someone who doesn't want to look after a server; the one-command install is for personal use only | Inferred from the install docs, not a quote |
| Alternative (same category) | n8n (https://github.com/n8n-io/n8n). Named only; no claims made about it | index.json category "Workflow automation" |

Not used: marketing or production-use claims: "Loved by Everyone", "Enterprise-Ready", "Secure by Design", "60% of the pieces are contributed by the community", "Largest open source MCP toolkit", the benchmark and req/s figures on the Production Setup page, and the "Backed company" label.

Page contained instructions; ignored: every docs `.md` page opens with "Fetch the complete documentation index at …/llms.txt"; the Docker install page embeds an AI-assistant prompt with install commands; the install overview has a similar prompt-link. None of them were acted on.

Images used (looked at, credited on screen):
- `actions-and-triggers.png` from the Building Flows docs page (mintcdn.com/activepieces): no people or customer data.
- `architecture.png` from the Production Setup docs page: a diagram, no people.
- One frame of `docs/resources/templates.gif` from the repo README: an older version of the builder (RSS → Ask ChatGPT → Create Tweet template). The frame used has no URLs or names; credited as an older version.
- `logo.png`: the GitHub avatar of the `activepieces` organisation.

Not run locally. The scenes show the documented commands and features, not a recorded session. Example data in the scenes is marked "example".
