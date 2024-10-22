<script setup lang="ts">
const links = [
  [{
    label: 'Profile',
    avatar: {
      src: 'https://avatars.githubusercontent.com/u/739984?v=4'
    },
    badge: 100,
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
