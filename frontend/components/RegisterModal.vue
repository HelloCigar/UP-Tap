<script lang="ts" setup>

defineProps({
  title: String,
  message: String
})
const emit = defineEmits(['success'])

function onSuccess () {
  emit('success')
}

const modal = useModal()

const successClass = ref('text-green-500')
const errorClass = ref('text-red-500')
</script>

<template>
    <UModal>
      <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold leading-6 dark:text-white"
            :class="title == 'Success' ? successClass: errorClass">
              {{ title }}
            </h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" class="-my-1" @click="modal.close()" />
          </div>
        </template>

        <div class="h-32">
            <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
              {{ message }}
            </h3>
        </div>
      </UCard>
    </UModal>
</template>

