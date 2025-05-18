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

const loading = ref(false)
async function onSubmit (event: FormSubmitEvent<Schema>) {
  error.value = false
  loading.value = true
  // Do something with event.data
  const data = await $fetch("/api/login", {
    method: "POST",
    body: event.data
  })
  if (data && "auth_token" in data) {
    loading.value = false
    const { fetch } = useUserSession();
    await fetch();
    // go to dashboard
    await navigateTo('/dashboard')
  }
  else {
    loading.value = false
    error.value = data?.error
    errorMsg.value = data?.message
  }
}

const error = ref<boolean>()
const errorMsg = ref<string>()
</script>

<template>
    <div>
        <UModal v-model="isOpen" prevent-close>
        <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
            <template #header>
              <p class="text-center text-base font-semibold leading-6 text-gray-900 dark:text-white">
                UP Tap
              </p>
              <p class="text-center mt-1 text-sm text-gray-500 dark:text-gray-400">
                Login to your account
              </p>
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
                        <UButton type="submit" :loading="loading">
                            Login
                        </UButton>
                    </div>
                    <p v-if="error" class="text-center mt-1 text-sm text-red-500 dark:text-gray-400">
                        {{ errorMsg }}
                    </p>
                </UForm>
            </div>

            <template #footer>
              <div>
                <div class="h-8 flex flex-row justify-center gap-x-1">
                  <p class="text-center mt-1 text-sm text-gray-500 dark:text-gray-400">
                    First time here?
                  </p>
                  <ULink to="/signup">
                    <p class="text-center mt-1 text-sm text-primary dark:text-gray-400">
                      Signup
                    </p>
                  </ULink>
                </div>
              <UDivider label="OR" />
              <ULink to="/public/register">
                <p class="text-center mt-4 text-sm text-primary underline dark:text-gray-400">
                  If you're a student, go here instead
                </p>
              </ULink>
            </div>
          </template>
        </UCard>
        </UModal>
    </div>
</template>

