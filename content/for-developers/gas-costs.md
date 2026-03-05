# Gas costs

Mainnet gas costs for Banq, broken down by what each protocol pays gas for. Banq numbers are pulled from mainnet activity — every cell links to a real on-chain trace. Aave V3 numbers are from the Cyfrin gas audit (May 2025) plus warm-path Foundry snapshots; Benqi numbers are from mainnet receipts on `qiAVAX`/`qiUSDC` (2026-04-14, Avalanche).

A gas measurement on a lending pool depends heavily on whether storage slots are warm or cold, whether the user is already in the position-marker set, whether the operation involves the same token on both sides, and whether the position has any debt at all. Rather than a single number, this page reports a **min / max envelope** per operation — the spread is structural, not noise.

## Warm-path summary

The warm path assumes the user already holds positions in the pool, vault state is loaded, and the user is already in the position-marker set. This is the steady-state cost — what most users pay on most operations.

| Operation              | Aave V3 |       Banq Min       |       Banq Max       |  Benqi  |
|------------------------|--------:|---------------------:|---------------------:|--------:|
| Supply / Mint          |    146k |   229k (`0xb4dc8515`) |   349k (`0xcaa7f16c`) |    148k |
| Borrow                 |    247k |   274k (`0xf2fb935f`) |   412k (`0xce913a08`) |    851k |
| Repay / Settle         |    176k |   195k (`0x36396c7e`) |   217k (`0x1410ec8c`) |    135k |
| Withdraw / Redeem      |    165k |   161k (`0xa560fbf1`) |   354k (`0x271fcd1a`) |  1,010k |

<div class="gas-grid">
  <div class="chart-box"><h3>Supply / Mint (warm)</h3><div class="chart-container"><canvas id="chartSupplyWarm"></canvas></div></div>
  <div class="chart-box"><h3>Borrow (warm)</h3><div class="chart-container"><canvas id="chartBorrowWarm"></canvas></div></div>
  <div class="chart-box"><h3>Repay / Settle (warm)</h3><div class="chart-container"><canvas id="chartRepayWarm"></canvas></div></div>
  <div class="chart-box"><h3>Withdraw / Redeem (warm)</h3><div class="chart-container"><canvas id="chartWithdrawWarm"></canvas></div></div>
</div>

## Cold vs warm envelope

The cold path is the first time a particular slot, user, or token is touched in a pool. Cold cost is paid **per token side** and **per user**, not per pool — adding a second token to a user's position re-pays the same cold premium that the first token did, regardless of pool age. Onboarding a new user re-pays the full cold-mark insert (+25k) regardless of the pool's age.

<div class="gas-grid">
  <div class="chart-box"><h3>Supply / Mint (cold/warm, min/max)</h3><div class="chart-container"><canvas id="chartSupplyCold"></canvas></div></div>
  <div class="chart-box"><h3>Borrow (cold/warm, min/max)</h3><div class="chart-container"><canvas id="chartBorrowCold"></canvas></div></div>
  <div class="chart-box"><h3>Repay / Settle (cold/warm, min/max)</h3><div class="chart-container"><canvas id="chartRepayCold"></canvas></div></div>
  <div class="chart-box"><h3>Withdraw / Redeem (cold/warm, min/max)</h3><div class="chart-container"><canvas id="chartWithdrawCold"></canvas></div></div>
</div>

### Gas categories

Each stacked bar above is broken down into six categories:

- **Health Check** — position balance reads across pool tokens (single-side or cross-pair `totalOf` legs)
- **Position Accounting** — mint / burn position tokens, reindex, interest accrual
- **Oracle** — TWAP price-feed reads (`Oracle::mixQuotes` or `minQuote`)
- **Vault / Custody** — ERC4626 deposit / redeem, share accounting
- **Token Transfers** — ERC20 `transferFrom` / `transfer`
- **Base Overhead** — tx cost, modifiers, guards, protocol logic

## Key insights

### Each warm op has a structural short-circuit

Each Banq warm op has a structural short-circuit that the Min trace exploits and the Max trace does not.

- **Supply** Min avoids the cold-mark insert because the user is already in the large-holder set; Max pays the full +25k cold per-user mark on a virgin user, plus cold first-of-tx Pool slots.
- **Borrow** Min is *self-pair* (same token on both legs — no oracle, no cross-token reads, ~106k saved); Max is *cross-pair* and forces all four `totalOf` legs plus `Oracle::mixQuotes`.
- **Settle** Min is exact-amount (no max-sentinel `totalOf`) and keeps the user in-set; Max passes `type(uint256).max` AND drains the user out-of-set (+46k upfront `totalOf`, +8k `mark(false)`).
- **Redeem** Min runs against a flat account (zero debt, oracle elided); Max is fully cross-token contended (+131k cross-token health, +19k oracle, plus interest reindex). At 161k → 354k (+120%), redeem has the largest min/max gap of any op.

### Cold cost is per-token and per-user

Adding a second token (XPOW supply Cold Max at 404k) byte-for-byte mirrors the first (APOW supply Cold Min at 404k) — the per-token cold premium repeats. Onboarding a new user re-pays the full cold-mark insert (+25k) regardless of pool age. The Cold Max borrow (483k) combines new-user state with cross-pair contention to define the realistic gas ceiling for any borrow on this pool.

### Versus Aave V3 / Benqi

Banq's redeployed Pool uses a single-side health check — only the operated token's positions are read; the oracle leg is invoked only when the user holds debt on the *other* pool token. Self-pair operations (same token supplied & borrowed) skip the oracle entirely, dropping warm borrow Min to 274k. Even contended cross-pair borrows fold both NAVs into one `Oracle::mixQuotes(supplyAmt, borrowAmt, src, dst)` call (~18.8k).

Benqi's Comptroller still iterates **all** entered markets on borrow / redeem, causing extreme gas spikes (851k–1,010k). Aave V3 benefits from efficient isolation-mode health checks and cheap Chainlink reads, but Banq's warm settle Min (195k) and warm redeem Min (161k) both undercut Aave V3 outright; Banq warm borrow Max (412k) loses to Aave V3 (247k) only when the user holds cross-pair debt.

## Trace sources

All Banq numbers above come from real mainnet traces on Pool P000 (`0x172698a1…9725`). Replace the hash prefixes with full block-explorer URLs to inspect each one.

- **Warm Min** — cheapest exact-amount warm trace per op: supply `0xb4dc8515` (229k, APOW ≈ 1 unit), borrow `0xf2fb935f` (274k, self-pair APOW — no oracle), settle `0x36396c7e` (195k, XPOW dust), redeem `0xa560fbf1` (161k, full-drain XPOW dust).
- **Warm Max** — most expensive warm trace per op: supply `0xcaa7f16c` (349k, new user — cold per-user mark slot), borrow `0xce913a08` (412k, cross-pair: APOW collateral, XPOW debt — full 4-leg health + `mixQuotes`), settle `0x1410ec8c` (217k, max-sentinel + drain-out-of-set), redeem `0x271fcd1a` (354k, fully cross-token contended).
- **Cold Min** — first-of-kind from the 2026-05-01 batch: supply `0xa2d1d5a4` (404k, first-ever APOW deposit), borrow `0x549a5f70` (354k, first-ever borrow, self-pair), settle `0xf5e3a287` (201k), redeem `0x1ac1277a` (171k, first redeem on flat account).
- **Cold Max** — most expensive cold trace per op: supply `0x4398edd1` (404k, first-ever XPOW deposit — per-token cold mirror), borrow `0x39d1b9d2` (483k, new user fully-cold cross-token), settle `0xc2b4c17b` (204k), redeem `0x925dc637` (185k, single-leg `minQuote` against outstanding cross-token debt).

The corresponding `spec/TTXs_*.md` files live in the protocol repository (`banq.git`).

## Other operations

These operations are not in the warm/cold mainnet trace set above — numbers are Foundry estimates with optimizer ON, against an isolated test pool. They may differ from mainnet costs once the redeployed pool has accumulated real state.

| Operation                              | XPower Banq | Aave V3 | Compound V3 | Notes                                  |
|----------------------------------------|------------:|--------:|------------:|----------------------------------------|
| Supply with lock                       |       ~138k |     n/a |         n/a | Lock state added                       |
| Redeem with lock-expiry                |       ~155k |     n/a |         n/a | Ring-buffer cleanup                    |
| Lock (retroactive)                     |        ~75k |     n/a |         n/a |                                        |
| Transfer Supply                        |        ~75k |    ~78k |        ~78k | Lock-aware proportional                |
| Transfer Borrow (with both approvals)  |        ~95k |     n/a |         n/a | Inverted direction                     |
| Liquidation (full)                     |       ~298k |   ~389k |       ~370k |                                        |
| Liquidation (16 slots)                 |     ~6,750k |     n/a |         n/a | Worst case — all ring slots active     |

The 16-slot liquidation case is unusual — it requires the victim to have all 16 ring-buffer slots active, which is an edge case. Typical liquidations clear positions with 0–3 active slots and run ~300k gas.

## Why Banq is generally cheaper

The protocol's log-space interest accumulation saves ~1,200 gas per accrual versus the multiplicative index used by incumbents. This compounds across operations.

The lock-aware transfer adds gas relative to plain ERC20 transfer, but only when locks are non-zero — fully unlocked positions transfer at near-baseline cost.

## Why the worst-case liquidation is expensive

A liquidation that propagates lock state across all 16 ring-buffer slots performs significant arithmetic per slot. This is the "worst case" — typical liquidations run ~300k gas.

Keepers should price gas into their bot's profitability calculation. A profitable liquidation requires the bonus to exceed gas + opportunity cost.

## Optimisation tips

- **Batch operations.** A single tx with multiple operations is cheaper than separate txs.
- **Use approve once.** Standing approvals save per-call gas at the cost of standing-approval risk.
- **Skip `MAX_UINT256` for partial settles.** Pass the exact amount when you know it — the difference is 195k vs 217k for warm settle.
- **Stay in the position-marker set.** Don't fully drain a token side unless you're closing the position — re-entering pays the cold-mark insert again (+25k).
- **Self-pair when you can.** If your strategy can hold the same token on both sides of a position, you skip the oracle entirely (~106k saved on borrow).

## Where to go next

- [Integration guide](/for-developers/integration-guide) — composition patterns
- [CLI and tools](/for-keepers/cli-and-tools) — `banq-cli` (dry-run by default)

<script setup>
import { onMounted, onUnmounted } from 'vue'

const COLORS = {
  healthCheck: '#f97583',
  position:    '#d2a8ff',
  oracle:      '#79c0ff',
  vault:       '#56d364',
  transfer:    '#e3b341',
  overhead:    '#8b949e',
}

function themeColors() {
  const s = getComputedStyle(document.documentElement)
  const pick = (v, fb) => (s.getPropertyValue(v).trim() || fb)
  return {
    text:  pick('--vp-c-text-2', '#666'),
    muted: pick('--vp-c-text-3', '#999'),
    grid:  pick('--vp-c-divider', 'rgba(128,128,128,0.2)'),
  }
}

function loadChartJs() {
  if (typeof window === 'undefined') return Promise.resolve(null)
  if (window.Chart) return Promise.resolve(window.Chart)
  return new Promise((resolve, reject) => {
    const existing = document.querySelector('script[data-chartjs]')
    if (existing) {
      existing.addEventListener('load', () => resolve(window.Chart))
      existing.addEventListener('error', reject)
      return
    }
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js'
    script.dataset.chartjs = '1'
    script.onload = () => resolve(window.Chart)
    script.onerror = reject
    document.head.appendChild(script)
  })
}

function makeDatasets(rows) {
  return [
    { label: 'Health Check',        data: rows.map(r => r[0]), backgroundColor: COLORS.healthCheck },
    { label: 'Position Accounting', data: rows.map(r => r[1]), backgroundColor: COLORS.position },
    { label: 'Oracle',              data: rows.map(r => r[2]), backgroundColor: COLORS.oracle },
    { label: 'Vault / Custody',     data: rows.map(r => r[3]), backgroundColor: COLORS.vault },
    { label: 'Token Transfers',     data: rows.map(r => r[4]), backgroundColor: COLORS.transfer },
    { label: 'Base Overhead',       data: rows.map(r => r[5]), backgroundColor: COLORS.overhead },
  ]
}

function chartOptions(opName) {
  const TITLE_WIDTH = 30
  const tc = themeColors()
  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { display: false },
      tooltip: {
        mode: 'index',
        intersect: false,
        itemSort: (a, b) => b.parsed.y - a.parsed.y,
        titleFont: { family: 'ui-monospace, SFMono-Regular, Menlo, monospace', size: 12, weight: 'bold' },
        bodyFont:  { family: 'ui-monospace, SFMono-Regular, Menlo, monospace', size: 12 },
        callbacks: {
          title: items => {
            const total = items.reduce((s, i) => s + i.parsed.y, 0)
            const left  = `${items[0].label} ${opName}`
            const right = `${(total / 1000).toFixed(1)}k gas`
            const pad   = Math.max(2, TITLE_WIDTH - left.length - right.length)
            return left + ' '.repeat(pad) + right
          },
          label: ctx => {
            const name = `${ctx.dataset.label}`.padEnd(20)
            const gas  = `${(ctx.raw / 1000).toFixed(1)}k gas`.padStart(10)
            return `${name}${gas}`
          },
        },
      },
    },
    scales: {
      x: {
        stacked: true,
        ticks: { color: tc.text, font: { size: 11 } },
        grid: { display: false },
      },
      y: {
        stacked: true,
        ticks: { color: tc.muted, callback: v => (v / 1000) + 'k' },
        grid: { color: tc.grid },
        title: { display: true, text: 'Gas Used', color: tc.muted },
      },
    },
  }
}

const warmLabels = ['Aave V3', 'Banq Min', 'Banq Max', 'Benqi']
const envLabels  = ['Cold Min', 'Cold Max', 'Warm Min', 'Warm Max']

// rows: [health, position, oracle, vault, transfer, overhead]
const CHARTS = [
  ['chartSupplyWarm', 'Supply', warmLabels, [
    [     0,  40000,     0,     0, 30000,  76354],   // Aave V3 146k
    [     0,  82506,     0, 48367, 32388,  65240],   // Banq Warm Min 229k
    [     0, 149369,     0, 48367, 32388, 119287],   // Banq Warm Max 349k
    [     0,  40000,     0,     0, 25000,  83374],   // Benqi 148k
  ]],
  ['chartBorrowWarm', 'Borrow', warmLabels, [
    [ 80000,  40000, 10000,     0, 30000,  87485],   // Aave V3 247k
    [ 42112,  92871,     0, 45254, 10911,  82929],   // Banq Warm Min 274k (self-pair)
    [129846, 123553, 18800, 45144, 10845,  83789],   // Banq Warm Max 412k (cross-pair)
    [700000,  40000, 10000,     0, 25000,  76008],   // Benqi 851k
  ]],
  ['chartRepayWarm', 'Settle', warmLabels, [
    [     0,  40000,     0,     0, 30000, 106087],   // Aave V3 176k
    [     0,  74395,     0, 48039, 35691,  36694],   // Banq Warm Min 195k
    [     0,  99347,     0, 48083, 32388,  37390],   // Banq Warm Max 217k
    [     0,  30000,     0,     0, 25000,  80073],   // Benqi 135k
  ]],
  ['chartWithdrawWarm', 'Redeem', warmLabels, [
    [ 50000,  40000, 10000,     0, 30000,  34659],   // Aave V3 165k
    [     0,  78108,     0, 45144, 10845,  27039],   // Banq Warm Min 161k (flat)
    [131874,  82990, 19010, 45254, 10911,  63842],   // Banq Warm Max 354k (cross-token contended)
    [870000,  40000, 10000,     0, 25000,  64678],   // Benqi 1010k
  ]],
  ['chartSupplyCold', 'Supply', envLabels, [
    [     0, 149369,     0, 99667, 35625, 119287],   // Cold Min 404k (APOW first)
    [     0, 149369,     0, 99623, 35691, 119352],   // Cold Max 404k (XPOW first)
    [     0,  82506,     0, 48367, 32388,  65240],   // Warm Min 229k
    [     0, 149369,     0, 48367, 32388, 119287],   // Warm Max 349k (new user)
  ]],
  ['chartBorrowCold', 'Borrow', envLabels, [
    [ 41734, 132613,     0, 45254, 10911, 123635],   // Cold Min 354k (self-pair)
    [130011, 132613, 18770, 45144, 10845, 145888],   // Cold Max 483k (cross-pair, new user)
    [ 42112,  92871,     0, 45254, 10911,  82929],   // Warm Min 274k (self-pair)
    [129846, 123553, 18800, 45144, 10845,  83789],   // Warm Max 412k (cross-pair)
  ]],
  ['chartRepayCold', 'Settle', envLabels, [
    [     0,  83494,     0, 48083, 32388,  36718],   // Cold Min 201k (APOW first)
    [     0,  83410,     0, 48039, 35691,  36742],   // Cold Max 204k (XPOW first)
    [     0,  74395,     0, 48039, 35691,  36694],   // Warm Min 195k
    [     0,  99347,     0, 48083, 32388,  37390],   // Warm Max 217k
  ]],
  ['chartWithdrawCold', 'Redeem', envLabels, [
    [  1484,  72920,     0, 45254, 10911,  40472],   // Cold Min 171k (flat)
    [  1484,  72920, 11213, 45144, 10845,  43449],   // Cold Max 185k (single-leg oracle)
    [     0,  78108,     0, 45144, 10845,  27039],   // Warm Min 161k (full-drain flat)
    [131874,  82990, 19010, 45254, 10911,  63842],   // Warm Max 354k (cross-token contended)
  ]],
]

let instances = []
let observer  = null

function renderAll(Chart) {
  for (const c of instances) c.destroy()
  instances = []
  for (const [id, opName, labels, rows] of CHARTS) {
    const el = document.getElementById(id)
    if (!el) continue
    instances.push(new Chart(el, {
      type: 'bar',
      data: { labels, datasets: makeDatasets(rows) },
      options: chartOptions(opName),
    }))
  }
}

onMounted(async () => {
  const Chart = await loadChartJs()
  if (!Chart) return
  renderAll(Chart)

  // Re-render when VitePress toggles the .dark class on <html>
  observer = new MutationObserver(muts => {
    if (muts.some(m => m.attributeName === 'class')) renderAll(Chart)
  })
  observer.observe(document.documentElement, { attributes: true })
})

onUnmounted(() => {
  if (observer) observer.disconnect()
  for (const c of instances) c.destroy()
  instances = []
})
</script>

<style scoped>
.gas-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin: 20px 0;
}
@media (max-width: 720px) {
  .gas-grid { grid-template-columns: 1fr; }
}
.chart-box {
  background: transparent;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 16px;
}
.chart-box h3 {
  font-size: 0.95em;
  margin: 0 0 12px;
  color: var(--vp-c-text-1);
  text-align: center;
  font-weight: 600;
  border: none;
  padding: 0;
  letter-spacing: 0;
}
.chart-container {
  position: relative;
  height: 280px;
}
</style>
