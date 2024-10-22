<script setup lang="ts">
const session = useUserSession()
import Camera from 'simple-vue-camera';
const resultRef = ref();

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
};
</script> 
<template> 
    <div v-if="session.loggedIn" class="flex flex-col justify-center gap-y-12"> 
        <div class="h-[500px]"> 
            <Camera :resolution="{ width: 200, height: 200 }" ref="camera" autoplay></Camera>             
        </div>         
        <div class="flex justify-center"> 
            <UButton size="sm" @click="snapshot" color="primary" variant="outline">Trigger face recognition</UButton>             
        </div>         
        <div class="flex justify-center" v-if="resultRef"> 
            <UAlert :description="resultRef" title="Result"/> 
        </div>         
    </div>     
</template>