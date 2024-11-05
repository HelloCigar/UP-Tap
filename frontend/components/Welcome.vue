<script lang="ts" setup>
interface TimeInResponse {
  time_in: string;
  success: boolean;
  message?: string;
  time_out?: string;
  is_present?: string;
  student_name?: string;
}
const props = defineProps<TimeInResponse>()

function to12HourFormat(time: string): string {
  const [hours, minutes] = time.split(":").map(Number);
  
  const suffix = hours >= 12 ? "PM" : "AM";
  const adjustedHours = hours % 12 || 12; // Convert 0 hour to 12 for 12-hour format

  return `${adjustedHours}:${minutes.toString().padStart(2, '0')} ${suffix}`;
}
</script>

<template>
  <UModal>
    <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
      <template #header>
        <div class="flex items-center justify-between">
          <h3
            :class="props.success ? 'text-green-500' : 'text-red-500'"
            class="text-base font-semibold leading-6"
          >
            {{ props.success ? (props.time_out ? 'Time Out Successful' : 'Time In Successful') : 'Error' }}
          </h3>
        </div>
      </template>

      <div class="h-32">
        <div class="flex items-center justify-between">
          <h3 class="text-grey-800 dark:text-primary-400 text-base font-semibold leading-6">
            {{ props.success 
              ? (props.time_out 
                ? `Time-out recorded @: ${to12HourFormat(props.time_out)}` 
                : `${student_name}'s time-in recorded @: ${to12HourFormat(props.time_in)}`) 
              : props.message 
            }}
          </h3>
        </div>
      </div>
    </UCard>
  </UModal>
</template>
