<script setup lang="ts">
import Camera from 'simple-vue-camera';
const resultRef = ref();
const photoTaken = ref()
const img = ref()

  // Get a reference of the component
  const camera = ref<InstanceType<typeof Camera>>();

  // Use camera reference to call functions
  const snapshot = async () => {
  const blob = await camera.value?.snapshot({ width: 500, height: 500 });

  if (blob) {
    // Convert blob to Base64
    const reader = new FileReader();

    reader.onloadend = async () => {
      const base64String = reader.result;
      resultRef.value = await $fetch("/api/verify", {
        method: "POST",
        body: {
          img64_str : base64String
        }
      }
    )
    };
    reader.readAsDataURL(blob);  // Read the blob as a data URL (Base64 string)    
  }
}

const takephoto = async () => {
    const blob = await camera.value?.snapshot({ width: 500, height: 500 });

    // Convert the blob to a JPEG if necessary
    const imageBitmap = await createImageBitmap(blob);
    const canvas = document.createElement('canvas');
    canvas.width = imageBitmap.width;
    canvas.height = imageBitmap.height;

    const ctx = canvas.getContext('2d');
    ctx?.drawImage(imageBitmap, 0, 0);

    // Convert canvas to JPEG format and get the Blob
    const jpegBlob = await new Promise<Blob | null>((resolve) =>
        canvas.toBlob((blob) => resolve(blob), 'image/jpeg')
    );

    if (jpegBlob) {
        photoTaken.value = URL.createObjectURL(jpegBlob);
        img.value = blob
    }
}

const retake =  () => {
    photoTaken.value = null
}

import { object, string, type InferType } from 'yup'
import type { FormSubmitEvent } from '#ui/types'


const schema = object({
  name: string().required('Required'),
})

type Schema = InferType<typeof schema>

const state = reactive({
  name: undefined,
})

async function onSubmit (event: FormSubmitEvent<Schema>) {
  // Do something with event.data

  const reader = new FileReader();
    
  let upload;
  reader.onloadend = async () => {
  const base64String = reader.result;
  
  try {
    upload = await $fetch("/api/upload", {
      method: "POST",
      body: {
        name: event.data.name,
        img64_str: base64String
      }
    });
    
        if (upload) {
          resultRef.value = upload;
        }
      } catch (error) {
        console.error("Upload failed:", error);
      }
    }
    reader.readAsDataURL(img.value);  // Read the blob as a data URL (Base64 string)   
    if(upload){
      resultRef.value = upload
    } 
  }


</script>
<template>
    <div>
        <div v-if="photoTaken" class="flex flex-col justify-center gap-y-12">
            <div class="flex justify-center h-[500px]" >
                <img :src="photoTaken" />
            </div>
            <div class="flex justify-center">
                <UForm :schema="schema" :state="state" class="space-y-4" @submit="onSubmit">
                <UFormGroup label="Email" name="email">
                <UInput v-model="state.name" />
                </UFormGroup>
                <div class="flex justify-center">
                    <UButton type="submit" size="sm" color="primary" variant="outline">Register face</UButton>
                </div>
            </UForm>
            </div>
            <div class="flex justify-center">
                <UButton size="sm" @click="retake" color="primary" variant="outline">Retake</UButton>
            </div>
            <div class="flex justify-center" v-if="resultRef">
                <UAlert
                    :description="resultRef"
                    title="Result"
                />
            </div>
        </div>
        <div v-else class="flex flex-col justify-center gap-y-12">
            <div class="h-[500px]">
                <Camera :resolution="{ width: 500, height: 500 }" ref="camera" autoplay></Camera>
            </div>
            <div class="flex justify-center">
                <UButton size="sm" @click="takephoto" color="primary" variant="outline">Take photo</UButton>
            </div>
        </div>
    </div>   
</template>