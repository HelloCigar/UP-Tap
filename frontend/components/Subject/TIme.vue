<script setup lang="ts">
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';

const props = defineProps<{
  currentTime?: {
    start_time: string;
    end_time: string;
  };
}>()

const time = ref();
const defaultTime = ref([
  {
    hours: props.currentTime?.start_time ? parseInt(props.currentTime.start_time.split(':')[0]) : 7,
    minutes: props.currentTime?.start_time ? parseInt(props.currentTime.start_time.split(':')[1]) : 0
  },
  {
    hours: props.currentTime?.end_time ? parseInt(props.currentTime.end_time.split(':')[0]) : 8,
    minutes: props.currentTime?.end_time ? parseInt(props.currentTime.end_time.split(':')[1]) : 0
  }
])


const minTime = ref({
  hours: 5,
  minutes: 0
});
const maxTime = ref({
  hours: 24,
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
    :start-time="defaultTime"
    :is-24="false" 
    time-picker 
    minutes-grid-increment="15"
    range
    :placeholder="props.currentTime ?  `Current Schedule: ${props.currentTime.start_time} - ${props.currentTime.end_time}`: `Default Schedule: 7:00 AM - 8:00 AM`"/>
</template>

