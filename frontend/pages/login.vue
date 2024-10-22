<script setup lang="ts">
import { object, string, type InferType } from 'yup'
import type { FormSubmitEvent } from '#ui/types'
const isOpen = ref(true)
const schema = object({
  email: string().email('Invalid email').required('Required'),
  password: string()
    .min(8, 'Must be at least 8 characters')
    .required('Required')
})

type Schema = InferType<typeof schema>

const state = reactive({
  email: undefined,
  password: undefined
})

async function onSubmit (event: FormSubmitEvent<Schema>) {
  // Do something with event.data
  const data = await $fetch("/api/login", {
    method: "POST",
    body: event.data
  })

  if (data) {
    // go home
    navigateTo("/")
  }
}
</script>

<template>
    <div>
        <UModal v-model="isOpen" prevent-close>
        <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
            <template #header>
            <div class="flex justify-center h-8">
                UP tap
            </div>
            </template>

            <div class="p-4 justify-center">
                <UForm :schema="schema" :state="state" class="space-y-4" @submit="onSubmit">
                    <UFormGroup label="Email" name="email" required>
                    <UInput v-model="state.email" />
                    </UFormGroup>

                    <UFormGroup label="Password" name="password" required>
                    <UInput v-model="state.password" type="password" />
                    </UFormGroup>

                    <div class="flex justify-center">
                        <UButton type="submit">
                            Login
                        </UButton>
                    </div>
                </UForm>
            </div>

            <template #footer>
            <div class="h-8"></div>
            </template>
        </UCard>
        </UModal>
    </div>
</template>

