<script setup lang="ts">
definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

import { is } from 'date-fns/locale'
import DateRangePicker from '~/components/DateRangePicker.vue'
const datePicker = ref()

const columns = [{
  key: 'student_name',
  label: 'Student',
  sortable: true
}, {
  key: 'subject_name',
  label: 'Subject',
  sortable: true
}, {
  key: 'session_date',
  label: 'Date',
  sortable: true,
}, {
  key: 'is_present',
  label: 'Status',
  sortable: true
},
{
  key: 'time_in',
  label: 'Time In',
  sortable: true
}, {
  key: 'time_out',
  label: 'Time Out',
  sortable: true
}]



const selectedColumns = ref(columns)
const columnsTable = computed(() => columns.filter(column => selectedColumns.value.includes(column)))
const excludeSelectColumn = computed(() => columns.filter(v => v.key !== 'select'))

const statusOptions = [{
  key: 'present',
  label: 'Present',
  value: true
}, {
  key: 'no_time_out', 
  label: 'No Time Out',
  value: false
}]

const search = ref('')
const selectedStatus = ref<boolean[]>([])
const selectedSubjects = ref<number[]>([])
const startDate = ref<Date>(new Date())
const endDate = ref<Date>(new Date())

function handleDateRangeChange(range: { start: Date, end: Date }) {
  startDate.value = range.start
  endDate.value = range.end
  console.log('Selected date range:', startDate.value, endDate.value)
}

function resetFilters() {
  console.log(selectedStatus.value)
  console.log(selectedSubjects.value)
  search.value = ''
  selectedStatus.value = []
  selectedSubjects.value = []
  datePicker.value.resetSelected()
}

// Data
const { data: attendanceRecords, status } = await useAsyncData<AttendanceRecord[]>('attendance', () => ($fetch as any)('/api/attendance/', {
  method: 'POST',
  query: {
    q: search.value,
    start_date: startDate.value.toLocaleDateString('en-CA'),
    end_date: endDate.value.toLocaleDateString('en-CA'),
  },
  body:{
    is_present: selectedStatus.value.length > 0 ? selectedStatus.value : undefined,
    subject_ids: selectedSubjects.value.length > 0 ? selectedSubjects.value : undefined,
  },
}), {
  watch: [search, selectedStatus, selectedSubjects, startDate, endDate],
})

const { data: subjects } = await useFetch<Subjects[]>('/api/teachers/subjects', { method: 'GET' } )
</script>



<template>
    <UCard>
      <template #header>
        <h2 class="font-semibold text-xl text-gray-900 dark:text-white leading-tight">
          Reports
        </h2>
      </template>

      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <UCard>
            <p class="text-gray-700 dark:text-gray-300">Total Sessions</p>
            <h4 class="text-lg font-bold">
              1,234
            </h4>
        </UCard>
        <UCard>
            <p class="text-gray-700 dark:text-gray-300">Present</p>
            <h4 class="text-lg font-bold">
              1,234
            </h4>
        </UCard>
        <UCard>
            <p class="text-gray-700 dark:text-gray-300">Absent</p>
            <h4 class="text-lg font-bold">
              1,234
            </h4>
        </UCard>
        <UCard>
            <p class="text-gray-700 dark:text-gray-300">Attendance Rate</p>
            <h4 class="text-lg font-bold">
              1,234
            </h4>
          </UCard>
      </div>

      <!-- search -->
      <div class="flex items-center justify-between gap-3 py-6">
        <UInput v-model="search" icon="i-heroicons-magnifying-glass-20-solid" placeholder="Search..." />
        <div class="flex items-center gap-3">
          <USelectMenu v-model="selectedStatus" :options="statusOptions" placeholder="Status" multiple value-attribute="value" class="w-40" />
          <USelectMenu v-model="selectedSubjects" :options="subjects" placeholder="Subject" multiple value-attribute="subject_id" option-attribute="subject_name" class="w-40"/>
          <DateRangePicker @selectedRange="handleDateRangeChange" ref="datePicker" />
        </div>
      </div>

      <div class="flex justify-between items-center w-full py-3">
        <div class="flex items-center gap-1.5">
          <span class="text-sm leading-5">Rows per page:</span>

          <USelect
            :options="[3, 5, 10, 20, 30, 40]"
            class="me-2 w-20"
            size="xs"
          />
          <!-- v-model="pageCount" -->

        </div>

      <div class="flex gap-1.5 items-center">
        <UDropdown 
          :ui="{ width: 'w-36' }">
          <!-- v-if="selectedRows.length > 1" :items="actions"  -->
          <UButton
            icon="i-heroicons-chevron-down"
            trailing
            color="gray"
            size="xs"
          >
            Mark as
          </UButton>
        </UDropdown>

        <USelectMenu v-model="selectedColumns" :options="excludeSelectColumn" multiple>
          <UButton
            icon="i-heroicons-view-columns"
            color="gray"
            size="xs"
          >
            Columns
          </UButton>
        </USelectMenu>

        <UButton
          icon="i-heroicons-funnel"
          color="gray"
          size="xs"
          
          :disabled="search === '' && selectedStatus.length === 0 && selectedSubjects.length === 0 && startDate === new Date() && endDate === new Date()"
          @click="resetFilters"
        >
          Reset
        </UButton>
      </div>
      </div>
      <template #footer class="w-full h-full">
        <UTable
          :rows="attendanceRecords"
          :columns="columnsTable"
          :loading="status === 'pending'"
          sort-asc-icon="i-heroicons-arrow-up"
          sort-desc-icon="i-heroicons-arrow-down"
          sort-mode="manual"
          :ui="{ td: { base: 'max-w-[0] truncate' }, default: { checkbox: { color: 'gray' as any } } }"
          
        >
          <template #is_present-data="{ row }">
            <UBadge size="xs" :label="row.is_present ? 'Present' : 'No Time Out'" :color="row.is_present ? 'emerald' : 'red'" variant="subtle" />
          </template>
        </UTable>
      </template>
    </UCard>
</template>