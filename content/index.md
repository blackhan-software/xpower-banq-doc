---
layout: home
hero:
  actions:
    - theme: brand
      text: Read the Whitepaper
      link: /whitepaper/01-introduction
    - theme: alt
      text: Mathematical Theory
      link: /theory/01-mathematical-foundations
features:
  - title: Locked Positions
    details: Optional position locks attenuate liquidation cascades by factor (1−φ); 16-slot quarterly ring buffer with O(1) cached depth
    link: /timelocks/01-introduction
  - title: Lethargic Governance
    details: Time-weighted parameter transitions bounded by 0.5×–2× per cycle, preventing governance shocks
    link: /whitepaper/06-governance
  - title: Beta-Distributed Caps
    details: Position caps 12λ(1−λ)²/√(n+2) rate-limit capacity accumulation to O(√k) for k accounts
    link: /whitepaper/04-mechanisms#beta-distributed-position-caps
  - title: Debt Assumption Liquidation
    details: Transferable debt positions with inverted ERC20 semantics — liquidators assume debt instead of supplying capital
    link: /whitepaper/04-mechanisms#health-factor-and-liquidation
  - title: Log-Space TWAP Oracle
    details: Geometric mean temporal averaging with bidirectional spread computation; resists flash-loan manipulation
    link: /whitepaper/04-mechanisms#oracle-twap
  - title: Log-Space Compounding Index
    details: Additive log-space accrual eliminates overflow (≥5×10⁵ years vs. ~29 for multiplicative) with net gas savings
    link: /logspace/01-introduction
---
