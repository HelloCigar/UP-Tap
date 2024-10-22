<script setup lang="ts">
	definePageMeta({
		// layout: 'default',
		// name: 'new-page',
		// alias: 'new-page',
		title: 'New Page',
		description: 'New Page',
		// hidden: true,
		navOrder: '5',
		type: 'primary',
    icon: 'i-mdi-home',
    // ogImage: 'images/ogImage.png', // url or local images inside public folder, for eg, ~/public/images/ogImage.png
	})
</script>

<template>
	<div>
		<div style="min-height: 100px; display: flex; align-items: center; justify-content: center; font-weight: bold">
			<span style="color: #0198cd">new-page.vue (Nuxt 3.13)</span>
		</div>
	</div>
</template>

<style scoped></style>

