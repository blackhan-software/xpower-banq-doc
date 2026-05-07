# banq-doc-ai (Cloudflare Worker)

Proxies an Anthropic-compatible Messages API for the "Ask AI" widget on
[www.xpowerbanq.com](https://www.xpowerbanq.com). Holds the API key as a Worker
secret, embeds the docs corpus in the system prompt with prompt-cache markers,
and rate-limits per IP.

The upstream is selected by the `API_PROVIDER` var in `wrangler.toml`:
`"anthropic"` (default) routes to `api.anthropic.com` and uses the
`ANTHROPIC_API_KEY` secret; while `"deepseek"` routes to
`api.deepseek.com/anthropic` and uses the `DEEPSEEK_API_KEY` secret instead.

The `MODEL` var must be updated to match (e.g. `deepseek-v4-pro` or
`deepseek-v4-flash`). DeepSeek's compat layer silently ignores
Anthropic-specific extras like `cache_control` prompt-cache markers, so the same
request body works for either provider.

## One-time setup

```bash
cd worker && npm install
```

### Cloudflare authentication

`npx wrangler login` opens an OAuth flow with a `localhost` callback. That fails
inside a devcontainer / remote shell because the browser can't reach the
Worker's loopback port. Use an **API token** instead:

1. Create a token at <https://dash.cloudflare.com/profile/api-tokens> → **Create
   Token** → **Edit Cloudflare Workers** template (or a custom token with
   `Account: Workers Scripts: Edit`, `Account: Workers KV Storage: Edit`,
   `Zone: Workers Routes: Edit`, `User: User Details: Read`).
2. Export the token (and account ID) — wrangler picks them up automatically and
   `wrangler login` becomes unnecessary:

   ```bash
   export CLOUDFLARE_API_TOKEN=<token>
   export CLOUDFLARE_ACCOUNT_ID=<account-id> # optional, avoids prompts
   ```

   Persist across container rebuilds either via `~/.bashrc`/`~/.zshrc` inside
   the container, or by forwarding from the host in
   `.devcontainer/devcontainer.json`:

   ```json
   "remoteEnv": {
     "CLOUDFLARE_API_TOKEN":  "${localEnv:CLOUDFLARE_API_TOKEN}",
     "CLOUDFLARE_ACCOUNT_ID": "${localEnv:CLOUDFLARE_ACCOUNT_ID}"
   }
   ```

3. Verify: `npx wrangler whoami`.

### Anthropic API key

Get one from the Anthropic Console:

1. Sign in at <https://console.anthropic.com/> and open **Settings → API Keys**
   (<https://console.anthropic.com/settings/keys>).

2. **Create Key**, name it (e.g. `ai-assistant`), pick the workspace, copy the
   `sk-ant-...` value — shown only once.

3. Make sure the workspace has billing set up (**Settings → Billing**) and
   access to the Sonnet tier the Worker calls; otherwise requests return
   `credit_balance_too_low` or `permission_error`.

Rotation is atomic: `wrangler secret put` the new key, then disable the old one
in the console — the next request picks up the new value, no redeploy.

### DeepSeek API key

Skip this section if you only ever run with `API_PROVIDER=anthropic`. Otherwise
get a key from the DeepSeek Platform:

1. Sign in at <https://platform.deepseek.com/> and open the **API keys** panel
   from the left nav.

2. **Create new API key**, name it (e.g. `ai-assistant`), copy the `sk-...`
   value — shown only once.

3. DeepSeek is prepaid: top up the account balance under **Billing** before
   first use, otherwise requests fail with an insufficient-balance error.

Rotation is the same as Anthropic — `wrangler secret put DEEPSEEK_API_KEY` with
the new value, then revoke the old one in the DeepSeek console.

### Provision Worker resources

Provision the KV namespace once, then store whichever provider key(s) you plan
to use as Worker secrets (only the one matching `API_PROVIDER` is read at
request time, so a single secret is enough if you don't intend to switch):

```bash
npx wrangler kv namespace create RATELIMIT
echo -n "$ANTHROPIC_API_KEY" | npx wrangler secret put ANTHROPIC_API_KEY
echo -n "$DEEPSEEK_API_KEY"  | npx wrangler secret put DEEPSEEK_API_KEY
npx wrangler secret list # verify
```

### GitHub Actions secrets

CI (`.github/workflows/ci-worker.yml`) needs the same Cloudflare credentials —
and only those (the Worker's provider API key is already stored in Cloudflare
and read by the Worker at request time, so CI doesn't need it). Set them with
`gh`:

```bash
echo -n "$CLOUDFLARE_API_TOKEN"  | gh secret set CLOUDFLARE_API_TOKEN
echo -n "$CLOUDFLARE_ACCOUNT_ID" | gh secret set CLOUDFLARE_ACCOUNT_ID
gh secret list # verify
```

`echo -n` avoids appending a newline that would become part of the secret. Add
`--repo OWNER/REPO`, `--env <name>`, or
`--org <org> --visibility selected --repos a,b` to scope to a repo, environment,
or org.

## Development

Export the provider API key(s) into your shell — `npm run dev` forwards them
into the local worker as bindings via `scripts/ai-worker-dev/index.mjs`
(wrangler itself does not auto-read these env vars). Only the key matching
`wrangler.toml`'s `API_PROVIDER` is consulted at request time, so an unset value
for the other provider is fine.

```bash
export ANTHROPIC_API_KEY=sk-ant-... # for API_PROVIDER=anthropic
export DEEPSEEK_API_KEY=sk-...      # for API_PROVIDER=deepseek
npm run dev                         # http://localhost:8787
```

`wrangler dev` runs the `[build]` step, which regenerates `source/ai-corpus.md`
from the current `content/` tree.

## Deployment

```bash
npm run deploy
```

CI (`.github/workflows/ci-worker.yml`) deploys automatically when `worker/**` or
`content/**` change on `main`, using the `CLOUDFLARE_API_TOKEN` /
`CLOUDFLARE_ACCOUNT_ID` GitHub secrets above.

## Copyright

© 2026 [Moorhead LLC](#)
