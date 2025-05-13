<script setup lang="ts">
const props = defineProps<{
  currentDays?: string[];
}>()

const DAYS = [
  {
    key: "Sunday",
    label: "Sun"
  },
  {
    key: "Monday",
    label: "Mon"
  },
  {
    key: "Tuesday",
    label: "Tue"
  },
  {
    key: "Wednesday",
    label: "Wed"
  },
  {
    key: "Thursday",
    label: "Thu"
  },
  {
    key: "Friday",
    label: "Fri"
  },
  {
    key: "Saturday",
    label: "Sun"
  }
];

const selected = ref(props.currentDays || [DAYS[0].key])

const emit = defineEmits(['updateDays']);

const handleClick = (day: string) => {
  console.log('Clicked day:', day);
  if (selected.value.includes(day)) {
    selected.value = selected.value.filter((item) => item !== day);
    emit('updateDays', selected.value);
  } else {
    selected.value.push(day);
    emit('updateDays', selected.value);
  }
};



</script>

<template>
    <UButtonGroup size="lg" orientation="horizontal">
        <UButton
            v-for="day in DAYS"
            :ui="{ rounded: 'rounded-full' }"  
            :key="day.key"
            :variant="selected.includes(day.key) ? 'solid' : 'outline'"
            @click="handleClick(day.key)"
            >
            {{ day.label }}
        </UButton>
    </UButtonGroup>
</template>

