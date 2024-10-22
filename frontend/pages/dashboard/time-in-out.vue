<script setup lang="ts">
definePageMeta({
    layout: 'dashboard'
})
import Camera from 'simple-vue-camera';
// Get a reference of the component
const camera = ref<InstanceType<typeof Camera>>();
    
const countries = ['United States', 'Canada', 'Mexico']

const items = [{
  key: 'time-in',
  label: 'Time in',
  icon: 'i-heroicons-arrow-left-on-rectangle',
}, {
  key: 'time-out',
  label: 'Time out',
  icon: 'i-heroicons-arrow-left-start-on-rectangle',
}]

function onChange (index: number) {
  const item = items[index]

}

const rfidNumber = ref(""); // Holds the string input

// Watcher for the inputString's length
watch(rfidNumber, async (newVal: string) => {
  if (newVal.length == 10) { // Trigger fetch after a certain length (e.g., 10)
    const result = sendTimeIn(newVal);
    if(result){
        openModal()
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

const sendTimeIn = (query: string) => {
//   try {
//     const response = await $fetch(`https://example.com/api?search=${query}`);
//     console.log("Fetched data:", response);
//   } catch (error) {
//     console.error("Fetch error:", error);
//   }
    return {"result": "success"}
};


import { Welcome } from '#components'

const toast = useToast()
const modal = useModal()
const count = ref(0)
const rfidRef = ref()


function openModal () {
  count.value += 1
  modal.open(Welcome, {
    count: count.value,
    onSuccess () {
      toast.add({
        title: 'Success !',
        id: 'modal-success'
      })
    }
  })
}

function closeModal () {
  rfidNumber.value = ''
  modal.close()
}

</script> 
<template>
    <div class="bg-gray-100 flex h-16 items-center px-4 dark:bg-gray-900">
        <h3>Student</h3>
    </div>
    <UDivider></UDivider>    
    <UContainer class="min-h-full"> 
            <div class="flex flex-row gap-4 items-start p-4"> 
                <div class="h-full">
                    <USelect size="lg" placeholder="Section" :options="countries" color="white" variant="outline"/>
                </div>             
                <div class="w-full">
                    <UTabs :items="items" class="w-full" @change="onChange"></UTabs>
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
                    <h1 class="text-primary-500 dark:text-primary-400 text-2xl text-center font-mono">...and tap your RFID to the scanner</h1>
                </div>
            </div>
    </UContainer>
</template>