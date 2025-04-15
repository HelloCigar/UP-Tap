<script setup lang="ts">
definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})
</script>

<template>
    <UCard variant="subtle">
      <template #header>
        <UTextarea placeholder="Type something..." class="h-32"/>
      </template>

      <UTextarea placeholder="Type something..." class="h-32"/>
    </UCard>
</template>