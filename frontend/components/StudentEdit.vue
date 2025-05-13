<script setup lang="ts">

const props = defineProps({
    student_id: Number,
    first_name: String,
    last_name: String,
    email: String 
})

import { object, string, type InferType } from 'yup'
import type { FormSubmitEvent } from '#ui/types'
import { RegisterModal } from '#components'

const isOpen = ref(false)
const {data: subjects} = await useFetch<Subjects[]>('/api/subjects', { method: 'GET' } )
const selectedSubjects = ref<number[]>([])
const emit = defineEmits(['success'])
const modal = useModal()
const rfidNumber = ref("");
const selectedTab = ref(0)


const schema = object({
  email: string().email('Invalid email').required('Required'),
  first_name: string().required('Required'),
  last_name: string().required('Required'),
})
type Schema = InferType<typeof schema>
const state = reactive({
  student_id: props.student_id,
  email: props.email,
  first_name: props.first_name,
  last_name: props.last_name,
})

async function onSubmit (event: FormSubmitEvent<Schema>) {
  // Do something with event.data
  console.log(event.data)
}
function nextTab() {
    if(selectedTab.value > 3){
        return
    }
    selectedTab.value++
}

const allowNext = computed(() => !(state.email && state.first_name && state.last_name));

watch(rfidNumber, (newVal) => { if (newVal.length === 10) nextTab(); });

watch(selectedTab, (newVal) => { if (newVal === 1) rfidNumber.value = ''; });

watch(isOpen, (newVal) => { if (!newVal) resetForm(); });

function resetForm() {
  rfidNumber.value = ''
  state.first_name = undefined
  state.last_name = undefined
  state.email = undefined
  photo.value = ''
  base64String.value = ''
  selectedSubjects.value = []
  selectedTab.value = 0
  emit('success')
}



const registerResult = ref<{success: boolean, message: string}>()
const faceDetected = ref(false); // Reactive variable to track face detection status
const photo = ref('')

async function registerStudent() {
  if(base64String.value != '') {
    registerResult.value = await $fetch('/api/students/', {
      method: 'PUT',
      body: {
        student_id: state.student_id,
        first_name: state.first_name,
        last_name: state.last_name,
        email: state.email,
        face_data: base64String.value,
      },
      credentials: 'include',
      query: {
        student_id_old: props.student_id,
        subjects: JSON.stringify(selectedSubjects.value),
        rfid: rfidNumber.value
      }
    })
    if(registerResult.value) handleRegisterResult()
  }
}

function handleRegisterResult() {
  const { success, message } = registerResult.value || {};
  emit('success')
  modal.open(RegisterModal, { title: success ? "Success" : "Error", message: message });
}

// Handle the emitted value from the child component
const handleFaceDetection = (detected: boolean) => {
  faceDetected.value = detected; // Update the reactive variable based on emitted value
};

// Handle the emitted Blob URL from the child component
const handlePhotoTaken = (photoURL: string) => {
  photo.value = photoURL; // Update the photo reactive variable with the Blob URL
  convertBlobToBase64(photo.value)
};

const faceDetection = ref(null); // Ref to access the child component
// Trigger photo capture by calling the `capturePhoto` method in the child component
const triggerCapture = () => {
  faceDetection.value.capturePhoto();
}

const base64String = ref('')

// Method to fetch blob and convert to base64
const convertBlobToBase64 = (fileBlobUrl: string) => {
  fetch(fileBlobUrl)
    .then((response) => response.blob())
    .then((blob) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        base64String.value = reader.result;
      };
      reader.readAsDataURL(blob);
    })
    .catch((error) => {
      console.error('Error fetching the blob:', error);
    });
};


const items = [{
  label: '1. Personal Information',
  icon: 'i-heroicons-information-circle',
}, {
  label: '2. UP RFID',
  icon: 'i-heroicons-identification',
}, {
  label: '3. Face Data',
  icon: 'i-heroicons-face-smile',
}]

</script>

<template>
    <UModal fullscreen>
      <UCard
        :ui="{
          base: 'h-full flex flex-col',
          rounded: '',
          divide: 'divide-y divide-gray-100 dark:divide-gray-800',
          body: {
            base: 'grow'
          }
        }"
      >
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
              Edit student information
            </h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" class="-my-1" @click="modal.close()" />
          </div>
        </template>

        <UContainer>
            <div class="w-full flex flex-col">
                <div class="w-full flex flex-col gap-y-4">
                    <UTabs v-model="selectedTab" :items="items" />
                    <UDivider />
                    <div v-if="selectedTab === 0" class="flex flex-col gap-y-4 w-1/2">
                        <UForm :schema="schema" :state="state" class="space-y-4" @submit="onSubmit">
                            <UFormGroup label="Student ID" name="student_id" description="The student number assigned by the university" required>
                                <UInput v-model="state.student_id" />
                            </UFormGroup>
                            <UFormGroup label="Email" name="email" required>
                                <UInput v-model="state.email" />
                            </UFormGroup>

                            <UFormGroup label="First Name" name="first_name" required>
                                <UInput v-model="state.first_name" />
                            </UFormGroup>

                            <UFormGroup label="Last Name" name="last_name" required>
                                <UInput v-model="state.last_name" />
                            </UFormGroup>
                            <USelectMenu v-model="selectedSubjects" :options="subjects" multiple placeholder="Select subjects" class="w-40" value-attribute="subject_id" option-attribute="subject_name"/>
                            <UButton :disabled="allowNext" size="sm" @click="nextTab" label="Next">
                              <template #leading>
                                <UIcon name="i-heroicons-arrow-right-circle-16-solid" class="w-5 h-5"/>
                              </template>
                            </UButton>
                        </UForm>
                    </div>
                    <div v-if="selectedTab === 1">
                        <div class="flex flex-col w-full items-center justify-center">
                            <NuxtImg src="/images/RFID.png" width="500"/>
                            <div class="w-36">
                                <UInput color="white" v-model="rfidNumber" variant="outline" autofocus ref="rfidRef" placeholder="Your RFID number..." /> 
                            </div>
                        </div>
                    </div>
                    <div v-if="selectedTab === 2">
                        <div v-if="!photo" class="flex flex-col w-full items-center justify-center gap-y-4">
                            <h3 v-if="faceDetected" class="text-base font-semibold leading-6 text-green-600 dark:text-white">
                                Face detected
                            </h3>
                            <h3 v-else class="text-base font-semibold leading-6 text-red-400 dark:text-white">
                                No face detected
                            </h3>
                            <FaceDetector ref="faceDetection" @face-detected="handleFaceDetection" @photo-taken="handlePhotoTaken" :is-open="isOpen"/>
                            <UButton @click="triggerCapture" :disabled="!faceDetected" label="Take a photo">
                              <template #leading>
                                <UIcon name="i-heroicons-camera-16-solid" class="w-5 h-5"/>
                              </template>
                            </UButton>
                        </div>
                        <div v-else class="flex flex-col w-full items-center justify-center gap-y-4">
                            <h3 class="text-base font-semibold leading-6 text-green-600 dark:text-white">
                                Photo taken
                            </h3>
                            <img :src="photo" alt="Captured photo" />
                            <UButton @click="photo = ''" label="Retake">
                              <template #leading>
                                <UIcon name="i-heroicons-arrow-path-rounded-square-solid" class="w-5 h-5"/>
                              </template>
                            </UButton>
                            <UDivider label="OR" class="w-64"></UDivider>
                            <UButton v-if="base64String != ''" @click="registerStudent" label="Upload and Finish">
                              <template #leading>
                                <UIcon name="i-heroicons-cloud-arrow-up-20-solid" class="w-5 h-5"/>
                              </template>
                            </UButton>
                            <UProgress v-else animation="swing" />
                        </div>
                    </div>
                </div>
            </div>
        </UContainer>
      </UCard>
    </UModal>
</template>

