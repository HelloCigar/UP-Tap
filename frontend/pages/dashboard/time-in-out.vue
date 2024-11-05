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
const chosenSub = ref<number>(1)

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

// Watcher for the inputString's length
watch(rfidNumber, async (newVal: string) => {
  if (newVal.length == 10) { // Trigger fetch after a certain length (e.g., 10)
    const face_data = await snapshot()
    console.log(face_data)
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
        openModal(time_in)
        // 2 second countdown
        setTimeout(() => {
            closeModal()
        }, 2000);
        setTimeout(() => {
            rfidRef.value.$refs.input.focus()
        }, 2300)
    }
  }
});


import { Welcome } from '#components'

const modal = useModal()
const rfidRef = ref()


function openModal(props: TimeInOutResponse) {

  modal.open(Welcome, {
    time_in: props.time_in,
    success: props.success,
    message: props.message,
    time_out: props.time_out,
    is_present: props.is_present,
    student_name: props.student_name,
  });
}

function closeModal () {
  rfidNumber.value = ''
  modal.close()
}

</script> 
<template>
    <UContainer class="min-h-full"> 
            <div class="flex flex-row gap-4 items-start p-4"> 
                <div class="h-full w-48">
                    <USelect v-if="subjects" v-model="chosenSub" size="lg" placeholder="Subject" :options="subjects" color="white" variant="outline" value-attribute="subject_id" option-attribute="subject_name"/>
                </div>             
                <div class="w-full">
                    <UTabs :items="items" class="w-full" @change="onChangeTab">
                      <template #default="{ item, index, selected }">
                        <span class="truncate" :class="[selected && 'text-primary-500 dark:text-primary-400']">{{ index + 1 }}. {{ item.label }}</span>
                      </template>
                      <template #icon="{ item, selected }">
                        <UIcon :name="item.icon" class="w-4 h-4 flex-shrink-0 me-2" :class="[selected && 'text-primary-500 dark:text-primary-400']" />
                      </template>
                    </UTabs>
                </div>             
            </div>         
            <div class="flex flex-row">
                <div class="basis-1/2 p-4">
                    <h1 class="text-primary-500 dark:text-primary-400 text-2xl text-start font-mono">Step 1. Face Recognition</h1> 
                    <div class="h-[500px] my-4">
                        <Camera :resolution="{ width: 500, height: 500 }" ref="camera" autoplay></Camera>
                    </div>
                    <h1 class="text-primary-500 dark:text-primary-400 text-2xl text-center font-mono mt-16">Align your face with the camera please</h1>             
                </div>
                <UDivider label="Then" orientation="vertical" />
                <div class="basis-1/2 p-4 gap-2">
                    <h1 class="text-primary-500 dark:text-primary-400 text-2xl text-start font-mono">Step 2. RFID Scan</h1>
                    <div class="flex flex-row h-[500px] w-full justify-center my-4">
                        <NuxtImg src="/images/RFID.png" height="500"/>
                    </div> 
                    <div class="flex flex-row w-full justify-center my-4">
                        <div class="w-36">
                            <UInput color="white" v-model="rfidNumber" variant="outline" autofocus ref="rfidRef" placeholder="Your RFID number..." /> 
                        </div>
                    </div>
                </div>
            </div>
    </UContainer>
</template>