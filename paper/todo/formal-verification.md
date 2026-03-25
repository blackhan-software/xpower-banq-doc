# Formal Verification Spec

## XPower Banq — Smart Contract Formal Verification Plan

---

## 1. Problem Statement

XPower Banq comprises 5 core contracts (Pool, Position, Vault, Oracle, Acma) with 10 interacting mechanisms where locks affect caps, caps affect health, health affects liquidation, and liquidation interacts with oracle pricing. The Hacken audit and comprehensive Foundry test suite provide significant coverage, but audits typically find 60–80% of critical bugs, and testing can only prove the presence of bugs, not their absence. Given the protocol's complexity and the financial value at stake, formal verification is needed to provide mathematical guarantees on critical invariants.

**Goal:** Formally verify the core safety properties of XPower Banq's smart contracts, prioritizing properties where a violation would cause loss of funds.

---

## 2. Verification Scope & Prioritization

### Tier 1 — Critical (Must Verify Before Mainnet)

These properties, if violated, directly cause loss of user funds.

| ID | Property | Contract(s) | Description |
|---|---|---|---|
| P1 | Vault solvency | Vault, Pool | Total underlying assets ≥ sum of all redeemable claims |
| P2 | Health factor correctness | Pool, Position | $H(u) < 1$ iff the user's weighted borrow value exceeds weighted supply value |
| P3 | Liquidation safety | Pool, Position | Post-liquidation, the liquidator's health factor $H \geq 1$ |
| P4 | Position token conservation | Position | Total supply of position tokens = sum of all balances (no creation or destruction outside mint/burn) |
| P5 | Interest accrual monotonicity | Position | Global index $I_t$ is strictly non-decreasing over time |
| P6 | Lock irrevocability | Position | Once `lock(u, p) > 0`, it can never decrease except via transfer (which preserves the ratio) or liquidation |
| P7 | Locked redemption block | Pool, Position | `redeem()` reverts if requested amount exceeds `liquid(u, p)` |

### Tier 2 — High (Verify Before Significant TVL)

These properties, if violated, enable governance attacks or economic exploits.

| ID | Property | Contract(s) | Description |
|---|---|---|---|
| P8 | Governance rate bound | Acma, all governed | No parameter changes exceed 2× or fall below 0.5× in a single transition |
| P9 | Governance rate limiting | Acma | No two transitions on the same parameter within one governance period |
| P10 | Initial lock enforcement | Acma | Parameters cannot be changed during their initial lock period |
| P11 | Cap function correctness | Position | `cap(B, S, n)` matches Equation 3 for all inputs, including edge cases ($\lambda = 0$, $n = 0$) |
| P12 | Transfer lock proportionality | Position | `transferlock(u_1, u_2, v)` moves exactly $\lfloor \text{lock}(u_1) \cdot v / \text{balance}(u_1) \rfloor$ lock units |
| P13 | Borrow transfer semantics | Position | `transfer()` on borrow positions pulls debt from `from`, health check applies to receiver |
| P14 | Dual approval enforcement | Position | `transferFrom()` on borrow positions requires approvals from both sender and receiver |

### Tier 3 — Medium (Verify Post-Launch)

These are correctness properties that affect protocol behavior but are less likely to cause direct fund loss.

| ID | Property | Contract(s) | Description |
|---|---|---|---|
| P15 | Oracle EMA correctness | Oracle | EMA update produces $m_t = \alpha \cdot m_{t-1} + (1-\alpha) \cdot \log_2(\bar{p}_t)$ in fixed-point |
| P16 | Spread scaling correctness | Oracle | $\mu = \log_2(2x + 2)$ where $x = n \cdot s$, with correct fixed-point arithmetic |
| P17 | Rate limiter correctness | Pool | Token bucket allows operation iff $C'(t) \geq 0$ per Definition D.5 |
| P18 | PoW validation | Pool | `zeros(keccak256(...)) \geq d` is checked correctly |
| P19 | Fee accrual correctness | Vault | Entry/exit fees are computed correctly and accrue to existing depositors |
| P20 | Interest rate model | Position | $R(U)$ matches the piecewise-linear model in Definition 4.5 for all $U \in [0, 1]$ |

---

## 3. Verification Approach

### 3.1 Tool Selection

| Tool | Use Case | Strengths for XPower Banq |
|---|---|---|
| **Certora Prover** | Primary verification of Tier 1 & 2 properties | Industry-standard for DeFi; handles EVM-level reasoning; strong fixed-point arithmetic support |
| **Halmos** | Symbolic testing for arithmetic edge cases | Lightweight; integrates with existing Foundry tests; good for fixed-point overflow/underflow |
| **KEVM (K Framework)** | Deep verification of critical paths if Certora hits limits | Full EVM semantics; can verify bytecode directly; handles complex state transitions |

**Recommended primary tool: Certora Prover.** It has the broadest DeFi verification track record (Aave V3, Compound V3, Lido), handles Solidity 0.8+ patterns well, and supports the fixed-point ray arithmetic XPower Banq uses.

### 3.2 Verification Strategy Per Property

#### P1: Vault Solvency

**Invariant:** `vault.totalAssets() >= sum(redeemable(u) for all u)`

where `redeemable(u) = liquid(u, supply) * index_ratio`.

**Approach:** Certora rule checking this invariant holds before and after every external function call. Must account for:
- Interest accrual changing `redeemable` without changing `totalAssets`
- Fee accumulation narrowing the gap
- Liquidation transferring positions without moving underlying

**Known challenge:** The `totalAssets` calculation involves iterating over token balances; Certora may need loop unrolling or summarization for multi-token pools.

#### P2: Health Factor Correctness

**Invariant:** `H(u) = (Σ w_s[i] * V_s[i]) / (Σ w_b[i] * V_b[i])` computed correctly.

**Approach:** Verify that `health()` view function matches the mathematical definition for all reachable states. Key concerns:
- Fixed-point division rounding (ray precision)
- Weight normalization by WEIGHT_MAX = 255
- Averaging across $n$ tokens — verify loop correctness
- Oracle price staleness does not cause arithmetic issues (division by zero, overflow)

**Certora spec sketch:**
```
rule healthFactorCorrectness(address user) {
    uint256 computed = pool.health(user);
    uint256 expected = ghost_health(user);  // ghost function with ideal math
    assert computed == expected;
}
```

#### P3: Liquidation Safety

**Invariant:** After `square()` or `liquidate()`, `health(liquidator) >= 1`.

**Approach:** Post-condition check on all liquidation functions. Must handle:
- Partial liquidation ($2^{-e}$ fraction)
- Simultaneous transfer of supply and borrow positions
- Lock proportionality in transferred positions
- Oracle price used during health check is the same oracle price used to trigger liquidation

**Edge cases to verify:**
- Liquidator has exactly $H = 1.0$ before liquidation
- Victim has multiple tokens with different weights
- Liquidation exponent $e = 0$ (full liquidation) and $e = 255$ (minimal liquidation)

#### P4: Position Token Conservation

**Invariant:** `totalSupply() == sum(balanceOf(u) for all u)`

**Approach:** Standard ERC20 conservation rule. Additionally verify:
- `mint` increases totalSupply and recipient balance by exactly the same amount
- `burn` decreases totalSupply and holder balance by exactly the same amount
- `transfer` and `transferFrom` are zero-sum
- No function outside mint/burn modifies totalSupply

#### P5: Interest Accrual Monotonicity

**Invariant:** For consecutive updates at $t_1 < t_2$: $I(t_2) \geq I(t_1)$.

**Approach:** Verify that `refresh()` on the interest index always produces a value ≥ the previous index. Key concern: the exponential calculation $I_0 \cdot e^{r \cdot \Delta t / T_{\text{year}}}$ in ray arithmetic — verify no overflow causes wrap-around, and that the approximation used in Solidity matches the mathematical definition within acceptable error bounds.

**Halmos is well-suited here** for exhaustive symbolic testing of the fixed-point exponentiation.

#### P6: Lock Irrevocability

**Invariant:** `lock(u, p)` at time $t_2$ ≥ `lock(u, p)` at time $t_1$ for all $t_2 > t_1$ (for the same user, absent transfers out).

**Approach:** Check that no function decreases `lock` except `transfer` (which decreases sender's lock proportionally) and liquidation paths. Verify there is no `unlock` function and no admin bypass.

#### P8: Governance Rate Bound

**Invariant:** For any `setTarget(θ_new)`, assert `θ_current / 2 <= θ_new <= θ_current * 2`.

**Approach:** Direct post-condition on the `Governed` modifier or `setTarget` function. Verify the check cannot be bypassed by:
- Reentrancy during transition
- Calling `setTarget` during an active transition
- Overflow in the multiplication/division bounds check

---

## 4. Fixed-Point Arithmetic Verification

XPower Banq uses ray precision (27 decimals) and WAD precision (18 decimals). Fixed-point bugs are the most common source of DeFi exploits.

### 4.1 Operations to Verify

| Operation | Risk | Verification Target |
|---|---|---|
| Ray multiplication | Overflow at $a \cdot b > 2^{256}$ before division by $10^{27}$ | Prove no reachable state causes overflow, or that SafeMath catches it |
| Ray division | Division by zero; precision loss | Prove denominator is never zero in all call paths |
| Ray exponentiation | Approximation error accumulation | Bound the error vs. ideal $e^x$ for the range of inputs the protocol uses |
| WAD-to-ray conversion | Precision loss on conversion | Prove lossless for all values the protocol generates |
| Log2 computation | Fixed-point log2 approximation error | Bound error against ideal log2 for the oracle's operating range |
| Index ratio computation | $B_t = P \cdot I_t / I_u$ — rounding | Prove rounding always favors the protocol (rounds down for supply claims, rounds up for borrow obligations) |

### 4.2 Approach

Use **Halmos** for symbolic execution of arithmetic functions in isolation, sweeping all $2^{256}$ input combinations symbolically. For functions that are too complex for full symbolic execution, use **Certora's overapproximation** with ghost variables tracking ideal mathematical values alongside actual fixed-point results.

---

## 5. Cross-Contract Interaction Verification

The 10 interacting mechanisms create emergent behaviors that per-contract verification misses.

### 5.1 Critical Interaction Paths

| Path | Contracts | Risk |
|---|---|---|
| Supply → Lock → Cap update → Health recalc | Position → Pool | Cap change after lock could make position unhealthy |
| Oracle refresh → Health change → Liquidation trigger | Oracle → Pool → Position | Stale-to-fresh transition could trigger cascade |
| Governance param change → Interest rate shift → Index jump | Acma → Position | Large rate change during transition could cause index discontinuity |
| Borrow transfer → Health check → Liquidation | Position → Pool | Transferred debt could make receiver immediately liquidatable |
| Liquidation → Position transfer → Lock proportionality → Cap recalc | Pool → Position | Post-liquidation cap state must remain consistent |

### 5.2 Approach

Model these as Certora **multi-contract rules** with havoc on external calls. For each path:

1. Set up precondition (valid starting state)
2. Execute the sequence of operations
3. Verify all invariants still hold post-sequence

---

## 6. Edge Cases & Adversarial Scenarios

### 6.1 Numeric Edge Cases

- Zero supply (first depositor)
- Single holder ($n = 1$)
- Maximum values ($2^{224}$ cap, $2^{255}$ balances)
- Minimum decimals (6) with maximum values
- Time delta = 0 (same block operations)
- Time delta = `CENTURY` (maximum possible elapsed time)
- Utilization exactly at kink ($U = U^*$)
- Health factor exactly 1.0 (boundary condition)

### 6.2 Adversarial Scenarios

- Self-liquidation (user liquidates own position)
- Circular debt transfer (A → B → A)
- Flash loan within same block (supply + borrow + redeem)
- Governance transition mid-liquidation
- Oracle refresh during governance parameter transition
- Maximum number of tokens in pool (stress test loops)

---

## 7. Implementation Plan

### Phase 1: Setup & Tier 1 Core (Weeks 1–4)

- Week 1: Certora environment setup, contract annotation, ghost variable definitions
- Week 2: P4 (token conservation), P5 (index monotonicity), P6 (lock irrevocability) — these are the most self-contained
- Week 3: P1 (vault solvency), P2 (health factor correctness)
- Week 4: P3 (liquidation safety), P7 (locked redemption block)

### Phase 2: Tier 2 Governance & Semantics (Weeks 5–7)

- Week 5: P8, P9, P10 (governance bounds, rate limiting, initial locks)
- Week 6: P11, P12 (cap function, transfer lock proportionality)
- Week 7: P13, P14 (borrow transfer semantics, dual approval)

### Phase 3: Arithmetic & Cross-Contract (Weeks 8–10)

- Week 8: Fixed-point arithmetic verification with Halmos
- Week 9: Cross-contract interaction paths
- Week 10: Edge cases and adversarial scenarios

### Phase 4: Tier 3 & Report (Weeks 11–12)

- Week 11: P15–P20 (oracle, rate limiter, PoW, fees, interest rate model)
- Week 12: Final verification runs, counterexample analysis, report generation

---

## 8. Deliverables

| # | Deliverable | Description |
|---|---|---|
| 1 | Certora spec files | `.spec` files for all 20 properties |
| 2 | Halmos test suite | Symbolic tests for fixed-point arithmetic |
| 3 | Verification report | Per-property results: verified, counterexample found, or timeout with analysis |
| 4 | Counterexample documentation | For any failed property: root cause, exploit scenario, recommended fix |
| 5 | Assumption register | Explicit list of all assumptions made (e.g., "oracle returns nonzero", "block.timestamp increases") |
| 6 | Coverage analysis | Which functions and state transitions are covered by verified properties |
| 7 | Residual risk assessment | Properties that could not be verified within tool limits, with manual reasoning |

---

## 9. Acceptance Criteria

1. All Tier 1 properties (P1–P7) verified with no counterexamples, or counterexamples resolved via code fixes and re-verified
2. All Tier 2 properties (P8–P14) verified or documented with manual proofs where tool limits apply
3. Fixed-point arithmetic verified for all operations in the protocol's reachable input range
4. At least 3 cross-contract interaction paths verified end-to-end
5. All adversarial scenarios from Section 6.2 tested (verification or bounded model checking)
6. No known false positives in the final verification report

---

## 10. Tool-Specific Notes

### Certora

- **Prover version:** Use latest stable (currently 7.x)
- **Timeout policy:** 600 seconds per rule default; escalate to 1800 for complex multi-contract rules
- **Loop handling:** Unroll loops to the maximum number of tokens per pool (known at deployment)
- **External call handling:** Havoc for all external calls except verified protocol contracts
- **Solidity version:** Certora supports 0.8.x; verify compatibility with XPower Banq's compiler version

### Halmos

- **Integration:** Run as `forge test` with `--halmos` flag
- **Symbolic inputs:** Use `svm.createUint256()` for symbolic values
- **Counterexample extraction:** Halmos provides concrete counterexamples that can be converted to Foundry regression tests

### KEVM (If Needed)

- **Use case:** Only if Certora cannot handle specific properties due to inline assembly, complex storage patterns, or transient storage (ReentrancyGuardTransient)
- **Note:** KEVM operates on compiled bytecode, so it handles compiler-introduced artifacts that source-level tools miss