<script setup lang="ts">
definePageMeta({
    layout: 'dashboard',
    middleware: 'auth'
})


// Mock data for subjects
const subjects = ref([
  { id: 1, name: 'Mathematics', schedule: 'MWF 8:30-10:30 AM', students: 35 },
  { id: 2, name: 'Physics', schedule: 'TTH 9:15-11:15 AM', students: 28 },
  { id: 3, name: 'Chemistry', schedule: 'MWF 10:00-12:00 PM', students: 32 },
])

// UI State
const showSubjectModal = ref(false)
const selectedSubject = ref(null)
const recordType = ref('time_in')
const newSubject = ref({ name: '', schedule: '', students: 0 })

// Modal handlers
const openAddModal = () => {
  selectedSubject.value = null
  newSubject.value = { name: '', schedule: '', students: 0 }
  showSubjectModal.value = true
}

const openEditModal = (subject) => {
  selectedSubject.value = subject
  newSubject.value = { ...subject }
  showSubjectModal.value = true
}

const closeModal = () => {
  showSubjectModal.value = false
  selectedSubject.value = null
  newSubject.value = { name: '', schedule: '', students: 0 }
}

const saveSubject = () => {
  if (selectedSubject.value) {
    const index = subjects.value.findIndex(s => s.id === selectedSubject.value.id)
    subjects.value[index] = { ...selectedSubject.value, ...newSubject.value }
  } else {
    subjects.value.push({
      id: subjects.value.length + 1,
      ...newSubject.value
    })
  }
  closeModal()
}

const deleteSubject = (id) => {
  subjects.value = subjects.value.filter(s => s.id !== id)
}


async function logout() {
  await $fetch('/api/logout', { method: 'POST' })
  await navigateTo('/login')
}

const { data: timeInOutData, status: timeInOutStatus } = await useAsyncData<{time_in: string, time_out: string, student_name: string}>
    ('', () => $fetch(`/api/attendance/recent/`, {
       method: 'GET', 
       query: 
      { type: recordType.value } 
      }
    ),
    { watch: [recordType] }
  )
const time_in_columns = [{
  key: 'student_name',
  label: 'Student Name',
}, {
  key: 'subject_name',
  label: 'Subject',
},{
  key: 'time_in',
  label: 'Time In',
},{
  key: 'date',
  label: 'Date'
}]

const time_out_columns = [{
  key: 'student_name',
  label: 'Student Name',
},  {
  key: 'subject_name',
  label: 'Subject',
}, {
  key: 'time_out',
  label: 'Time Out',
}, {
  key: 'date',
  label: 'Date',
}]


</script> 
<template>
  <UCard
  class="w-full h-full"
    :ui="{
      base: '',
      ring: '',
      divide: 'divide-y divide-gray-200 dark:divide-gray-700',
      header: { padding: 'px-4 py-4' },
      body: { padding: '', base: 'divide-y divide-gray-200 dark:divide-gray-700' },
      footer: { padding: 'p-4' }
    }">
    <template #header>
      <div class="flex justify-between items-center w-full">
        <div class="">
          <h1 class="text-xl font-semibold text-gray-900 dark:text-white">UP Tap Dashboard</h1>
        </div>
        <AuthState>
          <UButton
              icon="i-heroicons-arrow-left-start-on-rectangle"
              size="sm"
              color="red"
              variant="outline"
              label="Logout"
              @click="logout"
          />
      </AuthState>
      </div>
    </template>

  <div>
  <div class="min-h-screen">
    <!-- Main Content -->
    <div class="p-8">

      <!-- Attendance Records -->
      <div class="grid gap-8 md:grid-cols-2">
        <!-- Recent Attendance -->
        <UCard>
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Recent Attendance</h2>
            <div class="flex gap-2">
              <button
                @click="recordType = 'time_in'"
                class="px-3 py-1 rounded-full text-sm"
                :class="recordType === 'time_in' ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-700'"
              >
                Time In
              </button>
              <button
                @click="recordType = 'time_out'"
                class="px-3 py-1 rounded-full text-sm"
                :class="recordType === 'time_out' ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-700'"
              >
                Time Out
              </button>
            </div>
          </div>
          
          <div class="space-y-4">
            <UTable 
              :loading="timeInOutStatus === 'pending'"
              :loading-state="{ icon: 'i-heroicons-arrow-path-20-solid', label: 'Loading...' }"
              :progress="{ color: 'primary', animation: 'carousel' }"
              class="w-full"
              :rows="timeInOutData" :columns="recordType === 'time_in' ? time_in_columns : time_out_columns"
              :empty-state="{ icon: 'i-heroicons-circle-stack-20-solid', label: 'No items.' }" 
              >
            <template #time_in-data="{ row }">
              {{ convertTo12HourFormat(row.time_in) }}
            </template>
            <template #time_out-data="{ row }">
              {{ convertTo12HourFormat(row.time_out) }}
            </template>
            </UTable>
          </div>
        </UCard>

        <!-- Subjects Management -->
        <UCard>
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Subjects</h2>
            <button
              @click="openAddModal"
              class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
            >
              Add Subject
            </button>
          </div>

          <div class="space-y-4">
            <div v-for="subject in subjects" :key="subject.id" 
                 class="flex items-center justify-between p-4 rounded-lg bg-gray-50 dark:bg-gray-700/50">
              <div>
                <h3 class="font-medium text-gray-900 dark:text-white">{{ subject.name }}</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">{{ subject.schedule }}</p>
                <p class="text-sm text-gray-500 dark:text-gray-400">{{ subject.students }} students</p>
              </div>
              <div class="flex gap-2">
                <button
                  @click="openEditModal(subject)"
                  class="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                  </svg>
                </button>
                <button
                  @click="deleteSubject(subject.id)"
                  class="p-2 text-red-500 hover:text-red-700"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </UCard>
      </div>
    </div>

    <!-- Subject Modal -->
    <div v-if="showSubjectModal" class="fixed inset-0 bg-black/50 flex items-center justify-center">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md">
        <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
          {{ selectedSubject ? 'Edit Subject' : 'Add Subject' }}
        </h2>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Subject Name</label>
            <input
              v-model="newSubject.name"
              type="text"
              class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Schedule</label>
            <input
              v-model="newSubject.schedule"
              type="text"
              class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Number of Students</label>
            <input
              v-model="newSubject.students"
              type="number"
              class="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
            />
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-6">
          <button
            @click="closeModal"
            class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
          >
            Cancel
          </button>
          <button
            @click="saveSubject"
            class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
          >
            {{ selectedSubject ? 'Save Changes' : 'Add Subject' }}
          </button>
        </div>
      </div>
    </div>
  </div>
    </div>

    <template #footer>
      <div class="h-8"></div>
    </template>
  </UCard>
</template>