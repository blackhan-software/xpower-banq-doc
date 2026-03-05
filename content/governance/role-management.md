# Role management

How roles are granted and revoked in Acma. Acma extends OpenZeppelin's `AccessManager`, so the underlying mechanics are standard.

## The three-tier pattern

Each privileged action `X` defines three roles:

- **Base** (`X_ROLE`) — holders may *call* the gated function.
- **Admin** (`X_ADMIN_ROLE`) — holders may *grant* and *revoke* the base role and *modify its delays*.
- **Guard** (`X_GUARD_ROLE`) — holders may *cancel* a pending operation scheduled against the base role.

So "admin" and "guard" are companions to a specific base role; there is no single global admin or single global guard. See [Role hierarchy](/features/lethargic-governance/role-hierarchy) for the full role taxonomy.

## Per-pool scoping

Every role is scoped to one pool: the role accessors take the pool name as an argument (`POOL_SQUARE_ROLE("P007")`), and the role ID is derived from `keccak256(<verb>, <domain>, <pool-name>)`. Granting, revoking, or reconfiguring a role therefore applies to a single pool's instance — the same verb in another pool is an independent role. The only global role is `ACMA_RELATE_ROLE()`. When you see a bare role name like `POOL_SQUARE_ROLE` in these docs, read it as `POOL_SQUARE_ROLE(<pool>)` for the specific pool in question.

## Granting

The matching `_ADMIN_ROLE` holder calls `Acma.grantRole(role, account, executionDelay)`. The grant takes effect immediately for the role-membership but is subject to the per-target execution delay configured by the admin.

Multiple addresses can hold the same role.

## Revoking

The matching `_ADMIN_ROLE` holder calls `Acma.revokeRole(role, account)`. The address is removed.

## Self-revocation

Any role-holder can revoke themselves via `Acma.renounceRole(role, callerConfirmation)`. This is one-way; renouncing a role nobody else holds (e.g. an `_ADMIN_ROLE`) creates an irrecoverable state for that role family. **Be very careful with this.**

## Admin rotation

To rotate the holder of an `_ADMIN_ROLE`:

1. The current admin grants the role to the new address.
2. Verify the new address can perform a representative admin action (small test).
3. The old admin renounces the role.

The window between (1) and (3) is when both addresses hold the role. Plan accordingly.

## Where to go next

- [Role hierarchy](/features/lethargic-governance/role-hierarchy) — what each role does
- [Emergency procedures](/governance/emergency-procedures) — using roles in a crisis
- [CLI and tools](/for-keepers/cli-and-tools) — `banq acma` for live inspection
