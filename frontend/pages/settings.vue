<script setup lang="ts">

definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

const toast = useToast()

const items = [{
  slot: 'account',
  label: 'Account'
}, {
  slot: 'password',
  label: 'Password'
}]

const { data: user } = await useFetch<Teacher>('/api/teachers/me', { method: 'GET' })

const accountForm = reactive({ first_name: "", last_name: "" })
const passwordForm = reactive({ current_password: '', new_password: '' })
const loading = ref(false)

async function onSubmitAccount() {
    loading.value = true
    await $fetch('/api/teachers/me', {
        method: 'PATCH',
        body: accountForm
    }).catch((e) => {
        toast.add({
            title: 'Error updating account',
            id: 'account-error',
            color: 'red',
        })
    }).then(() => {
        toast.add({
            title: 'Account updated successfully',
            id: 'account-success',
            color: 'green',
        })
        //delay reload
        setTimeout(() => window.location.reload(), 1500)

    }).finally(() => loading.value = false)
}

async function onSubmitPassword() {
    loading.value = true
    await $fetch('/api/teachers/set-password', {
        method: 'POST',
        body: passwordForm
    }).catch((e) => {
        toast.add({
            title: 'Error updating password',
            id: 'password-error',    
            color: 'red',
        })    
    }).then(() => {
        toast.add({
            title: 'Password updated successfully',
            id: 'password-success',
            color: 'green',
        })
        setTimeout(() => {
            useUserSession().clear()
            navigateTo('/login')
        }, 2000)
        
    }).finally(() => loading.value = false)
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
    }"
  >
    <template #header>
      <div class="flex justify-between items-center w-full">
        <div class="">
          <h1 class="text-xl font-semibold text-gray-900 dark:text-white">Settings</h1>
        </div>
      </div>
    </template>
    <UTabs :items="items" class="p-6">
    <template #account="{ item }">
      <UCard @submit.prevent="onSubmitAccount">
        <template #header>
          <p class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
            {{ item.label }}
          </p>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Make changes to your account here. Click save when you're done.
          </p>
        </template>

        <UFormGroup label="First Name" name="first_name" class="mb-3 w-1/2">
          <UInput v-model="accountForm.first_name" :placeholder="user?.first_name" />
        </UFormGroup>
        <UFormGroup label="Last Name" name="last_name" class="w-1/2">
          <UInput v-model="accountForm.last_name" :placeholder="user?.last_name"/>
        </UFormGroup>

        <template #footer>
          <UButton type="submit" :disabled="!accountForm.first_name && !accountForm.last_name" :loading="loading">
            Save account
          </UButton>
        </template>
      </UCard>
    </template>

    <template #password="{ item }">
      <UCard @submit.prevent="onSubmitPassword">
        <template #header>
          <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
            {{ item.label }}
          </h3>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Change your password here. After saving, you'll be logged out.
          </p>
        </template>

        <UFormGroup label="Current Password" name="current" required class="mb-3 w-1/2">
          <UInput v-model="passwordForm.current_password" type="password" required />
        </UFormGroup>
        <UFormGroup label="New Password" name="new" required class="w-1/2">
          <UInput v-model="passwordForm.new_password" type="password" required />
        </UFormGroup>

        <template #footer>
          <UButton type="submit" :loading="loading">
            Save password
          </UButton>
        </template>
      </UCard>
    </template>
  </UTabs>
    </UCard>
</template>

