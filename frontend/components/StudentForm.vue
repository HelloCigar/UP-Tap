<script setup lang="ts">
import { number, object, string, type InferType } from 'yup'
import type { FormSubmitEvent } from '#ui/types'
const route = useRoute()
const { isMobile } = useMobile()
const toast = useToast()

import * as faceapi from 'face-api.js';
const loadModels = async () => {
    const MODEL_URL = '/models'; // Local model directory
    await faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL);
    await faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL);
    await faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL);
    await faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL);
};

onMounted(() => {
    loadModels()
        .then(() => {
            console.log('Models loaded');
        })
        .catch((err) => {
            console.error('Error loading models:', err);
        });
});


const schema = object({
    student_id: number().integer().required('Student ID is required').typeError('Student ID must be a number').lessThan(1000000000, 'Student ID must be less than 10 digits'),
    first_name: string().required('First name is required'),
    middle_initial: string().optional(),
    last_name: string().required('Last name is required'),
    email: string().email('Invalid email').required('Email is required'),
    alt_email: string().email('Invalid email').optional(),
    gender: string().required('Gender is required'),
    course: string().required('Course is required'),
    face_data: string().required('Face data is required').typeError('Face data must be a file'),
})
const gender = [{
    id: 'M',
    name: 'Male'
}, {
    id: 'F',
    name: 'Female'
}] 

type Schema = InferType<typeof schema>


const state = reactive({
  student_id: undefined as number | undefined,
  first_name: undefined as string | undefined,
  middle_initial: undefined as string | undefined,
  last_name: undefined as string | undefined,
  email: undefined as string | undefined,
  alt_email: undefined as string | undefined,
  gender: undefined as string | undefined,
  course: undefined as string | undefined,
  face_data: null as File | null,
  facePreviewUrl: null as string | null,
  faceBase64: null as string | null,
})
console.log(route.params.id)
if (route.params.id) {
    const {data: student} = await useFetch<Student>(`/api/students/detail/${route.params.id}`, {method: 'GET'})
  if (student.value) {
    state.student_id = student.value.student_id
    state.first_name = student.value.first_name
    state.middle_initial = student.value.middle_initial
    state.last_name = student.value.last_name
    state.email = student.value.email
    state.alt_email = student.value.alt_email
    state.gender = student.value.gender
    state.course = student.value.course
    state.facePreviewUrl = student.value.face_data
    state.face_data =  new File([], student.value.face_data)
  }
}

const { data: subjects } = await useFetch('/api/subjects', {method: 'GET'})
const selected = ref([])

const cameraInput = ref()
// Clear the selected photo
function clearPhoto() {
  state.face_data = null
}

const photoLoader = ref(false)
async function onFileSelected(files: FileList) {
  photoLoader.value = true
  if (!files[0]) return
  const file = files[0]

  // 2. Create an HTMLImageElement from the File
  const img = await new Promise<HTMLImageElement>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const image = new Image()
      image.src = reader.result as string
      image.onload = () => resolve(image)
      image.onerror = reject
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })

  // 3. Detect a single face with TinyFaceDetector (fast)
  const detection = await faceapi
    .detectSingleFace(img, new faceapi.TinyFaceDetectorOptions())
    .withFaceLandmarks()
    .withFaceDescriptor()

  if (!detection) {
    // No face found → clear and alert the user
    state.face_data = null
    state.facePreviewUrl = null
    photoLoader.value = false
    return alert('No face detected in that photo. Please try again.')
  }

  // 4. Crop the face region
  const { x, y, width, height } = detection.detection.box
  const offscreen = document.createElement('canvas')
  offscreen.width = width
  offscreen.height = height
  const ctx = offscreen.getContext('2d')!
  ctx.drawImage(img, x, y, width, height, 0, 0, width, height)

  // 5. Turn the cropped canvas into a Blob and URL
  const dataUrl = offscreen.toDataURL('image/jpeg')
  // dataUrl looks like "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."

  // 6. Update your state
  state.face_data       = file                   // if you still need the original File
  state.facePreviewUrl  = dataUrl                // for <img :src="..." />
  photoLoader.value = false
}

function openCamera() {
  const el = cameraInput.value?.$el
  if (el) {
    const input = el.querySelector('input[type=file]')
    input?.click()
  }
}

const formRef = ref()
const submitState = ref(false)
async function onSubmit(event: FormSubmitEvent<Schema>) {
  submitState.value = true
  // Do something with event.data
  await $fetch('/api/students/register', {
    method: 'POST',
    body: {
        student_id: state.student_id,
        first_name: state.first_name,
        middle_initial: state.middle_initial,
        last_name: state.last_name,
        email: state.email,
        alt_email: state.alt_email,
        gender: state.gender,
        course: state.course,
        face_data: state.facePreviewUrl,
        subject_ids: selected.value,
    },
  }).then((res) => {
    toast.add({
        title: 'Success',
        color: 'green',
        description: 'Student registered successfully.',
        icon: 'i-heroicons-check-circle-20-solid',
    })
    //reset states
    state.student_id = undefined
    state.first_name = undefined
    state.middle_initial = undefined
    state.last_name = undefined
    state.email = undefined
    state.alt_email = undefined 
    state.gender = undefined
    state.course = undefined
    state.face_data = null
    state.facePreviewUrl = null
    state.faceBase64 = null
    selected.value = []
    if (route.params.id) {
        // Redirect to the student list page
        navigateTo('/dashboard/student')
    }
  }).catch((err) => {
    toast.add({
        title: 'Error',
        color: 'red',
        description: 'An error occurred while registering the student.',
        icon: 'i-heroicons-x-circle-20-solid',
    })
  }).finally(() => {
    submitState.value = false
  })
}
</script>

<template>
    <UForm :schema="schema" :state="state" ref="formRef" @submit="onSubmit">
        <UCard>
            <template #header>
                <h3 class="text-2xl font-semibold leading-none tracking-tight">
                    Student Information
                </h3>
            </template>
                <div className="space-y-2">
                    <UFormGroup label="Student ID" name="student_id" required
                        description="The UP ID number assigned by the university. No dashes or spaces.">
                        <UInput placeholder="ex: 2021*****" icon="i-heroicons-identification" v-model="state.student_id"/>
                    </UFormGroup>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <UFormGroup label="First Name" name="first_name" required>
                            <UInput placeholder="Juan" icon="i-heroicons-user-circle" v-model="state.first_name"/>
                        </UFormGroup>
                        <UFormGroup label="Middle Initial" name="middle_initial">
                            <UInput placeholder="C" icon="i-heroicons-user-circle" v-model="state.middle_initial"/>
                        </UFormGroup>
                        <UFormGroup label="Last Name" name="last_name" required>
                            <UInput placeholder="Dela Cruz" icon="i-heroicons-user-circle" v-model="state.last_name"/>
                        </UFormGroup>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormGroup label="Email" name="email" description="Your personal email." required>
                            <UInput placeholder="you@example.com" icon="i-heroicons-envelope" v-model="state.email"/>
                        </UFormGroup>
                        <UFormGroup label="UP Email" name="alt_email" description="Your UP email.">
                            <UInput placeholder="you@up.edu.ph" icon="i-heroicons-envelope" v-model="state.alt_email"/>
                        </UFormGroup>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormGroup label="Gender" name="gender" required>
                            <USelectMenu v-model="state.gender" :options="gender" placeholder="Male or Female" 
                                value-attribute="id"
                                option-attribute="name" />
                        </UFormGroup>
                        <UFormGroup label="Course" name="course" required>
                            <UInput placeholder="BS in Computer Science" icon="i-heroicons-building-library-solid" v-model="state.course"/>
                        </UFormGroup>
                    </div>
                    <div class="space-y-2">
                        <UFormGroup label="Face Data" name="face_data" required>
                        <div class="flex flex-col items-center space-y-4">
                        <!-- If we already have a photo -->
                        <div v-if="state.face_data" class="relative">
                            <img
                            :src="state.facePreviewUrl || '/placeholder.svg'"
                            alt="Student photo"
                            class="w-48 h-48 object-cover rounded-md border"
                            />
                            <UButton
                            variant="solid"
                            size="sm"
                            class="absolute top-2 right-2"
                            @click="clearPhoto"
                            >
                            Change
                            </UButton>
                        </div>

                        <!-- Otherwise show upload/take-photo buttons -->
                        <div v-else class="flex flex-col md:flex-row space-y-2 md:space-y-0 md:space-x-2">
                            <!-- Only on mobile, show camera-capture -->
                            <UButton
                            @click="openCamera"
                            :loading="photoLoader"
                            variant="outline"
                            icon="i-heroicons-camera-20-solid"
                            :label="photoLoader ? 'Finding face...' : isMobile ? 'Take Photo' : 'Upload Photo'"
                            >
                            </UButton>

                            <!-- Hidden inputs -->
                            <UInput
                            type="file"
                            ref="cameraInput"
                            accept="image/*"
                            capture="environment"
                            @change="onFileSelected"
                            class="hidden"
                            />
                        </div>
                        </div>
                        </UFormGroup>
                    </div>
                    <UFormGroup label="Subject Enrollment" name="subjects" required>
                        <USelectMenu v-if="subjects" v-model="selected" :options="subjects" multiple placeholder="Select the subjects you are enrolled in." value-attribute="subject_id" option-attribute="subject_name"/>
                    </UFormGroup>
                </div>
                
            <template #footer>
                <div class="flex"
                    :class="{
                        'justify-between': route.params.id,
                        'justify-end': !route.params.id,
                    }">
                    <UButton type="button" variant="outline" size="sm" icon="i-heroicons-x-circle-20-solid" @click="$router.back()" v-if="route.params.id">
                        Back
                    </UButton>
                    <UButton type="submit" variant="solid" size="sm" icon="i-heroicons-check-circle-20-solid" :loading="submitState" :disabled="selected.length === 0">
                        {{ route.params.id ? 'Update' : 'Register' }}
                    </UButton>
                </div>
            </template>
        </UCard>
    </UForm>
</template>

