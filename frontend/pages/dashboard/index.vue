<script setup lang="ts">
definePageMeta({
    layout: 'dashboard',
    middleware: 'auth'
})

// UI State
const showSubjectModal = ref(false)
const selectedSubject = ref<Subjects>()
const recordType = ref('time_in')
const newSubject = ref<Subjects>()
const deleted = ref(false)

const { data: subjects } = await useFetch<Subjects[]>(() => '/api/teachers/subjects', 
  { 
    method: 'GET',
    watch: [newSubject, deleted, newSubject]
  },
)

// Modal handlers
const openAddModal = () => {
  newSubject.value = {
    subject_id: 0,
    subject_name: '',
    schedule: [],
    start_time: '',
    end_time: '',
  }
  selectedSubject.value = undefined
  showSubjectModal.value = true
}

const openEditModal = (subject: Subjects) => {
  console.log('Edit subject:', subject)
  selectedSubject.value = subject
  showSubjectModal.value = true
}

const closeModal = () => {
  showSubjectModal.value = false
  deleted.value = !deleted.value
}

//emit handlers
function handleTimeUpdate(newTime: { hours: number, minutes: number }[]) {
  //handle single digits 
  let start_hours = `${newTime[0].hours}`
  let start_minutes = `${newTime[0].minutes}`
  let end_hours = `${newTime[1].hours}`
  let end_minutes = `${newTime[1].minutes}`
  if (newTime[0].hours < 10) {
    start_hours = `0${newTime[0].hours}`
  }
  if (newTime[0].minutes < 10) {
    start_minutes = `0${newTime[0].minutes}`
  }
  if (newTime[1].hours < 10) {
    end_hours = `0${newTime[1].hours}`
  }
  if (newTime[1].minutes < 10) {
    end_minutes = `0${newTime[1].minutes}`
  }
  if(newSubject.value) {
    newSubject.value.start_time = `${start_hours}:${start_minutes}`
    newSubject.value.end_time = `${end_hours}:${end_minutes}`
  }
  if (selectedSubject.value) {
    selectedSubject.value.start_time = `${start_hours}:${start_minutes}`
    selectedSubject.value.end_time = `${end_hours}:${end_minutes}`
    console.log('Selected subject:', selectedSubject.value);
  }
}

function handleDaysUpdate(newDays: string[]) {
  if (newSubject.value) {
    newSubject.value.schedule = newDays
  }
  if (selectedSubject.value) {
    selectedSubject.value.schedule = newDays
  }
  console.log(newSubject.value);
  console.log(selectedSubject.value);
  console.log(newDays);
}


async function saveSubject () {
  if (selectedSubject.value) {
    await $fetch('/api/subjects', {
      method: 'PUT',
      body: selectedSubject.value,
      query: {
        subject_id: selectedSubject.value.subject_id
      }
    }
  )
  } else {
    console.log('New subject:', newSubject.value);
    await $fetch('/api/subjects', {
      method: 'POST',
      body: newSubject.value,
    })
  }
  closeModal()
}

const modal = useModal()
import { AvailablePage, SubjectDeleteModal } from '#components'
async function deleteSubject (subject: Subjects) {
  modal.open(
    SubjectDeleteModal, {
      subject_id: subject.subject_id,
      subject_name: subject.subject_name,
      onSuccess: async () => {
        await $fetch('/api/subjects', {
          method: 'DELETE',
          query: {
            subject_id: subject.subject_id
          }
        })
        closeModal()
      }
    }
  )
  deleted.value = !deleted.value
}

async function logout() {
  await $fetch('/api/logout', { method: 'POST' })
  await navigateTo('/login')
}

const live_time_event = ref(true)
const { data: timeInOutData, status: timeInOutStatus } = await useAsyncData<{time_in: string, time_out: string, student_name: string}[]>
    ('', () => $fetch(`/api/attendance/recent/`, {
       method: 'GET', 
       query: 
      { type: recordType.value } 
      }
    ),
    { watch: [recordType, live_time_event] }
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
    live_time_event.value = !live_time_event.value
  });
  eventSource.value.addEventListener("time_out", function(event) {
    live_time_event.value = !live_time_event.value
  })

}

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
      </div>
    </template>

  <div>
  <div class="min-h-screen">
    <!-- Main Content -->
    <div class="p-8">

      <!-- Attendance Records -->
      <div class="grid gap-8 md:grid-cols-2 items-start">
        <!-- Recent Attendance -->
        <UCard class="flex flex-col h-96">
          <div class="flex justify-between items-center mb-6 flex-shrink-0">
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
          
          <div class="overflow-auto flex-1 space-y-4">
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
        <UCard class="flex flex-col h-96">
          <div class="flex justify-between items-center mb-6 flex-shrink-0">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Subjects</h2>
            <UButton
              icon="i-heroicons-pencil-square" 
              size="sm"
              @click="openAddModal">New</UButton>
          </div>

          <div class="overflow-scroll h-64 flex-1 space-y-4">
            <div v-if="subjects && subjects.length > 0"
              v-for="subject in subjects" 
              :key="subject.subject_id" 
              class="flex items-center justify-between p-4 rounded-lg bg-gray-50 dark:bg-gray-700/50">
              <div>
                <h3 class="font-medium text-gray-900 dark:text-white">{{ subject.subject_name }}</h3>
                <p class="font-thin text-gray-900 dark:text-white">{{ subject.start_time }} to {{ subject.end_time }}</p>
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
                  @click="deleteSubject(subject)"
                  class="p-2 text-red-500 hover:text-red-700"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
            <div v-else class="text-center">
              <p class="text-gray-900 dark:text-white">No subjects found.</p>
            </div>
          </div>
        </UCard>
      </div>
      <UCard class="mt-8">
        <template #header>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            Subject Time Table
          </h2>
        </template>
        <SubjectTimeTable :subjects="subjects"/>
      </UCard>
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
            <div v-if="selectedSubject">
              <UInput
              v-model="selectedSubject.subject_name"
              type="text"
              placeholder="CMSC..." 
            />
            </div>
            <div v-else>
              <UInput
              v-model="newSubject.subject_name"
              type="text"
              placeholder="CMSC..." 
            />
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Schedule</label>
            <SubjectSchedule v-on:updateDays="handleDaysUpdate"  :current-days="selectedSubject?.schedule" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Start and End Time</label>
            <SubjectTIme v-on:update-time="handleTimeUpdate" :current-time="selectedSubject ? { start_time: selectedSubject.start_time, end_time: selectedSubject.end_time } : undefined" />
          </div>
          <AvailablePage />
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
            {{ selectedSubject ? 'Save Changes' : 'Save' }}
          </UButton>
        </div>
        </template>
      </UCard>
    </UModal>
    </div>
  </div>

    <template #footer>
    </template>
  </UCard>
</template>