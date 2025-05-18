<script setup lang="ts">


import { object, string, type InferType } from 'yup'
import type { FormSubmitEvent } from '#ui/types'
const isOpen = ref(true)
const schema = object({
  email: string().email('Invalid email').required('Required'),
  first_name: string().required('Please enter your first name'),
  last_name: string().required('Please enter your last name'),
  password: string()
    .min(8, 'Must be at least 8 characters')
    .required('Required')
})

type Schema = InferType<typeof schema>

const state = reactive({
  email: undefined,
  first_name: undefined,
  last_name: undefined,
  password: undefined
})

const emailSent = ref(false)

async function onSubmit (event: FormSubmitEvent<Schema>) {
  error.value = false
  // Do something with event.data
  const data = await $fetch("/api/signup", {
    method: "POST",
    body: event.data
  })

  if (data && "id" in data) {
    // go home
    emailSent.value = true

  }
  else {
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
          <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }" v-if="!emailSent">
              <template #header>
                <p class="text-center text-base font-semibold leading-6 text-gray-900 dark:text-white">
                  UP Tap
                </p>
                <p class="text-center mt-1 text-sm text-gray-500 dark:text-gray-400">
                  Signup to our system
                </p>
              </template>

              <div class="p-4 justify-center">
                  <UForm :schema="schema" :state="state" class="space-y-4" @submit="onSubmit">
                      <UFormGroup label="Email" name="email" required>
                      <UInput v-model="state.email" />
                      </UFormGroup>

                      <UFormGroup label="First Name" name="first_name" required>
                      <UInput v-model="state.first_name" />
                      </UFormGroup>

                      <UFormGroup label="Last Name" name="last_name" required>
                      <UInput v-model="state.last_name" />
                      </UFormGroup>

                      <UFormGroup label="Password" name="password" required>
                      <UInput v-model="state.password" type="password" />
                      </UFormGroup>

                      <div class="flex justify-center">
                          <UButton type="submit">
                              Signup
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
                    Already have an account?
                  </p>
                <ULink to="/login">
                  <p class="text-center mt-1 text-sm text-primary dark:text-gray-400">
                    Login
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
          <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }" v-else>
            <template #header>  
              <p class="text-center text-base font-semibold leading-6 text-gray-900 dark:text-white">
                UP Tap
              </p>
            </template>

            <div class="flex flex-col items-center gap-y-10">
              <p class="text-center mt-1 text-sm text-gray-500 dark:text-gray-400">
                A confirmation email has been sent to your email address.
              </p>
              <UButton>
                <NuxtLink to="/login">Go to Login</NuxtLink>
              </UButton>
            </div>
          </UCard>
        </UModal>
    </div>
</template>

