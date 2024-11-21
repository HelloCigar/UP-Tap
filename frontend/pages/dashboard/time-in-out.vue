<script setup lang="ts">
definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})
import Camera from 'simple-vue-camera';
// Get a reference of the component
const camera = ref<InstanceType<typeof Camera>>();

const snapshot = async () => {
  const blob = await camera.value?.snapshot();

  if (blob) {
    return new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64String = reader.result as string;
        resolve(base64String);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }
};

  
const {data: subjects} = await useFetch<Subjects[]>('/api/teachers/subjects')
const chosenSub = ref<number>(subjects.value[0].subject_id)

const items = [{
  key: 'time-in',
  label: 'Time in',
  icon: 'i-heroicons-arrow-left-on-rectangle',
}, {
  key: 'time-out',
  label: 'Time out',
  icon: 'i-heroicons-arrow-left-start-on-rectangle',
}]

const time_in_out = ref('time-in')
function onChangeTab (index: number) {
  const item = items[index]
  rfidRef.value.$refs.input.focus()
  time_in_out.value = item.key
}

const rfidNumber = ref(""); // Holds the string input
function to12HourFormat(time: string): string {
  const [hours, minutes] = time.split(":").map(Number);
  
  const suffix = hours >= 12 ? "PM" : "AM";
  const adjustedHours = hours % 12 || 12; // Convert 0 hour to 12 for 12-hour format

  return `${adjustedHours}:${minutes.toString().padStart(2, '0')} ${suffix}`;
}

const loading = ref(false)
// Watcher for the inputString's length
watch(rfidNumber, async (newVal: string) => {
  if (newVal.length == 10) { // Trigger fetch after a certain length (e.g., 10)
    loading.value = true
    const face_data = await snapshot()
    const time_in = await $fetch<TimeInOutResponse>(`/api/attendance/${time_in_out.value}`, {
        method: 'POST',
        body: {
          student_id: +rfidNumber.value,
          subject_id: chosenSub.value,
          face_data: face_data,
        }
      }
    )
    if(time_in){
        loading.value = false
        toast.add({
          id: 'time-in',
          title: time_in.success 
              ? (time_in.time_out 
                ? `Time-out recorded @: ${to12HourFormat(time_in.time_out)}` 
                : `Hi, ${time_in.student_name}. Your time-in recorded @: ${to12HourFormat(time_in.time_in)}`) 
              : time_in.message ,
          color: time_in.success ? 'green': 'red',
          icon: time_in.success ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle',
          timeout: 1500,
        })
        rfidNumber.value = ''
        rfidRef.value.$refs.input.focus()

        // openModal(time_in)
        // // 2 second countdown
        // setTimeout(() => {
        //     closeModal()
        // }, 2000);
        // setTimeout(() => {
        //     rfidRef.value.$refs.input.focus()
        // }, 2300)
    }
  }
});


// import { Welcome } from '#components'

// const modal = useModal()
const rfidRef = ref()
const toast = useToast()

// function openModal(props: TimeInOutResponse) {

//   modal.open(Welcome, {
//     time_in: props.time_in,
//     success: props.success,
//     message: props.message,
//     time_out: props.time_out,
//     is_present: props.is_present,
//     student_name: props.student_name,
//   });
// }

// function closeModal () {
//   rfidNumber.value = ''
//   modal.close()
// }

</script> 
<template>
  <UContainer class="min-h-screen py-8">
    <div class="max-w-6xl mx-auto space-y-8">
      <UCard>
        <div class="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0 sm:space-x-4">
          <h1 class="text-2xl font-bold text-gray-800 dark:text-white">UP Tap Attendance System</h1>
          <div class="w-full sm:w-64">
            <USelect
              v-if="subjects"
              v-model="chosenSub"
              size="lg"
              placeholder="Select Subject"
              :options="subjects"
              color="primary"
              variant="outline"
              value-attribute="subject_id"
              option-attribute="subject_name"
            />
          </div>
        </div>
        <UTabs :items="items" class="mt-6" @change="onChangeTab">
          <template #default="{ item, index, selected }">
            <span class="truncate font-medium" :class="[selected ? 'text-primary-600 dark:text-primary-400' : 'text-gray-600 dark:text-gray-400']">
              {{ item.label }}
            </span>
          </template>
          <template #icon="{ item, selected }">
            <UIcon
              :name="item.icon"
              class="w-5 h-5 mr-2"
              :class="[selected ? 'text-primary-600 dark:text-primary-400' : 'text-gray-600 dark:text-gray-400']"
            />
          </template>
        </UTabs>
      </UCard>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <UCard>
          <h2 class="text-xl font-semibold text-gray-800 dark:text-white mb-4">Step 1: Face Recognition</h2>
          <div class="bg-gray-200 dark:bg-gray-700 rounded-lg overflow-hidden">
            <Camera :resolution="{ width: 500, height: 500 }" ref="camera" autoplay class="w-full h-auto" />
          </div>
          <p class="text-center text-gray-600 dark:text-gray-400 mt-4">
            Align your face with the camera, please.
          </p>
        </UCard>

        <UCard>
          <h2 class="text-xl font-semibold text-gray-800 dark:text-white mb-4">Step 2: RFID Scan</h2>
          <div class="flex flex-col items-center justify-center space-y-6">
            <NuxtImg src="/images/RFID.png" class="w-[500px] h-[500px] object-contain" />
            <div class="w-full max-w-xs">
              <UInput
                :loading="loading"
                v-model="rfidNumber"
                color="primary"
                variant="outline"
                autofocus
                ref="rfidRef"
                placeholder="Scan your RFID card..."
                class="w-full"
              />
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </UContainer>
</template>