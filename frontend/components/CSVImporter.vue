<script setup lang="ts">
import type { FormError, FormSubmitEvent } from '#ui/types'

const props = defineProps({
    subject_id: Number,
    subject_name: String
})
const isOpen = ref(false)

const requiredFields = ["last_name", "first_name", "middle_initial", "student_id", "gender", "course", "email", "alt_email"];

const state = reactive({
  csvfile: undefined as File | undefined
});

async function onFileSelected(files: FileList) {
    state.csvfile = files[0]
}

const validate = async (state: any): Promise<FormError[]> => {
  const errors = []
  if (!state.csvfile) errors.push({ path: 'csvfile', message: 'Required' })

    try {
        const { valid, missingFields, parsedFields } =
        await validateCsvFields(state.csvfile, requiredFields, {
            delimiter: ',',        // default is auto-detect
            encoding: 'UTF-8',
        });

        if (!valid) {
        errors.push({ path: 'csvfile', message: 'Missing required fields: ' + missingFields.join(', ') + '.' })
        } else {
        console.log('All required fields present:', parsedFields);
        // proceed to full-parse or upload...
        }
    } catch (err) {
        errors.push({ path: 'csvfile', message: 'Invalid CSV file.' })
    }
  return errors
}

const toast = useToast()
const loading = ref(false)
async function onSubmit(event: FormSubmitEvent<any>) {
  loading.value = true
  // Do something with data
  const formData = new FormData()
  formData.append('csvfile', event.data.csvfile)

  await $fetch('/api/teachers/upload-classlist', {
    method: 'POST',
    body: formData,
    query: {
      subject_id: props.subject_id
    }
  }).then((res) => {
    loading.value = false
    toast.add({
      title: 'Class list uploaded successfully',
      description: res.message,
      color: 'green',
    })
    isOpen.value = false
  }).catch((error) => {
    toast.add({
      title: 'Error uploading class list',
      description: error.message,
      color: 'red',
    })
  })
}

</script>

<template>
  <div>
    <UButton size="sm" icon="i-heroicons-document-arrow-up-16-solid" label="Class List" @click="isOpen = true" variant="outline"/>

    <UModal v-model="isOpen">
      <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
            <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
                Import your CRS class list for {{ subject_name }}
            </h3>
        </template>
        <UForm :validate="validate" :state="state" class="space-y-4" @submit="onSubmit">
            <UFormGroup label="Classlist in CSV format" name="csvfile" description="Fields: last_name, first_name, middle_initial, student_id, gender, course, email, alt_email(UP Mail)" required>
                <UInput type="file" size="sm" id="csvfile" icon="i-heroicons-folder" accept=".csv" @change="onFileSelected"/>
            </UFormGroup>
            <div class="flex justify-center">
                <UButton type="submit" :disabled="!state.csvfile" :loading="loading">
                    Import
                </UButton>
            </div>
        </UForm>
      </UCard>
    </UModal>
  </div>
</template>

