<script setup lang="ts">
const route = useRoute()
const { uid, token } = route.params
const activated = ref(false)
async function activate() {
    await $fetch('/api/activate', {
        method: 'POST',
        body: {
            uid: uid,
            token: token
        }
    }).catch((e) => {
        console.log(e)
    }).then((res) => {
        activated.value = true
    })

}
const isOpen = ref(true)

onMounted(() => {
    activate()
})
</script>
<template>
    <UModal v-model="isOpen" prevent-close>
          <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
              <template #header>
                <p class="text-center text-base font-semibold leading-6 text-gray-900 dark:text-white">
                  UP Tap
                </p>
              </template>

              <div class="flex flex-col items-center gap-y-5" v-if="!activated">
                <UProgress animation="carousel" />
                <p class="text-center mt-1 text-sm text-gray-500 dark:text-gray-400">
                  Activating your account...
                </p>
              </div>
              <div class="flex flex-col items-center gap-y-5" v-else>
                <p class="text-center mt-1 text-sm text-gray-500 dark:text-gray-400">
                  Account successfully activated!
                </p>
                <UButton>
                  <NuxtLink to="/login">Go to Login</NuxtLink>
                </UButton>
              </div>
          </UCard>
    </UModal>
</template>