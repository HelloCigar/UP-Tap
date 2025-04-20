<script setup lang="ts">
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';

const props = defineProps<{
  currentTime?: SubjectTimeAndSchedule[];
}>()

const time = ref();


const minTime = ref({
  hours: 5,
  minutes: 0
});
const maxTime = ref({
  hours: 20,
  minutes: 0
});

const emit = defineEmits(['updateTime']);

watch(time, (newTime) => {
  emit('updateTime', newTime);
});

</script>

<template>
   <VueDatePicker 
    v-model="time"
    :min-time="minTime" 
    :max-time="maxTime"
    :is-24="false" 
    time-picker 
    minutes-grid-increment="15"
    range
    :placeholder="props.currentTime ?  `Current Schedule: ${props.currentTime[0].start_time} - ${props.currentTime[0].end_time}`: 'Time Schedule'"/>
</template>

