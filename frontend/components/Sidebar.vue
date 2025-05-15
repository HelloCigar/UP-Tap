<script setup lang="ts">

const teacher = await useFetch<Teacher>('/api/teachers/me', { method: 'GET' })

const links = [
  [{
    label: 'Dashboard',
    icon: 'i-heroicons-arrow-path-rounded-square-16-solid',
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
  }], [
    {
      label: 'Settings',
      icon: 'i-heroicons-cog',
      to: '/settings'
    }, {
      label: 'Logout',
      icon: 'i-heroicons-arrow-right-on-rectangle',
      click: () => {
        useUserSession().clear()
        navigateTo('/login')
      }
    }
  ]
]
</script>

<template>
  <UVerticalNavigation :links="links" :ui="{ width: 'w-48', active: 'text-primary-600 dark:text-white before:bg-primary-100 dark:before:bg-gray-800',}" />
</template>
