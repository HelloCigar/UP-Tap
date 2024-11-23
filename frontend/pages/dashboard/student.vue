<script lang="ts" setup>

definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})
// Columns
const columns = [{
  key: 'student_id',
  label: 'RFID #',
  sortable: true
}, {
  key: 'first_name',
  label: 'First Name',
  sortable: true
}, {
  key: 'last_name',
  label: 'Last Name',
  sortable: true
}, {
  key: 'email',
  label: 'Email',
  sortable: true
}, {
  key: 'actions'
}
]

const selectedColumns = ref(columns)
const columnsTable = computed(() => columns.filter((column) => selectedColumns.value.includes(column)))
const onDelete = ref(false)
// Actions
const actions = [
  [{
    key: 'completed',
    label: 'Completed',
    icon: 'i-heroicons-check'
  }], [{
    key: 'uncompleted',
    label: 'In Progress',
    icon: 'i-heroicons-arrow-path'
  }]
]

const {data: subjects} = await useFetch<Subjects[]>('/api/teachers/subjects', { method: 'GET' } )

// Filters
const todoStatus = [{
  key: 'uncompleted',
  label: 'In Progress',
  value: false
}, {
  key: 'completed',
  label: 'Completed',
  value: true
}]

const search = ref('')
const selectedSubjects = ref<number[]>([
])

const resetFilters = () => {
  search.value = ''
  selectedSubjects.value = []
}

const refreshAfterRegister = ref(false)
function registerDone (value: boolean){
  refreshAfterRegister.value = !refreshAfterRegister.value
}
// Pagination
const sort = ref({ column: 'student_id', direction: 'asc' as const })
const page = ref(1)
const pageCount = ref(10)
const { data: pageTotal, status: pageStatus } = await useAsyncData<StudentQueryResponse>('count',
  () => $fetch('/api/students/', {
    method: 'GET',
  }),
  {
    watch: [page, search, pageCount, sort, selectedSubjects, refreshAfterRegister, onDelete]
  }
)
const pageFrom = computed(() => (page.value - 1) * pageCount.value + 1)
const pageTo = computed(() => Math.min(page.value * pageCount.value, pageTotal.value.count))
// Data
const { data: students, status } = await useAsyncData<StudentQueryResponse>('students', () => ($fetch as any)('/api/students/', {
  query: {
    q: search.value,
    offset: (page.value - 1) * pageCount.value,
    limit: pageCount.value,
    sort: sort.value.column,
    order: sort.value.direction,
    subjects: JSON.stringify(selectedSubjects.value)
  }
}), {
  default: () => { return { items: [], count: 0 } },
  watch: [page, search, pageCount, sort, selectedSubjects, refreshAfterRegister, onDelete ],
})

// Selected Rows
const selectedRows = ref<Student[]>([])

function select (row: Student) {
  const index = selectedRows.value.findIndex((item) => item.student_id === row.student_id)
  if (index === -1) {
    selectedRows.value.push(row)
  } else {
    selectedRows.value.splice(index, 1)
  }
}


import { StudentDeleteModal, StudentEdit } from '#components'
const modal = useModal()
const items = (row: Student) => [
  [{
    label: 'Edit',
    icon: 'i-heroicons-pencil-square-20-solid',
    click: () => {
      modal.open(StudentEdit, { 
        student_id: row.student_id,
        first_name: row.first_name,
        last_name: row.last_name,
        email: row.email, 
        onSuccess: () => {
           refreshAfterRegister.value = !refreshAfterRegister.value 
           onDelete.value = !onDelete.value
          } 
        })
    }
  }], [{
    label: 'Delete',
    icon: 'i-heroicons-trash-20-solid',
    click: () => {
      modal.open(StudentDeleteModal, {
        student_id: row.student_id,
        first_name: row.first_name,
        last_name: row.last_name,
        onSuccess: () => {
          selectedRows.value = selectedRows.value.filter((item) => item.student_id !== row.student_id)
          onDelete.value = !onDelete.value
        }
      })
    }
  }]
]

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
    }"
  >
    <template #header>
      <div class="flex justify-between items-center w-full">
        <h2 class="font-semibold text-xl text-gray-900 dark:text-white leading-tight">
          Students
        </h2>
        <StudentRegister @register-done="registerDone" />
      </div>
    </template>

    <!-- Filters -->
    <div class="flex items-center justify-between gap-3 px-4 py-3">
      <UInput v-model="search" icon="i-heroicons-magnifying-glass-20-solid" autofocus placeholder="Search..." />

      <USelectMenu v-if="subjects" v-model="selectedSubjects" :options="subjects" multiple placeholder="Subject" class="w-40" value-attribute="subject_id" option-attribute="subject_name"/>
    </div>

    <!-- Header and Action buttons -->
    <div class="flex justify-between items-center w-full px-4 py-3">
      <div class="flex items-center gap-1.5">
        <span class="text-sm leading-5">Rows per page:</span>

        <USelect
          v-model="pageCount"
          :options="[3, 5, 10, 20, 30, 40]"
          class="me-2 w-20"
          size="xs"
        />
      </div>

      <div class="flex gap-1.5 items-center">
        <UDropdown v-if="selectedRows.length > 1" :items="actions" :ui="{ width: 'w-36' }">
          <UButton
            icon="i-heroicons-chevron-down"
            trailing
            color="gray"
            size="xs"
          >
            Actions
          </UButton>
        </UDropdown>

        <USelectMenu v-model="selectedColumns" :options="columns" multiple>
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
          :disabled="search === '' && selectedSubjects.length === 0"
          @click="resetFilters"
        >
          Reset
        </UButton>
      </div>
    </div>

    <!-- Table -->
    <UTable
        v-model="selectedRows"
        v-model:sort="sort"
        :rows="students?.items"
        :columns="columnsTable"
        :loading="status === 'pending'"
        sort-asc-icon="i-heroicons-arrow-up"
        sort-desc-icon="i-heroicons-arrow-down"
        sort-mode="manual"
        class="min-w-full"
        :ui="{ td: { base: 'max-w-[0] truncate' }, default: { checkbox: { color: 'gray' as any } }, wrapper: 'h-[650px] overflow-y-auto' }"
    >
        <template #actions-data="{ row }">
          <UDropdown :items="items(row)">
            <UButton color="gray" variant="ghost" icon="i-heroicons-ellipsis-horizontal-20-solid" />
          </UDropdown>
        </template>
    </UTable>


    <!-- Number of rows & Pagination -->
    <template #footer>
      <div class="flex flex-wrap justify-between items-center">
        <div>
          <span class="text-sm leading-5">
            Showing
            <span class="font-medium">{{ pageFrom }}</span>
            to
            <span class="font-medium">{{ pageTo }}</span>
            of
            <span class="font-medium">{{ pageTotal?.count }}</span>
            results
          </span>
        </div>

        <UPagination
          v-if="students"
          v-model="page"
          :page-count="pageCount"
          :total="pageTotal?.count"
          :ui="{
            wrapper: 'flex items-center gap-1',
            rounded: '!rounded-full min-w-[32px] justify-center',
            default: {
              activeButton: {
                variant: 'outline'
              }
            }
          }"
        />
      </div>
    </template>
  </UCard>
</template>