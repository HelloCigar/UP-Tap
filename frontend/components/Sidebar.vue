<script setup lang="ts">
import { Icon } from '#build/components';


const teacher = await useFetch<Teacher>('/api/teachers/me', { method: 'GET' })

const links = [
  [{
    label: `${teacher.data.value?.first_name} ${teacher.data.value?.last_name}`,
    icon: 'i-heroicons-user',
    to: '/dashboard/'
  }, {
    label: 'Time In/Out',
    icon: 'i-heroicons-clock',
    to: '/dashboard/time-in-out'
  }, {
    label: 'Students',
    icon: 'i-heroicons-academic-cap',
    to: '/dashboard/student'
  }, {
    label: 'Reports',
    icon: 'i-heroicons-presentation-chart-bar',
    to: '/dashboard/reports'
  }]
]
</script>

<template>
  <UVerticalNavigation :links="links" :ui="{ width: 'w-48' }" />
</template>
