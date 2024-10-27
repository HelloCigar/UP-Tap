<script lang="ts" setup>
defineProps({
  count: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['success'])

function onSuccess () {
  emit('success')
}
</script>

<template>
  <UModal>
    <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <Placeholder class="h-8" />
        </template>

        <Placeholder class="h-32" />

        <template #footer>
          <Placeholder class="h-8" />
        </template>
      </UCard>
  </UModal>
</template>

