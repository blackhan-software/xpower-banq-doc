<template>
  <h1 class="name">
    <span class="clip">XPower Banq</span> Protocol
    <br />Documentation
  </h1>
  <p class="tagline">
    A Permissionless DeFi Lending Protocol with Lethargic
    Governance and Beta-Distributed Position Caps
  </p>
</template>

<style scoped>
.name {
  font-size: 48px;
  line-height: 1.1;
  font-weight: 700;
  white-space: pre-line;
}

.name .clip {
  background: var(--vp-c-brand-1);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.tagline {
  font-size: 20px;
  padding-top: 12px;
  line-height: 1.5;
  color: var(--vp-c-text-2);
  max-width: 640px;
}

@media (min-width: 640px) {
  .name {
    font-size: 56px;
  }
}

@media (min-width: 960px) {
  .name {
    font-size: 64px;
  }
  .tagline {
    font-size: 24px;
  }
}
</style>
