<script setup lang="ts">
definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

import DateRangePicker from '~/components/DateRangePicker.vue'
const datePicker = ref()

const columns = [{
  key: 'student_name',
  label: 'Student',
}, {
  key: 'subject_name',
  label: 'Subject',
}, {
  key: 'is_present',
  label: 'Status',
},
{
  key: 'session_date',
  label: 'Date',
},
{
  key: 'time_in',
  label: 'Time In',
}, {
  key: 'time_out',
  label: 'Time Out',
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
const selectedSections = ref<string[]>([])
import { subDays } from 'date-fns'
const startDate = ref<Date>(subDays(new Date(), 7))
const endDate = ref<Date>(new Date())

function handleDateRangeChange(range: { start: Date, end: Date }) {
  startDate.value = range.start
  endDate.value = range.end
}

function resetFilters() {
  console.log(selectedStatus.value)
  console.log(selectedSubjects.value)
  search.value = ''
  selectedStatus.value = []
  selectedSubjects.value = []
  datePicker.value.resetSelected()
  selectedSections.value = []
}

// Data
const { data: attendanceRecords, status } = await useAsyncData<AttendanceRecord[] | QueryError>('attendance', () => ($fetch as any)('/api/attendance/', {
  method: 'POST',
  query: {
    q: search.value,
    start_date: startDate.value.toLocaleDateString('en-CA'),
    end_date: endDate.value.toLocaleDateString('en-CA'),
  },
  body:{
    is_present: selectedStatus.value.length > 0 ? selectedStatus.value : undefined,
    subject_ids: selectedSubjects.value.length > 0 ? selectedSubjects.value : undefined,
    sections: selectedSections.value.length > 0 ? selectedSections.value : undefined,
  },
}), {
  watch: [search, selectedStatus, selectedSubjects, startDate, endDate],
})

const { data: subjects } = await useFetch<Subjects[]>('/api/teachers/subjects', { method: 'GET' } )

const subjectSectionsMap = computed(() => {
  if (!subjects.value || ('success' in subjects.value && subjects.value.success === false)) return new Map()

  const map = new Map<number, Set<string>>()

  subjects.value.forEach((subject) => {
    const id = subject.subject_id
    const section = subject.section ?? ''
    if (!map.has(id)) {
      map.set(id, new Set())
    }
    if (section) {
      map.get(id)?.add(section)
    }
  })

  return new Map(
    Array.from(map.entries()).map(([id, sections]) => [id, Array.from(sections)])
  )
})


const calculateStats = computed(() => {

  if (!attendanceRecords.value || 'success' in attendanceRecords.value &&  attendanceRecords.value.success == false) return { uniqueSessions: 0, presentCount: 0, absentCount: 0, attendanceRate: 0 }

  if(!Array.isArray(attendanceRecords.value)) return { uniqueSessions: 0, presentCount: 0, absentCount: 0, attendanceRate: 0 }
  const uniqueSessions = new Set(attendanceRecords.value.map((r) => r.sheet_id)).size
  const presentCount = attendanceRecords.value.filter((r) => r.is_present).length
  const absentCount = attendanceRecords.value.filter((r) => !r.is_present).length
  const totalRecords = attendanceRecords.value.length

  const attendanceRate = ((presentCount / totalRecords) * 100).toFixed(2)

  return {
    uniqueSessions: uniqueSessions,
    presentCount,
    absentCount,
    attendanceRate
  }
})

function downloadPDFReport() {
  // Pass in the current records and date range
  generatePDF(
    attendanceRecords.value as AttendanceRecord[],
    startDate.value,
    endDate.value
  )
}

function downloadCsv() {
  // cast to correct type
  const records = attendanceRecords.value as AttendanceRecord[]
  generateCSV(records)
}

const disableDownload = computed(() => {
  return !attendanceRecords.value || 'success' in attendanceRecords.value &&  attendanceRecords.value.success == false
})

const items = [
  [{
    label: 'Export CSV',
    icon: 'i-heroicons-document-text-solid',
    click: () => {
      downloadCsv()
    },
    disabled: disableDownload.value,
  }, {
    label: 'Download PDF',
    icon: 'i-heroicons-document-arrow-down',
    click: () => {
      downloadPDFReport()
    },
    disabled: disableDownload.value
  }]]



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
              {{ calculateStats.uniqueSessions }}
            </h4>
        </UCard>
        <UCard>
            <p class="text-gray-700 dark:text-gray-300">Present</p>
            <h4 class="text-lg font-bold">
              {{ calculateStats.presentCount }}
            </h4>
        </UCard>
        <UCard>
            <p class="text-gray-700 dark:text-gray-300">No Time Out</p>
            <h4 class="text-lg font-bold">
              {{ calculateStats.absentCount }}
            </h4>
        </UCard>
        <UCard>
            <p class="text-gray-700 dark:text-gray-300">Attendance Rate</p>
            <h4 class="text-lg font-bold">
              {{ calculateStats.attendanceRate }}%
            </h4>
          </UCard>
      </div>

      <!-- search -->
      <div class="flex items-center justify-between gap-3 py-6">
        <UInput v-model="search" icon="i-heroicons-magnifying-glass-20-solid" placeholder="Search..." />
        <div class="flex items-center gap-3">
          <USelectMenu v-model="selectedStatus" :options="statusOptions" placeholder="Status" multiple value-attribute="value" class="w-40" />
          <USelectMenu 
            v-if="subjects" 
            v-model="selectedSubjects" 
            :options="subjects" 
            placeholder="Subject" 
            multiple 
            value-attribute="subject_id" 
            option-attribute="subject_name" 
            class="w-40">

            <template #option="{ option: subject }">
              <span class="truncate">{{ subject.subject_name }} -  Section {{ subject.section[0].name }}</span>
          </template>
          </USelectMenu>
          <!-- <USelectMenu v-if="subjectSectionsMap" v-model="selectedSections" :disabled="selectedSubjects.length !== 1" :options="subjectSectionsMap.get(selectedSubjects[0])" placeholder="Section" multiple class="w-40"/> -->
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
        </div>

      <div class="flex gap-1.5 items-center">
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
          
          :disabled="search === '' && selectedStatus.length === 0 && selectedSubjects.length === 0 && startDate === subDays(new Date(), 7) && endDate === new Date()"
          @click="resetFilters"
        >
          Reset
        </UButton>
        <UDropdown :items="items" :popper="{ placement: 'bottom-start' }">
          <UButton color="white" size="xs" label="Download/Export" trailing-icon="i-heroicons-arrow-right-circle-16-solid" :disabled="disableDownload"/>
        </UDropdown>
        
      </div>
      </div>
      <template #footer class="w-full h-full">
        <UTable
          :rows="attendanceRecords"
          :columns="columnsTable"
          :loading="status === 'pending'"
          sort-asc-icon="i-heroicons-arrow-up"
          sort-desc-icon="i-heroicons-arrow-down"
          :ui="{ td: { base: 'max-w-[0] truncate' }, default: { checkbox: { color: 'gray' as any } } }"
          
        >
          <template #is_present-data="{ row }">
            <UBadge size="xs" :label="row.is_present ? 'Present' : 'No Time Out'" :color="row.is_present ? 'emerald' : 'red'" variant="subtle" />
          </template>
        </UTable>
      </template>
    </UCard>
</template>