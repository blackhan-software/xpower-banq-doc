---
layout: home
hero:
  actions:
    - theme: brand
      text: Read the Whitepaper
      link: /whitepaper/01-introduction
    - theme: alt
      text: Technical Appendices
      link: /appendices/part-i-math/mathematical-foundations
features:
  - title: Lethargic Governance
    details: Time-weighted parameter transitions bounded by 0.5×–2× per cycle
    link: /whitepaper/04-mechanisms#lethargic-governance
  - title: Beta-Distributed Caps
    details: Position caps with holder-count scaling that rate-limits capacity accumulation
    link: /whitepaper/04-mechanisms#beta-distributed-position-caps
  - title: Debt Assumption Liquidation
    details: Transferable debt positions with inverted ERC20 semantics
    link: /whitepaper/04-mechanisms#health-factor-and-liquidation
  - title: Log-Space TWAP Oracle
    details: Geometric mean temporal averaging with bidirectional spread computation
    link: /whitepaper/04-mechanisms#oracle-twap
  - title: Conservative Defaults
    details: 33% LTV with 200% over-collateralization buffer
    link: /whitepaper/07-security
  - title: Ring-Buffer Time Locks
    details: 16-slot quarterly ring buffer with O(1) cached depth via algebraic identity D = ΣQ − Tt + pL
    link: /timelocks/01-introduction
---
