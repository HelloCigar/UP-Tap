<script setup lang="ts">
const props = defineProps<{
  currentDays?: string[];
}>()

const DAYS = [
  {
    key: "Sunday",
    label: "S"
  },
  {
    key: "Monday",
    label: "M"
  },
  {
    key: "Tuesday",
    label: "T"
  },
  {
    key: "Wednesday",
    label: "W"
  },
  {
    key: "Thursday",
    label: "T"
  },
  {
    key: "Friday",
    label: "F"
  },
  {
    key: "Saturday",
    label: "S"
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

