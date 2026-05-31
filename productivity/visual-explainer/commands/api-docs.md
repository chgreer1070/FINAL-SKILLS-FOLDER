---
description: Generate beautiful HTML API documentation — endpoint cards with method badges, request/response schemas, authentication flow diagram, error reference, and copy-ready curl examples
---
Load the visual-explainer skill, then generate comprehensive API documentation as a self-contained HTML page.

Follow the visual-explainer skill workflow. Read the reference template, CSS patterns, and mermaid theming references before generating. Use an Editorial or Blueprint aesthetic — API docs should feel authoritative and precise.

**Scope:** `$1` if provided (path to file, directory, or URL); otherwise scan the current working directory for API definitions.

**Data gathering phase** — collect API surface before generating:

1. **Detect API style:**
   - REST: look for route definitions (`router.get`, `app.post`, `@app.route`, `@Get`, `@Post`, FastAPI decorators, etc.)
   - GraphQL: look for schema files (`*.graphql`, `*.gql`), resolvers, type definitions
   - CLI: look for `commander`, `argparse`, `click`, `cobra`, `clap` usage
   - gRPC/Protobuf: look for `.proto` files
   - OpenAPI: look for `openapi.yaml`, `swagger.json`, `swagger.yaml`

2. **Extract endpoints (REST):**
   - Find all route definitions across all files
   - For each route: HTTP method, path pattern, handler function name, auth requirement (look for middleware like `authenticate`, `requireAuth`, JWT checks)
   - Read each handler to understand: what parameters it accepts (path, query, body), what it returns, what errors it throws
   - Find request validation schemas (Zod, Joi, Pydantic, class-validator, etc.)

3. **Extract types and schemas:**
   - Find request body types/interfaces
   - Find response types/interfaces
   - Find shared/common types used across endpoints

4. **Authentication and authorization:**
   - Identify auth mechanism (JWT, API key, OAuth, session cookie, basic auth)
   - Find which endpoints are public vs protected
   - Find role/permission checks

5. **Error handling:**
   - Find HTTP status codes used in error responses
   - Find error response shapes

6. **Examples:**
   - Look for test files that call the API — they often contain realistic example payloads
   - Look for example requests in comments, README, or docs directories

**Verification checkpoint** — before generating HTML, confirm:
- Every endpoint listed was found in actual code (not hallucinated from naming conventions)
- Parameter names match actual code variable names or schema field names
- Response shapes come from actual return statements or type definitions

**Diagram structure:**

1. **API overview** — name, version (from package.json/pyproject.toml), base URL (from config/env), brief description of what the API does. KPI row: total endpoint count, public vs protected count, authentication type. *Visual treatment: hero depth.*

2. **Authentication guide** — how to authenticate requests. Mermaid sequence diagram showing the auth flow (e.g., POST /login → receive token → include in Authorization header). Code block showing the exact header/parameter format. *Visual treatment: elevated card with accent-colored left border.*

3. **Endpoint reference** — the main section. Group endpoints by resource or tag. For each endpoint:
   - Method badge (GET=teal, POST=green, PUT=amber, PATCH=blue, DELETE=red) — styled `<span>` elements, not emoji
   - Path with path parameters highlighted in accent color (e.g., `/users/{id}`)
   - One-line description of what it does
   - Auth requirement badge (Public / Protected / Admin)
   - Collapsible `<details>` with:
     - **Request:** path params table, query params table, body schema table (field, type, required/optional, description)
     - **Response:** 200 success shape as a styled code block or field table; common error codes with meanings
     - **Example:** `curl` command with copy-to-clipboard button; example response JSON block

4. **Data models** — for shared types used across multiple endpoints, one card per model: field names, types, descriptions. For entities with relationships, add a Mermaid `erDiagram` or `classDiagram`.

5. **Error reference** — table of all HTTP status codes the API returns: code, description, when it occurs, how to resolve it.

6. **Quick start** — 3-5 `curl` examples showing the most common end-to-end workflows (authenticate → create → fetch → update → delete). Each in a code block with a copy-to-clipboard button. *Visual treatment: numbered flow cards.*

**Copy-to-clipboard buttons** — add to every code block containing curl commands or example payloads. See the copy-to-clipboard pattern in `./references/css-patterns.md`.

**Syntax highlighting** — if Prism.js is appropriate (code blocks with JSON, bash, TypeScript), load it via CDN. See `./references/libraries.md`.

**Visual hierarchy:** Sections 1-2 are hero/elevated (dominate on load). Section 3 is the main content body. Sections 4-6 are reference material (collapsible where long).

Include responsive section navigation. Write to `~/.agent/diagrams/` and open in browser.

Ultrathink.

$@
