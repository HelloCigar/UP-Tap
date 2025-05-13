<script setup lang="ts">
defineProps<{
    day: DayData
}>()
</script>

<template>
    <UCard class="h-full">
      <template #header class="pb-2">
        <div class="flex justify-between items-center">
          <span>{{day.day_of_week}}</span>
          <UBadge  variant="outline" class="ml-2">
            {{day.free_slots.length}} {{day.free_slots.length === 1 ? "slot" : "slots"}}
          </UBadge>
        </div>
      </template #header>
      <div v-if="day.free_slots.length > 0">
          <ul class="space-y-2">
              <li 
                v-for="slot, index in day.free_slots"
                :key="index"
                class="p-2 bg-primary-50 border border-primary-600 rounded-md flex justify-between">
                <span class="font-medium">{{convertTo12HourFormat(slot.start)}}</span>
                <span class="text-gray-500">to</span>
                <span class="font-medium">{{convertTo12HourFormat(slot.end)}}</span>
              </li>
          </ul>
        </div>
        <div v-else>
          <p class="text-gray-500 text-center py-4">No available slots</p>
        </div>
    </UCard>
</template>