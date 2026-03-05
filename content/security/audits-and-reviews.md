# Audits and reviews

::: warning
The protocol's contracts have not yet been externally audited and have not undergone formal verification. **Formal verification** is the *highest-priority* future work identified in the whitepaper (`paper/001.banq-pro/banq-pro.tex:620`); external audits are also outstanding but ranked separately.
:::

## Status

| Item | Status | Date |
|---|---|---|
| Internal Foundry tests | Complete | (referenced in whitepaper) |
| Property tests | Complete | (referenced in whitepaper) |
| Simulation evaluation | Complete | (referenced in whitepaper) |
| Crowdsourced audit (HackenProof) | Run | See [Bug bounty](#bug-bounty) below |
| External smart-contract audit | **Not yet** | TBD |
| Formal verification | **Not yet** | TBD |
| Mainnet deployment | Live (Avalanche C-Chain) | v10c — see [contract addresses](/for-developers/contract-addresses) |

This page will be updated as audits and verifications complete. The expected publication format for each:

- **External audit reports.** PDF link, audit firm name, date, scope, and findings.
- **Formal verification.** Tools used (Certora, K Framework, etc.), properties verified, residuals.

## What "audited" will and won't mean

A completed audit is *necessary but not sufficient*. An audited contract has been reviewed for known classes of bugs by experienced reviewers. It does not guarantee absence of all bugs. Users should:

- Verify the audit firm is reputable.
- Read the audit report's findings, not just the headline.
- Pay attention to "informational" or "low" findings as well as "critical" — these can be useful warnings.
- Distinguish "audited" from "formally verified" — the latter is a stronger property.

## Bug bounty

The protocol contracts went through a crowdsourced audit on **HackenProof** sponsored by **Blackhan Software** (the company developing XPower Banq):

- **Program:** [Blackhan Software Audit Contest on HackenProof](https://hackenproof.com/audit-programs/blackhan-software-audit-contest) — HackenProof's "Crowdsourced Audit" format, in which a public pool of researchers reviews the in-scope contracts during a fixed window for tiered rewards.
- **Public reports:** disclosed findings appear under the `BLCHANAC` ticket prefix (e.g. [BLCHANAC-5](https://hackenproof.com/reports/BLCHANAC-5)). Severity, scope, and remediation status are recorded on each report page.
- **Status:** the contest window has run; findings have been triaged and remediated where applicable. Follow the program page for the canonical timeline and payout breakdown.

A continuous bug-bounty program (separate from the time-bounded contest) may be opened after the formal external audit completes. Any such program will be linked from this page when active.

## Releases and PDFs

Every tagged release of the documentation repo bundles the six papers as PDFs (signed and pinned to IPFS by `gh-paper.yml`). After the first audit completes, audit reports will be attached to the corresponding release.

- All releases: [github.com/blackhan-software/xpower-banq-doc/releases](https://github.com/blackhan-software/xpower-banq-doc/releases)
- Latest unified bundle: [`banq-all.pdf`](https://github.com/blackhan-software/xpower-banq-doc/releases/latest/download/banq-all.pdf)

## Where to go next

- [Smart contract risk](/risks/smart-contract-risk) — the full risk picture
- [Whitepaper](/research/whitepaper) — the design under review
