---
title: "6. Governance & Parameters"
prev:
  text: "5. Anti-Spam Protection"
  link: /whitepaper/05-anti-spam
next:
  text: "7. Security Analysis"
  link: /whitepaper/07-security
---

All protocol parameters are governed via the [lethargic transition mechanism](/whitepaper/04-mechanisms#lethargic-governance). They are organized into four contract domains: **Pool** (rate limits, PoW difficulty, health weights), **Position** (interest rate model, caps), **Oracle** (TWAP behavior, feed management), and **Vault** (entry/exit fees). Full parameter tables and role categories appear in the [Reference: Parameters](/reference/parameters) page.

::: theorem
**Theorem 2** (Governance Rate Bound). *Under multiplicative bound $\mu = 2$ and minimum cycle $\Delta t_{\min}$, the parameter at time $t$ satisfies*

$$\mu^{-n} \theta_0 \leq \theta(t) \leq \mu^n \theta_0$$

*where $n = \lfloor(t{-}t_0)/\Delta t_{\min}\rfloor$. A $10\times$ change requires $\lceil\log_2 10\rceil = 4$ months.*
:::

The protocol implements a three-tier role hierarchy per governable function: an **executor** (who calls the function), an **admin** (who grants and revokes the executor role), and a **guard** (who provides veto-only revocation). Guard roles serve as a "break glass" mechanism, allowing emergency halts of malicious actions without granting execution power. The governance rate bound proof is provided in [Theory: Formal Proofs](/theory/02-formal-proofs).
