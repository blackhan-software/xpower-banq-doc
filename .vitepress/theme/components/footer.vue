<script setup lang="ts">
import { ref, onMounted } from 'vue'

const address = 'P.O. Box 2255, Shedden Road, Georgetown, Grand Cayman KY1-1107, KY'

const year = ref(new Date().getFullYear())
onMounted(() => {
  year.value = new Date().getFullYear()
})
</script>

<template>
  <footer class="site-footer">
    <p class="copyright">
      <span class="company" :aria-label="address" :title="address">
        <span>©</span><span>&nbsp;{{ year }}</span><span class="company-name">&nbsp;Moorhead LLC</span>
      </span>
    </p>
  </footer>
</template>

<style scoped>
.site-footer {
  border-top: 1px solid var(--vp-c-divider);
  padding: 16px 24px;
  text-align: center;
  background-color: var(--vp-c-bg);
}

.copyright {
  margin: 0;
  font-size: 13px;
  color: var(--vp-c-text-2);
}

.company {
  cursor: help;
}

/* Hide the company name below Bootstrap's `sm` breakpoint, matching the
   `d-none d-sm-inline` behavior of the source markup. */
.company-name {
  display: none;
}

@media (min-width: 576px) {
  .company-name {
    display: inline;
  }
}
</style>
