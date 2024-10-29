<script setup lang="ts">
definePageMeta({
    layout: 'dashboard',
    middleware: 'auth'
})


async function logout() {
  await $fetch('/api/logout', { method: 'POST' })
  await navigateTo('/login')
}

</script> 
<template>
  <UCard
  class="w-full h-full"
    :ui="{
      base: '',
      ring: '',
      divide: 'divide-y divide-gray-200 dark:divide-gray-700',
      header: { padding: 'px-4 py-4' },
      body: { padding: '', base: 'divide-y divide-gray-200 dark:divide-gray-700' },
      footer: { padding: 'p-4' }
    }">
    <template #header>
      <div class="flex justify-between items-center w-full">
        <h2 class="font-semibold text-xl text-gray-900 dark:text-white leading-tight">
          Dashboard
        </h2>
        <AuthState>
          <UButton
              icon="i-heroicons-arrow-left-start-on-rectangle"
              size="sm"
              color="red"
              variant="outline"
              label="Logout"
              @click="logout"
          />
      </AuthState>
      </div>
    </template>

    <div class="h-32"></div>

    <template #footer>
      <div class="h-8"></div>
    </template>
  </UCard>
</template>