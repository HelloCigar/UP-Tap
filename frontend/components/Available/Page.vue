<script setup lang="ts">
definePageMeta({
    middleware: 'auth'
})

const { data: schedule } = await useFetch<DayData[]>('/api/teachers/available-slots', {
  method: 'GET'
})

const sortedSchedule = computed(() => {
    if (!schedule.value) return []
    return sortDays(schedule.value) 
})

const isOpen = ref(false)

</script>
<template>
    <UButton
        variant="link" 
        label="See available time slots" 
        @click="isOpen = true" 
    />
    <UModal v-model="isOpen" fullscreen>
        <UCard
        :ui="{
          base: 'h-full flex flex-col',
          rounded: '',
          divide: 'divide-y divide-gray-100 dark:divide-gray-800',
          body: {
            base: 'grow'
          }
        }"
      >
        <template #header>
          <div class="flex items-center justify-between">
            <h1 class="text-3xl font-bold mb-6 text-center">Weekly Availability</h1>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" class="-my-1" @click="isOpen = false" />
          </div>
        </template>
        <main class="h-full p-4 md:p-8 bg-gray-50">
            <div class="max-w-6xl mx-auto">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <AvailableDaySchedule 
                        v-for="day in sortedSchedule"
                        :key="day.day_of_week"
                        :day="day" 
                    />
                </div>
            </div>
        </main>
      </UCard>
        
    </UModal>
</template>