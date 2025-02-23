<script setup lang="ts">
definePageMeta({
    layout: 'dashboard',
    middleware: 'auth'
})


// UI State
const showSubjectModal = ref(false)
const selectedSubject = ref<Subjects | null>(null)
const recordType = ref('time_in')
const newSubject = ref({ subject_name: '', section: ''})
const deleted = ref(false)

const { data: subjects } = await useFetch<Subjects[]>(() => '/api/teachers/subjects', 
  { 
    method: 'GET',
    watch: [newSubject, deleted]
  },
)

// Modal handlers
const openAddModal = () => {
  selectedSubject.value = null
  newSubject.value = { subject_name: '', section: ''}
  showSubjectModal.value = true
}

const openEditModal = (subject: Subjects) => {
  selectedSubject.value = subject
  newSubject.value = { ...subject }
  showSubjectModal.value = true
}

const closeModal = () => {
  showSubjectModal.value = false
  selectedSubject.value = null
  newSubject.value = { subject_name: '', section: ''}
}

async function saveSubject () {
  if (selectedSubject.value) {
    await $fetch('/api/subjects', {
      method: 'PUT',
      body: newSubject.value,
      query: {
        subject_id: selectedSubject.value.subject_id
      }
    })
  } else {
    await $fetch('/api/subjects', {
      method: 'POST',
      body: newSubject.value,
    })
  }
  closeModal()
}

async function deleteSubject (subject_id: number) {
  await $fetch('/api/subjects', {
    method: 'DELETE',
    query: {
      subject_id: subject_id
    }
  })
  deleted.value = !deleted.value
}


async function logout() {
  await $fetch('/api/logout', { method: 'POST' })
  await navigateTo('/login')
}

const { data: timeInOutData, status: timeInOutStatus } = await useAsyncData<{time_in: string, time_out: string, student_name: string}[]>
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

import { useEventSource } from '@vueuse/core'

const { status, data, error, close, eventSource,  } = useEventSource('/api/sse', ['time_in', 'time_out'] as const, {
  autoReconnect: true
})
if (eventSource.value) {
  eventSource.value.addEventListener("time_in", function(event) {
    const data = JSON.parse(event.data);
    timeInOutData.value?.unshift(data as {time_in: string, time_out: string, student_name: string})
    console.log("Received message:", data);
  });
  eventSource.value.addEventListener("time_out", function(event) {
      const data = JSON.parse(event.data);
      //find similar name and date, then add time_out field
      timeInOutData.value?.forEach((item) => {
        if (item.student_name === data.student_name && item.date === data.date) {
          item.time_out = data.time_out
        }
      })
      console.log("Received message:", data);
  })

}
onMounted(() => {
  
})

onBeforeUnmount(() => {
  close()
})
// const { data: timeInData, status: timeInStatus, close: closeTimeIn, eventSource: timeInEvent } = useEventSource('/api/sse/time_in', [], {
//   autoReconnect: true
// })

// const { data: timeOutData, status: timeOutStatus, close: closeTimeOut, eventSource: timeOutEvent } = useEventSource('/api/sse/time_out', [], {
//   autoReconnect: true
// })

// onMounted(() => {
//   console.log('Time In Status:', timeInStatus.value)
//   console.log('Time Out Status:', timeOutStatus.value)
// })

// onBeforeUnmount(() => {
//   closeTimeIn()
//   closeTimeOut()
// })

// watch(timeInData, (newData) => {
//   console.log('New data:', newData)
// })

// watch(timeOutData, (newData) => {
//   console.log('New data:', newData)
// })

// timeInEvent.value.onmessage = (event) => {
//   timeInOutData.value?.unshift(JSON.parse(event.data) as {time_in: string, time_out: string, student_name: string})
//   console.log(JSON.parse(event.data))
// }

// timeOutEvent.value.onmessage = (event) => {
//   timeInOutData.value?.unshift(JSON.parse(event.data) as {time_in: string, time_out: string, student_name: string})
//   console.log(JSON.parse(event.data))
// }

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
      <div class="grid gap-8 md:grid-cols-2 items-start">
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
              v-if="timeInOutData"
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
            <UButton
              @click="openAddModal"
            >
              Add Subject
            </UButton>
          </div>

          <div class="space-y-4">
            <div v-for="subject in subjects" :key="subject.subject_id" 
                 class="flex items-center justify-between p-4 rounded-lg bg-gray-50 dark:bg-gray-700/50">
              <div>
                <h3 class="font-medium text-gray-900 dark:text-white">{{ subject.subject_name }}</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">Section {{ subject.section }}</p>
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
                  @click="deleteSubject(subject.subject_id)"
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
    <UModal v-model="showSubjectModal">
      <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ selectedSubject ? 'Edit Subject' : 'Add Subject' }}
          </h2>
        </template>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Subject Name</label>
            <UInput
              v-model="newSubject.subject_name"
              type="text"
              placeholder="CMSC..." 
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Section</label>
            <UInput
              v-model="newSubject.section"
              type="text"
              placeholder="1..." 
            />
          </div>
        </div>

        <template #footer>
          <div class="flex justify-end gap-3 mt-6">
          <UButton
            @click="closeModal"
          >
            Cancel
          </UButton>
          <UButton
            @click="saveSubject"
          >
            {{ selectedSubject ? 'Save Changes' : 'Add Subject' }}
          </UButton>
        </div>
        </template>
      </UCard>
    </UModal>
    </div>
    </div>

    <template #footer>
      <div class="h-8"></div>
    </template>
  </UCard>
</template>