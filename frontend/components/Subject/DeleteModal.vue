<script setup lang="ts">
defineProps({
    subject_name: String,
    subject_id: Number,
})

const modal = useModal()
const toast = useToast()
const emit = defineEmits(['success'])


function onSuccess() {
  emit('success')
    modal.close()
}

</script>
<template>
    <UModal prevent-close>
      <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-base text-center font-semibold leading-6 text-red-400 dark:text-white">
              Confirm Delete
            </h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" class="-my-1" @click="modal.close()" />
          </div>
        </template>
        <div class="h-20">
            <div class="flex flex-col justify-between h-full">
                <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
                    Are you sure you want to delete <span class="text-red-400 dark:text-white">{{ subject_name }}</span>?
                </h3>
                <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
                    This will also delete students and records associated with this subject.
                </h3>
                <div class="h-4 flex flex-row justify-center gap-x-1">
                    <p class="text-center mt-1 text-sm text-gray-500 dark:text-gray-400">
                    You cannot undo this action.
                    </p>
                </div>
            </div>
        </div>
        <template #footer>
          <div class="flex gap-x-2 justify-end">
            <UButton color="white" variant="solid" @click="modal.close()">
                Cancel
            </UButton>
            <UButton color="red" variant="solid" @click="onSuccess()">
                Delete
            </UButton>
            </div>
        </template>
      </UCard>
    </UModal>
</template>