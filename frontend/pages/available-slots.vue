<script setup lang="ts">
definePageMeta({
    middleware: 'auth'
})

const { data: schedule } = await useFetch<DayData[]>('/api/teachers/available-slots', {
  method: 'GET'
})

console.log(schedule.value)
const sortedSchedule = computed(() => {
    if (!schedule.value) return []
    return sortDays(schedule.value) 
})

</script>
<template>
    <main class="min-h-screen p-4 md:p-8 bg-gray-50">
      <div class="max-w-6xl mx-auto">
        <h1 class="text-3xl font-bold mb-6 text-center">Weekly Availability</h1>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <AvailableDaySchedule 
                v-for="day in sortedSchedule"
                :key="day.day_of_week"
                :day="day" 
            />
        </div>
      </div>
    </main>
</template>